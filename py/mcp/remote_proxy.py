#!/usr/bin/env python3
"""
MCP 远程代理（零依赖版）：本地 stdio ↔ 远程 HTTPS MCP 服务器。

纯 Python 标准库实现，无需 pip install。
Windows 客户端只需安装 Python 3.10+ 即可使用。

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
import ssl
import sys
import time
import urllib.request


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


# ── 远程 HTTP 请求（urllib，无第三方依赖）───────────────────────────

def create_ssl_context(ca_cert_path: str | None) -> ssl.SSLContext:
    """创建 SSL 上下文。ca_cert_path 为 None 时跳过证书验证。"""
    if ca_cert_path:
        return ssl.create_default_context(cafile=ca_cert_path)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def parse_sse(raw: str) -> dict | None:
    """解析 SSE (Server-Sent Events) 响应的第一个 JSON 消息。"""
    for line in raw.split("\n"):
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue
    return None


def remote_request(base_url: str, body: dict, ak: str, sk: str,
                   session_id: str | None, ssl_ctx: ssl.SSLContext,
                   expect_response: bool = True) -> tuple[dict | None, str | None]:
    """发送签名后的 MCP JSON-RPC 请求到远程服务器。

    返回 (响应体, 新的 session_id)。
    """
    body_bytes = json.dumps(body).encode()
    headers = sign("POST", "/mcp", body_bytes, ak, sk)
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = urllib.request.Request(
        f"{base_url}/mcp",
        data=body_bytes,
        headers=headers,
        method="POST",
    )

    resp = urllib.request.urlopen(req, context=ssl_ctx)
    new_session_id = resp.headers.get("Mcp-Session-Id")

    if not expect_response:
        resp.read()  # 消费响应体
        return None, new_session_id

    raw = resp.read().decode()
    content_type = resp.headers.get("Content-Type", "")

    if "text/event-stream" in content_type:
        return parse_sse(raw), new_session_id
    return json.loads(raw), new_session_id


def mcp_initialize(base_url: str, ak: str, sk: str,
                   ssl_ctx: ssl.SSLContext) -> tuple[str, dict]:
    """初始化 MCP 会话。返回 (session_id, server_info)。"""
    msg_id = 1

    # 1. 发送 initialize 请求
    result, sid = remote_request(base_url, {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-remote-proxy", "version": "1.0.0"},
        },
        "id": msg_id,
    }, ak, sk, None, ssl_ctx)

    session_id = sid or ""
    server_info = result.get("result", {}).get("serverInfo", {}) if result else {}

    # 2. 发送 initialized 通知（MCP 协议要求）
    remote_request(base_url, {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {},
    }, ak, sk, session_id, ssl_ctx, expect_response=False)

    return session_id, server_info


def mcp_list_tools(base_url: str, ak: str, sk: str,
                   session_id: str, ssl_ctx: ssl.SSLContext) -> list[dict]:
    """获取远程工具列表。"""
    result, _ = remote_request(base_url, {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2,
    }, ak, sk, session_id, ssl_ctx)
    return result.get("result", {}).get("tools", []) if result else []


def mcp_call_tool(base_url: str, ak: str, sk: str, session_id: str,
                  tool_name: str, arguments: dict,
                  ssl_ctx: ssl.SSLContext) -> list[dict]:
    """调用远程工具。"""
    result, _ = remote_request(base_url, {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
        "id": 3,
    }, ak, sk, session_id, ssl_ctx)
    return result.get("result", {}).get("content", []) if result else []


# ── 本地 stdio MCP 服务（纯标准库，无第三方依赖）────────────────────

def stdio_loop(base_url: str, ak: str, sk: str, ca_cert: str | None):
    """主循环：从 stdin 读取 JSON-RPC，处理后写入 stdout。"""
    ssl_ctx = create_ssl_context(ca_cert)

    # 连接远程服务器
    session_id, server_info = mcp_initialize(base_url, ak, sk, ssl_ctx)
    print(f"[INFO] 已连接到 {server_info.get('name', '未知')} "
          f"v{server_info.get('version', '?')}，会话: {session_id[:16]}...",
          file=sys.stderr)

    # 拉取远端工具列表
    remote_tools = mcp_list_tools(base_url, ak, sk, session_id, ssl_ctx)
    if not remote_tools:
        print("[WARN] 未获取到远端工具，尝试重连", file=sys.stderr)
        try:
            session_id, _ = mcp_initialize(base_url, ak, sk, ssl_ctx)
            remote_tools = mcp_list_tools(base_url, ak, sk, session_id, ssl_ctx)
        except Exception as e:
            print(f"[ERROR] 重连后仍无法获取工具列表: {e}", file=sys.stderr)
    print(f"[INFO] 发现 {len(remote_tools)} 个远端工具", file=sys.stderr)
    for t in remote_tools:
        print(f"[INFO]   - {t['name']}", file=sys.stderr)

    # ── 处理 stdio JSON-RPC 请求 ─────────────────────────────────

    def build_tools_list():
        return [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "inputSchema": t.get("inputSchema", {"type": "object", "properties": {}}),
            }
            for t in remote_tools
        ]

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            # 返回本地代理的能力声明
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "remote-monitor-proxy",
                        "version": "1.0.0",
                    },
                },
            }
            write_response(resp)

        elif method == "notifications/initialized":
            pass  # 通知无需响应

        elif method == "tools/list":
            # 重新拉取远端工具列表（含会话恢复）
            try:
                remote_tools = mcp_list_tools(base_url, ak, sk, session_id, ssl_ctx)
                if not remote_tools:
                    raise RuntimeError("empty tool list")
            except Exception as e:
                print(f"[WARN] 获取工具列表失败，尝试重连: {e}", file=sys.stderr)
                try:
                    session_id, _ = mcp_initialize(base_url, ak, sk, ssl_ctx)
                    remote_tools = mcp_list_tools(base_url, ak, sk, session_id, ssl_ctx)
                except Exception as e2:
                    print(f"[ERROR] 重连后仍无法获取工具列表: {e2}", file=sys.stderr)
                    remote_tools = []
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": build_tools_list()},
            }
            write_response(resp)

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            print(f"[INFO] 转发工具调用: {tool_name}({json.dumps(arguments)})",
                  file=sys.stderr)

            try:
                content = mcp_call_tool(
                    base_url, ak, sk, session_id,
                    tool_name, arguments, ssl_ctx,
                )
            except Exception as e:
                print(f"[WARN] 远端调用失败，尝试重连: {e}", file=sys.stderr)
                try:
                    session_id, _ = mcp_initialize(base_url, ak, sk, ssl_ctx)
                    content = mcp_call_tool(
                        base_url, ak, sk, session_id,
                        tool_name, arguments, ssl_ctx,
                    )
                except Exception as e2:
                    content = [{"type": "text",
                                "text": f"远程调用失败: {e2}"}]

            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": content},
            }
            write_response(resp)

        elif method == "notifications/cancelled":
            pass  # 忽略取消通知

        else:
            # 未知方法
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }
            write_response(resp)


def write_response(resp: dict):
    """将 JSON-RPC 响应写入 stdout。"""
    sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
    sys.stdout.flush()


# ── 入口 ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MCP 远程代理（零依赖版）")
    parser.add_argument("--host", default="localhost", help="远程服务器地址")
    parser.add_argument("--port", type=int, default=8443, help="远程服务器端口")
    parser.add_argument("--ak", required=True, help="Access Key")
    parser.add_argument("--sk", required=True, help="Secret Key")
    parser.add_argument("--ca-cert", default="", help="CA 证书路径（为空则跳过验证）")
    args = parser.parse_args()

    base_url = f"https://{args.host}:{args.port}"

    ca_cert = args.ca_cert if args.ca_cert and os.path.exists(args.ca_cert) else None
    if args.ca_cert and not ca_cert:
        print(f"[WARN] CA 证书未找到: {args.ca_cert}，将跳过 SSL 验证", file=sys.stderr)

    stdio_loop(base_url, args.ak, args.sk, ca_cert)


if __name__ == "__main__":
    main()
