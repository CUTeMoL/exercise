#!/usr/bin/env python3
"""
CLI to manage AK/SK API keys for the MCP server.

Usage:
    python manage_keys.py create --description "My key"
    python manage_keys.py list
    python manage_keys.py disable <access_key>
    python manage_keys.py verify --ak <access_key> --sk <secret_key>
"""
import argparse
import sys
import time

from auth import (
    compute_signature,
    create_api_key,
    disable_api_key,
    get_db_connection,
    get_master_key,
    init_db,
    list_api_keys,
    load_config,
    verify_signature,
)


def cmd_create(args, conn, master_key):
    ak, sk = create_api_key(conn, master_key, args.description)
    print(f"Access Key: {ak}")
    print(f"Secret Key: {sk}")
    print()
    print("IMPORTANT: Save the Secret Key now — it will not be shown again.")


def cmd_list(args, conn, master_key):
    keys = list_api_keys(conn)
    if not keys:
        print("No API keys found.")
        return
    print(f"{'ID':<4} {'Access Key':<38} {'Description':<20} {'Enabled':<8} {'Created'}")
    print("-" * 96)
    for k in keys:
        print(
            f"{k['id']:<4} "
            f"{k['access_key']:<38} "
            f"{k['description'][:20]:<20} "
            f"{'Yes' if k['enabled'] else 'No':<8} "
            f"{k['created_at']}"
        )


def cmd_disable(args, conn, master_key):
    if disable_api_key(conn, args.access_key):
        print(f"API key '{args.access_key}' has been disabled.")
    else:
        print(f"API key '{args.access_key}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_verify(args, conn, master_key):
    """Self-test: sign a sample request and verify it locally."""
    config = load_config()
    tolerance = config.get("auth", {}).get("timestamp_tolerance_seconds", 300)

    ts = str(int(time.time()))
    method = "POST"
    path = "/mcp"
    body = b'{"jsonrpc":"2.0","method":"tools/list","id":1}'

    sig = compute_signature(method, path, ts, body, args.sk)
    print(f"Access Key:   {args.ak}")
    print(f"Timestamp:    {ts}")
    print(f"Signature:    {sig}")

    valid, err = verify_signature(conn, master_key, args.ak, sig, ts, method, path, body, tolerance)
    if valid:
        print("Verification: PASSED")
    else:
        print(f"Verification: FAILED — {err}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Manage MCP Server AK/SK Keys")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_create = subparsers.add_parser("create", help="Create a new AK/SK pair")
    p_create.add_argument("--description", default="", help="Optional description")

    subparsers.add_parser("list", help="List all API keys")

    p_disable = subparsers.add_parser("disable", help="Disable an API key")
    p_disable.add_argument("access_key", help="Access key to disable")

    p_verify = subparsers.add_parser("verify", help="Self-test AK/SK signing")
    p_verify.add_argument("--ak", required=True, help="Access key")
    p_verify.add_argument("--sk", required=True, help="Secret key")

    args = parser.parse_args()

    config = load_config()
    master_key = get_master_key(config)
    conn = get_db_connection(config["sqlite"]["path"])
    init_db(conn)

    try:
        if args.command == "create":
            cmd_create(args, conn, master_key)
        elif args.command == "list":
            cmd_list(args, conn, master_key)
        elif args.command == "disable":
            cmd_disable(args, conn, master_key)
        elif args.command == "verify":
            cmd_verify(args, conn, master_key)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
