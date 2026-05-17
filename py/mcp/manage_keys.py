#!/usr/bin/env python3
"""
AK/SK 密钥管理 CLI 工具。

用法:
    python manage_keys.py create --description "描述信息"    创建新的 AK/SK 对
    python manage_keys.py list                               列出所有密钥
    python manage_keys.py disable <access_key>               禁用指定密钥
    python manage_keys.py verify --ak <ak> --sk <sk>         自测签名验证
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
    """创建一对新的 AK/SK。"""
    ak, sk = create_api_key(conn, master_key, args.description)
    print(f"Access Key: {ak}")
    print(f"Secret Key: {sk}")
    print()
    print("重要: 请立即保存 Secret Key，后续将无法再次查看。")


def cmd_list(args, conn, master_key):
    """列出所有 API 密钥（不显示加密的 SK）。"""
    keys = list_api_keys(conn)
    if not keys:
        print("暂无 API 密钥。")
        return
    print(f"{'ID':<4} {'Access Key':<38} {'描述':<20} {'启用':<6} {'创建时间'}")
    print("-" * 96)
    for k in keys:
        print(
            f"{k['id']:<4} "
            f"{k['access_key']:<38} "
            f"{k['description'][:20]:<20} "
            f"{'是' if k['enabled'] else '否':<6} "
            f"{k['created_at']}"
        )


def cmd_disable(args, conn, master_key):
    """禁用指定的 API 密钥。"""
    if disable_api_key(conn, args.access_key):
        print(f"API 密钥 '{args.access_key}' 已禁用。")
    else:
        print(f"API 密钥 '{args.access_key}' 未找到。", file=sys.stderr)
        sys.exit(1)


def cmd_verify(args, conn, master_key):
    """自测: 对一条示例请求签名并本地验证，用于诊断签名计算是否正确。"""
    config = load_config()
    tolerance = config.get("auth", {}).get("timestamp_tolerance_seconds", 300)

    ts = str(int(time.time()))
    method = "POST"
    path = "/mcp"
    body = b'{"jsonrpc":"2.0","method":"tools/list","id":1}'

    sig = compute_signature(method, path, ts, body, args.sk)
    print(f"Access Key:   {args.ak}")
    print(f"时间戳:       {ts}")
    print(f"签名:         {sig}")

    valid, err = verify_signature(conn, master_key, args.ak, sig, ts, method, path, body, tolerance)
    if valid:
        print("验证结果:     通过")
    else:
        print(f"验证结果:     失败 — {err}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="MCP 服务器 AK/SK 密钥管理工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_create = subparsers.add_parser("create", help="创建新的 AK/SK 对")
    p_create.add_argument("--description", default="", help="可选的描述信息")

    subparsers.add_parser("list", help="列出所有 API 密钥")

    p_disable = subparsers.add_parser("disable", help="禁用指定的 API 密钥")
    p_disable.add_argument("access_key", help="要禁用的 Access Key")

    p_verify = subparsers.add_parser("verify", help="自测 AK/SK 签名计算是否正确")
    p_verify.add_argument("--ak", required=True, help="Access Key")
    p_verify.add_argument("--sk", required=True, help="Secret Key")

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
