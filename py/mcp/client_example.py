#!/usr/bin/env python3
"""
Example MCP client with AK/SK HMAC signing.

Demonstrates how to:
1. Sign requests with AK/SK (HMAC-SHA256 over canonical request)
2. Connect to the MCP server over HTTPS (with self-signed cert)
3. Initialize an MCP session and call tools (get_top_memory_processes, get_top_cpu_processes)

Usage:
    python client_example.py --ak <access_key> --sk <secret_key> [--host localhost] [--port 8443]
"""
import argparse
import hashlib
import hmac
import json
import ssl
import time
import urllib.request


def sign_request(ak: str, sk: str, method: str, path: str, body: bytes) -> dict:
    """Build AK/SK auth headers for a request."""
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


class McpClient:
    """Minimal MCP Streamable HTTP client with AK/SK auth."""

    def __init__(self, host: str, port: int, ak: str, sk: str):
        self.base_url = f"https://{host}:{port}"
        self.ak = ak
        self.sk = sk
        self.session_id = None
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def _request(self, method: str, path: str, body: dict, extra_headers: dict = None) -> dict:
        """Send a signed request and return parsed JSON response."""
        body_bytes = json.dumps(body).encode()
        headers = sign_request(self.ak, self.sk, method, path, body_bytes)
        if extra_headers:
            headers.update(extra_headers)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body_bytes,
            headers=headers,
            method=method,
        )
        with urllib.request.urlopen(req, context=self.ctx) as resp:
            # Capture session ID from response headers
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid
            return json.loads(resp.read().decode())

    def initialize(self) -> dict:
        """Initialize MCP session."""
        result = self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "aksk-client", "version": "1.0.0"},
            },
            "id": 1,
        })
        return result

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call an MCP tool."""
        result = self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
            "id": 2,
        })
        return result


def print_mcp_result(result: dict, tool_name: str):
    """Pretty-print MCP tool result."""
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
            print("  (no results)")
            return

        if tool_name == "get_top_memory_processes":
            print(f"{'PID':>8}  {'Name':<25} {'Memory (bytes)':>15}")
            print("-" * 52)
            for p in data:
                print(f"{p['pid']:>8}  {p['name']:<25} {p['memory_bytes']:>15,}")
        elif tool_name == "get_top_cpu_processes":
            print(f"{'PID':>8}  {'Name':<25} {'CPU (%)':>10}")
            print("-" * 47)
            for p in data:
                print(f"{p['pid']:>8}  {p['name']:<25} {p['cpu_percent']:>10.1f}")
        else:
            print(json.dumps(data, indent=2))
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")
        print(f"Raw: {json.dumps(result, indent=2)}")


def main():
    parser = argparse.ArgumentParser(description="MCP AK/SK Client Example")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--ak", required=True, help="Access Key")
    parser.add_argument("--sk", required=True, help="Secret Key")
    args = parser.parse_args()

    client = McpClient(args.host, args.port, args.ak, args.sk)

    # Step 1: Health check (no auth needed)
    print("=== Health Check ===")
    url = f"https://{args.host}:{args.port}/health"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx) as resp:
        print(f"  {resp.read().decode()}")

    # Step 2: Initialize MCP session
    print("\n=== Initialize MCP Session ===")
    init_result = client.initialize()
    print(f"  Session ID: {client.session_id}")
    print(f"  Server: {init_result.get('result', {}).get('serverInfo', {})}")

    # Step 3: Top memory processes
    print("\n=== Top 5 Memory Processes ===")
    result = client.call_tool("get_top_memory_processes", {"limit": 5})
    print_mcp_result(result, "get_top_memory_processes")

    # Step 4: Top CPU processes
    print("\n=== Top 5 CPU Processes ===")
    result = client.call_tool("get_top_cpu_processes", {"limit": 5})
    print_mcp_result(result, "get_top_cpu_processes")


if __name__ == "__main__":
    main()
