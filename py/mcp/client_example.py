#!/usr/bin/env python3
"""
MCP 客户端示例：AK/SK HMAC 签名 + CA 证书验证。

特性:
- 使用 httpx 实现连接池、keep-alive、超时控制
- SSL/TLS 证书链验证（信任 CA 证书，无需跳过验证）
- 自动处理 SSE (Server-Sent Events) 响应
- 上下文管理器，自动释放连接

用法:
    python client_example.py --ak <access_key> --sk <secret_key> [--host 服务器IP] [--port 8443] [--no-ssl]
"""
import argparse
import hashlib
import hmac
import json
import os
import ssl
import time
from pathlib import Path

import httpx


# 项目根目录，用于定位 CA 证书
PROJECT_ROOT = Path(__file__).parent
DEFAULT_CA_CERT = str(PROJECT_ROOT / "certs" / "ca.crt")


def sign_request(ak: str, sk: str, method: str, path: str, body: bytes) -> dict:
    """为请求构建 AK/SK 认证头。

    签名算法:
        规范字符串 = HTTP方法 + 换行 + URL路径 + 换行 + 时间戳 + 换行 + SHA256(请求体)
        签名 = hex(HMAC-SHA256(SK, 规范字符串))
    """
    timestamp = str(int(time.time()))
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"{method}\n{path}\n{timestamp}\n{body_hash}"
    signature = hmac.new(sk.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    return {
        "X-AK": ak,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }


def create_ssl_context(ca_cert_file: str) -> ssl.SSLContext:
    """创建带 CA 验证的 SSL 上下文。"""
    ctx = ssl.create_default_context(cafile=ca_cert_file)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


def parse_sse_body(raw: str) -> list[dict]:
    """解析 SSE (Server-Sent Events) 响应体，提取 JSON 消息。"""
    messages = []
    for line in raw.split("\n"):
        if line.startswith("data:"):
            try:
                messages.append(json.loads(line[5:].strip()))
            except json.JSONDecodeError:
                continue
    return messages


class McpClient:
    """MCP Streamable HTTP 客户端，支持 AK/SK 认证和 CA 证书验证。"""

    def __init__(self, host: str, port: int, ak: str, sk: str,
                 use_ssl: bool = True, ca_cert_file: str = DEFAULT_CA_CERT,
                 timeout: float = 30.0):
        scheme = "https" if use_ssl else "http"
        self.base_url = f"{scheme}://{host}:{port}"
        self.ak = ak
        self.sk = sk
        self.session_id = None

        # 构建 httpx 客户端（连接池 + CA 验证）
        client_kwargs = {
            "timeout": httpx.Timeout(timeout),
            "limits": httpx.Limits(max_keepalive_connections=5, max_connections=10),
        }
        if use_ssl:
            if not os.path.exists(ca_cert_file):
                raise FileNotFoundError(
                    f"CA 证书未找到: {ca_cert_file}\n"
                    f"请先生成证书，参考 README.md 中的步骤。"
                )
            client_kwargs["verify"] = ca_cert_file

        self._client = httpx.Client(**client_kwargs)

    def close(self):
        """关闭底层连接池。"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _request(self, method: str, path: str, body: dict) -> dict:
        """发送签名的 MCP 请求，返回解析后的 JSON-RPC 结果。"""
        body_bytes = json.dumps(body).encode()
        headers = sign_request(self.ak, self.sk, method, path, body_bytes)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        resp = self._client.request(
            method, f"{self.base_url}{path}",
            content=body_bytes, headers=headers,
        )

        # 从响应头提取 Session ID
        sid = resp.headers.get("mcp-session-id")
        if sid:
            self.session_id = sid

        content_type = resp.headers.get("content-type", "")

        if "text/event-stream" in content_type:
            # SSE 响应: 解析 data 字段
            messages = parse_sse_body(resp.text)
            return messages[0] if messages else {}
        else:
            return resp.json()

    def initialize(self) -> dict:
        """初始化 MCP 会话，获取 Session ID。"""
        return self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "aksk-client", "version": "1.0.0"},
            },
            "id": 1,
        })

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """调用 MCP 工具。"""
        return self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
            "id": 2,
        })


def print_mcp_result(result: dict, tool_name: str):
    """格式化打印 MCP 工具返回结果。"""
    try:
        content = result["result"]["content"]
        if isinstance(content, list) and len(content) > 0:
            item = content[0]
            if isinstance(item, dict) and "text" in item:
                data = json.loads(item["text"])
            elif isinstance(item, dict) and "data" in item:
                data = item["data"]
            else:
                data = content
        else:
            data = content

        if not data:
            print("  (无结果)")
            return

        if tool_name == "get_top_memory_processes":
            print(f"{'PID':>8}  {'进程名':<25} {'内存 (B)':>15}")
            print("-" * 52)
            for p in data:
                print(f"{p['pid']:>8}  {p['name']:<25} {p['memory_bytes']:>15,}")
        elif tool_name == "get_top_cpu_processes":
            print(f"{'PID':>8}  {'进程名':<25} {'CPU (%)':>10}")
            print("-" * 47)
            for p in data:
                print(f"{p['pid']:>8}  {p['name']:<25} {p['cpu_percent']:>10.1f}")
        else:
            print(json.dumps(data, indent=2))
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        print(f"解析结果出错: {e}")
        print(f"原始响应: {json.dumps(result, indent=2)}")


def main():
    parser = argparse.ArgumentParser(description="MCP AK/SK 客户端示例")
    parser.add_argument("--host", default="localhost", help="服务器地址")
    parser.add_argument("--port", type=int, default=8443, help="服务器端口")
    parser.add_argument("--ak", required=True, help="Access Key")
    parser.add_argument("--sk", required=True, help="Secret Key")
    parser.add_argument("--no-ssl", action="store_true", help="使用 HTTP 而非 HTTPS")
    parser.add_argument("--ca-cert", default=DEFAULT_CA_CERT,
                        help=f"CA 证书路径 (默认: {DEFAULT_CA_CERT})")
    args = parser.parse_args()

    use_ssl = not args.no_ssl
    ca_cert = args.ca_cert

    # 第一步: 健康检查（无需认证）
    print("=== 健康检查 ===")
    scheme = "https" if use_ssl else "http"
    url = f"{scheme}://{args.host}:{args.port}/health"
    with httpx.Client(verify=ca_cert if use_ssl else False, timeout=10) as hc:
        resp = hc.get(url)
        print(f"  {resp.text}")

    # 第二步: 初始化 MCP 会话并调用工具
    with McpClient(args.host, args.port, args.ak, args.sk,
                   use_ssl=use_ssl, ca_cert_file=ca_cert) as client:

        print("\n=== 初始化 MCP 会话 ===")
        init_result = client.initialize()
        server_info = init_result.get("result", {}).get("serverInfo", {})
        print(f"  会话 ID: {client.session_id}")
        print(f"  服务器: {server_info.get('name', '未知')} v{server_info.get('version', '?')}")

        print("\n=== 内存占用 Top 5 ===")
        result = client.call_tool("get_top_memory_processes", {"limit": 5})
        print_mcp_result(result, "get_top_memory_processes")

        print("\n=== CPU 占用 Top 5 ===")
        result = client.call_tool("get_top_cpu_processes", {"limit": 5})
        print_mcp_result(result, "get_top_cpu_processes")


if __name__ == "__main__":
    main()
