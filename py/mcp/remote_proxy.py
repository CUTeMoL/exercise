#!/usr/bin/env python3
"""
MCP 远程代理：将本地 stdio 协议的 MCP 请求签名后转发到远程 HTTPS 服务器。

用于 Claude Code / VS Code / Cursor 等 MCP 客户端连接远程 MCP 服务器。

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
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
import time

# MCP SDK 导入（客户端连接远端 + 服务端暴露给本地）
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server


# ── AK/SK 签名（与服务器端 auth.py 的 compute_signature 一致）────────

def sign(method: str, path: str, body: bytes, ak: str, sk: str) -> dict:
    """为请求计算 HMAC 签名，返回带认证头的字典。"""
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


# ── 主逻辑 ───────────────────────────────────────────────────────────

async def run():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="MCP 远程代理")
    parser.add_argument("--host", default="localhost", help="远程服务器地址")
    parser.add_argument("--port", type=int, default=8443, help="远程服务器端口")
    parser.add_argument("--ak", required=True, help="Access Key")
    parser.add_argument("--sk", required=True, help="Secret Key")
    parser.add_argument("--ca-cert", default="", help="CA 证书路径（为空则跳过验证）")
    args = parser.parse_args()

    server_url = f"https://{args.host}:{args.port}/mcp"

    # SSL 验证配置
    if args.ca_cert and os.path.exists(args.ca_cert):
        verify = args.ca_cert
    else:
        verify = False
        if args.ca_cert:
            print(f"[WARN] CA 证书未找到: {args.ca_cert}，将跳过 SSL 验证", file=sys.stderr)

    # ── 远端工具缓存 ─────────────────────────────────────────────
    remote_tools: list = []
    session_id: str = ""

    # ── 创建本地 MCP 服务端 ───────────────────────────────────────
    local_server = Server("remote-monitor-proxy")

    # ── 建立与远端的连接 ─────────────────────────────────────────
    async def connect_remote():
        nonlocal remote_tools, session_id

        # 自定义传输层：在 HTTP 请求中注入 AK/SK 认证头
        class AuthHeadersFactory:
            """在每次 HTTP 请求中注入 AK/SK 签名头。"""
            def __init__(self, ak, sk):
                self._ak = ak
                self._sk = sk

            async def __call__(self, method: str, url: str, headers: dict, body: bytes):
                auth_headers = sign(method, url, body, self._ak, self._sk)
                headers.update(auth_headers)

        auth_factory = AuthHeadersFactory(args.ak, args.sk)

        async with streamablehttp_client(
            server_url,
            verify=verify,
            headers_factory=auth_factory,
        ) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                # 初始化 MCP 会话
                init_result = await session.initialize()
                server_info = init_result.server_info
                print(f"[INFO] 已连接到 {server_info.name} v{server_info.version}",
                      file=sys.stderr)

                sid = get_session_id()
                print(f"[INFO] 会话 ID: {sid}", file=sys.stderr)

                # 拉取远端工具列表
                tools_result = await session.list_tools()
                remote_tools.clear()
                for tool in tools_result.tools:
                    remote_tools.append({
                        "name": tool.name,
                        "description": tool.description or "",
                        "inputSchema": tool.inputSchema,
                    })

                # 注册为本地工具
                await update_local_tools()

                print(f"[INFO] 已同步 {len(remote_tools)} 个远端工具", file=sys.stderr)

    async def update_local_tools():
        """将远端工具同步到本地 MCP 服务端。"""
        # 直接更新本地 server 的工具列表
        tools_for_local = []
        for t in remote_tools:
            # 用 mcp.types.Tool 创建工具定义
            from mcp.types import Tool
            tools_for_local.append(Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"],
            ))
        # 通过 list_tools handler 返回
        pass  # 在 handler 中返回

    # ── 本地 MCP 处理器 ─────────────────────────────────────────

    @local_server.list_tools()
    async def handle_list_tools():
        """返回从远端同步到的工具列表。"""
        from mcp.types import Tool
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"],
            )
            for t in remote_tools
        ]

    @local_server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        """将本地工具调用转发到远端服务器。"""
        async with streamablehttp_client(
            server_url,
            verify=verify,
            headers_factory=AuthFactoryInternal(args.ak, args.sk),
        ) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
                return result.content

    # ── 启动 ─────────────────────────────────────────────────────
    # 先连接远端获取工具列表
    await connect_remote()

    # 启动本地 stdio 服务，等待 Claude Code 连接
    async with stdio_server() as (read_stream, write_stream):
        await local_server.run(
            read_stream,
            write_stream,
            InitializationCapabilities(
                sampling={},
                experimental={},
                roots={},
            ),
            notification_options=NotificationOptions(
                tools_changed=False,
                prompts_changed=False,
                resources_changed=False,
            ),
        )


# 单独定义一个 AuthHeadersFactory 类供 call_tool 使用
class AuthFactoryInternal:
    def __init__(self, ak, sk):
        self._ak = ak
        self._sk = sk

    async def __call__(self, method: str, url: str, headers: dict, body: bytes):
        auth_headers = sign(method, url, body, self._ak, self._sk)
        headers.update(auth_headers)


def main():
    import asyncio
    asyncio.run(run())


if __name__ == "__main__":
    main()
