#!/usr/bin/env python3
"""
Example MCP client with AK/SK HMAC signing and CA certificate verification.

Demonstrates how to:
1. Sign requests with AK/SK (HMAC-SHA256 over canonical request)
2. Connect to the MCP server over HTTPS with CA trust chain verification
3. Initialize an MCP session and call tools (get_top_memory_processes, get_top_cpu_processes)

Usage:
    python client_example.py --ak <access_key> --sk <secret_key> [--host <host>] [--port 8443] [--no-ssl]
"""
import argparse
import hashlib
import hmac
import json
import os
import ssl
import time
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
DEFAULT_CA_CERT = str(PROJECT_ROOT / "certs" / "ca.crt")


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


def create_ssl_context(ca_cert_file: str, check_hostname: bool = False) -> ssl.SSLContext:
    """Create SSL context with CA certificate verification."""
    ctx = ssl.create_default_context(cafile=ca_cert_file)
    ctx.check_hostname = check_hostname
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


def parse_sse(data: str) -> list[dict]:
    """Parse SSE (Server-Sent Events) text into a list of event dicts."""
    events = []
    current = {}
    for line in data.split("\n"):
        if not line.strip():
            if current:
                events.append(current)
                current = {}
            continue
        if line.startswith(":"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            value = value.strip()
            if key == "data":
                current["data"] = current.get("data", "") + value
            else:
                current[key] = value
    if current:
        events.append(current)
    return events


class McpClient:
    """Minimal MCP Streamable HTTP client with AK/SK auth and CA verification."""

    def __init__(self, host: str, port: int, ak: str, sk: str, use_ssl: bool = True,
                 ca_cert_file: str = DEFAULT_CA_CERT):
        scheme = "https" if use_ssl else "http"
        self.base_url = f"{scheme}://{host}:{port}"
        self.ak = ak
        self.sk = sk
        self.session_id = None
        self.use_ssl = use_ssl
        if use_ssl:
            if not os.path.exists(ca_cert_file):
                raise FileNotFoundError(
                    f"CA certificate not found: {ca_cert_file}\n"
                    f"Generate it with: openssl req -x509 -newkey rsa:4096 ..."
                )
            self.ctx = create_ssl_context(ca_cert_file)
        else:
            self.ctx = None

    def _request(self, method: str, path: str, body: dict) -> dict:
        """Send a signed MCP request and return parsed JSON-RPC result."""
        body_bytes = json.dumps(body).encode()
        headers = sign_request(self.ak, self.sk, method, path, body_bytes)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body_bytes,
            headers=headers,
            method=method,
        )
        with urllib.request.urlopen(req, context=self.ctx, timeout=30) as resp:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid

            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read().decode()

            if "text/event-stream" in content_type:
                events = parse_sse(raw)
                for event in events:
                    if "data" in event:
                        try:
                            return json.loads(event["data"])
                        except json.JSONDecodeError:
                            continue
                return {}
            else:
                return json.loads(raw)

    def initialize(self) -> dict:
        """Initialize MCP session."""
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
        """Call an MCP tool."""
        return self._request("POST", "/mcp", {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
            "id": 2,
        })


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
    parser.add_argument("--no-ssl", action="store_true", help="Use HTTP instead of HTTPS")
    parser.add_argument("--ca-cert", default=DEFAULT_CA_CERT,
                        help=f"Path to CA certificate for verification (default: {DEFAULT_CA_CERT})")
    args = parser.parse_args()

    use_ssl = not args.no_ssl
    ca_cert = args.ca_cert

    # Step 1: Health check
    print("=== Health Check ===")
    scheme = "https" if use_ssl else "http"
    url = f"{scheme}://{args.host}:{args.port}/health"
    ctx = create_ssl_context(ca_cert) if use_ssl else None
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        print(f"  {resp.read().decode()}")

    # Step 2: Create client and initialize
    client = McpClient(args.host, args.port, args.ak, args.sk,
                       use_ssl=use_ssl, ca_cert_file=ca_cert)

    print("\n=== Initialize MCP Session ===")
    init_result = client.initialize()
    server_info = init_result.get("result", {}).get("serverInfo", {})
    print(f"  Session ID: {client.session_id}")
    print(f"  Server: {server_info.get('name', 'unknown')} v{server_info.get('version', '?')}")

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
