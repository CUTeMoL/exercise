#!/usr/bin/env python3
"""
MCP 远程代理：将本地 stdio 协议转发到远程 HTTPS MCP 服务器。

用于 Claude Code / VS Code / Cursor 等 MCP 客户端连接远程服务器。
运行在 Windows 客户端上，通过 AK/SK 签名认证连接远程 Linux 服务器。

用法（在 Claude Code 的 mcp.json 中配置）:
{
  "mcpServers": {
    "remote-monitor": {
      "command": "python",
      "args": [
        "C:/path/to/remote_proxy.py",
        "--host", "172.26.72.248",
        "--port", "8443",
        "--ak", "ak-xxxxxxxx",
        "--sk", "sk-xxxxxxxx",
        "--ca-cert", "C:/path/to/ca.crt"
      ]
    }
  }
}

Windows 客户端依赖: pip install mcp httpx
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
from itertools import count

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ServerCapabilities, Tool, ToolsCapability


# ── AK/SK 签名（与服务器端 auth.py 的 compute_signature 一致）────────

def sign(method: str, path: str, body: bytes, ak: str, sk: str) -> dict:
    """为请求构建 AK/SK HMAC-SHA256 认证头。"""
    ts = str(int(time.time()))
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"{method}\n{path}\n{ts}\n{body_hash}"
    signature = hmac.new(sk.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    return {
        "X-AK": ak,
        "X-Timestamp": ts,
        "X-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }


# ── 远程 MCP 客户端（持久连接）─────────────────────────────────────

class RemoteMcpClient:
    """使用 httpx 异步客户端与远程 MCP 服务器通信，保持持久连接池。"""

    def __init__(self, base_url: str, ak: str, sk: str, verify: str | bool = False):
        self.base_url = base_url
        self.ak = ak
        self.sk = sk
        self.session_id: str | None = None
        self._msg_id = count(1)
        self._client = httpx.AsyncClient(
            verify=verify,
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def close(self):
        await self._client.aclose()

    # ── 底层 HTTP 请求 ──────────────────────────────────────────

    async def _request(self, method: str, path: str, body: dict | None,
                       expect_response: bool = True) -> dict:
        """发送签名后的 MCP JSON-RPC 请求，返回解析结果。"""
        body_bytes = json.dumps(body).encode() if body else b"{}"
        headers = sign(method, path, body_bytes, self.ak, self.sk)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        resp = await self._client.request(
            method, f"{self.base_url}{path}",
            content=body_bytes, headers=headers,
        )

        # 提取 Session ID
        sid = resp.headers.get("mcp-session-id")
        if sid:
            self.session_id = sid

        if not expect_response:
            return {}

        content_type = resp.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            messages = self._parse_sse(resp.text)
            return messages[0] if messages else {}
        return resp.json()

    @staticmethod
    def _parse_sse(raw: str) -> list[dict]:
        """解析 SSE (Server-Sent Events) 响应中的 JSON 消息。"""
        messages = []
        for line in raw.split("\n"):
            if line.startswith("data:"):
                try:
                    messages.append(json.loads(line[5:].strip()))
                except json.JSONDecodeError:
                    continue
        return messages

    # ── MCP 协议操作 ────────────────────────────────────────────

    async def initialize(self) -> dict:
        """初始化 MCP 会话并发送 initialized 通知。"""
        result = await self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-remote-proxy", "version": "1.0.0"},
            },
            "id": next(self._msg_id),
        })

        # MCP 协议要求: initialize 响应后必须发送 notifications/initialized
        await self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }, expect_response=False)

        server_info = result.get("result", {}).get("serverInfo", {})
        print(f"[INFO] 已连接到 {server_info.get('name', '未知')} "
              f"v{server_info.get('version', '?')}，会话: {self.session_id}",
              file=sys.stderr)
        return result

    async def list_tools(self) -> list[dict]:
        """获取远程服务器的工具列表。"""
        result = await self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": next(self._msg_id),
        })
        return result.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: dict) -> list[dict]:
        """调用远程工具并返回 content 列表。"""
        result = await self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
            "id": next(self._msg_id),
        })
        return result.get("result", {}).get("content", [])


# ── 主逻辑 ───────────────────────────────────────────────────────

async def run():
    parser = argparse.ArgumentParser(description="MCP 远程代理")
    parser.add_argument("--host", default="localhost", help="远程服务器地址")
    parser.add_argument("--port", type=int, default=8443, help="远程服务器端口")
    parser.add_argument("--ak", required=True, help="Access Key")
    parser.add_argument("--sk", required=True, help="Secret Key")
    parser.add_argument("--ca-cert", default="", help="CA 证书路径（为空则跳过验证）")
    args = parser.parse_args()

    server_url = f"https://{args.host}:{args.port}"

    # SSL 验证配置
    verify: str | bool = False
    if args.ca_cert:
        if os.path.exists(args.ca_cert):
            verify = args.ca_cert
        else:
            print(f"[WARN] CA 证书未找到: {args.ca_cert}，将跳过 SSL 验证", file=sys.stderr)

    # 建立持久远程连接
    remote = RemoteMcpClient(server_url, args.ak, args.sk, verify)

    try:
        # 初始化 MCP 会话并拉取工具列表
        await remote.initialize()
        remote_tools = await remote.list_tools()
        print(f"[INFO] 发现 {len(remote_tools)} 个远端工具", file=sys.stderr)
        for t in remote_tools:
            print(f"[INFO]   - {t['name']}: {t.get('description', '')}", file=sys.stderr)

        # 创建本地 MCP 服务端（stdio）
        local_server = Server("remote-monitor-proxy")

        @local_server.list_tools()
        async def handle_list_tools():
            return [
                Tool(
                    name=t["name"],
                    description=t.get("description", ""),
                    inputSchema=t.get("inputSchema", {"type": "object", "properties": {}}),
                )
                for t in remote_tools
            ]

        @local_server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            print(f"[INFO] 转发工具调用: {name}({json.dumps(arguments)})", file=sys.stderr)
            try:
                return await remote.call_tool(name, arguments)
            except Exception as e:
                print(f"[WARN] 远端调用失败，尝试重连: {e}", file=sys.stderr)
                try:
                    await remote.initialize()
                    return await remote.call_tool(name, arguments)
                except Exception as e2:
                    return [{"type": "text", "text": f"远程调用失败: {e2}"}]

        # 启动本地 stdio 服务
        async with stdio_server() as (read_stream, write_stream):
            await local_server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="remote-monitor-proxy",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(tools=ToolsCapability()),
                ),
            )

    finally:
        await remote.close()


def main():
    import asyncio
    asyncio.run(run())


if __name__ == "__main__":
    main()
