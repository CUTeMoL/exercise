#!/usr/bin/env python3
"""
FastMCP 服务器：进程监控 + AK/SK 认证 + HTTPS 加密。

提供 MCP 工具:
- get_top_memory_processes: 进程内存占用排行（RSS，单位 B）
- get_top_cpu_processes: 进程 CPU 占用排行（每核 100%，多核可超 100%）

启动时启用 HTTPS (TLS) 和 AK/SK HMAC 签名认证。
"""
import logging
import os

import uvicorn
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth import (
    AkSkAuthMiddleware,
    get_db_connection,
    get_master_key,
    init_db,
    load_config,
)
from tools import register_all_tools

# 配置日志格式：时间 [级别] 模块: 消息
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── 加载配置 ──────────────────────────────────────────────────────────
config = load_config()
master_key = get_master_key(config)

# ── 初始化数据库 ──────────────────────────────────────────────────────
db_dir = os.path.dirname(config["sqlite"]["path"])
if db_dir:
    os.makedirs(db_dir, exist_ok=True)
conn = get_db_connection(config["sqlite"]["path"])
init_db(conn)
conn.close()
logger.info(f"数据库已初始化: {config['sqlite']['path']}")

# ── FastMCP 服务器 ────────────────────────────────────────────────────
mcp = FastMCP(name="Process Monitor", version="1.0.0")


# ── 自定义路由（无需认证）─────────────────────────────────────────────
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """健康检查端点，无需 AK/SK 认证。"""
    return JSONResponse({"status": "ok", "service": "mcp-process-monitor"})


# ── 注册 MCP 工具 ──────────────────────────────────────────────────────
register_all_tools(mcp)


# ── 入口 ──────────────────────────────────────────────────────────────
def main():
    """启动 MCP 服务器（HTTPS + AK/SK 认证）。"""
    ssl_config = config.get("ssl", {})

    # 构建 SSL 参数
    uvicorn_kwargs = {}
    if ssl_config.get("cert_file") and ssl_config.get("key_file"):
        uvicorn_kwargs["ssl_certfile"] = ssl_config["cert_file"]
        uvicorn_kwargs["ssl_keyfile"] = ssl_config["key_file"]

    # 构建 ASGI 应用，挂载认证中间件
    app = mcp.http_app()
    app.add_middleware(
        AkSkAuthMiddleware,
        db_path=config["sqlite"]["path"],
        master_key=master_key,
        tolerance=config.get("auth", {}).get("timestamp_tolerance_seconds", 300),
        max_body_size=config.get("auth", {}).get("max_body_size", 1_048_576),
    )

    host = config["server"]["host"]
    port = config["server"]["port"]

    logger.info(
        f"正在启动 MCP 服务器: https://{host}:{port} "
        f"(SSL: {'已启用' if uvicorn_kwargs else '未启用'})"
    )

    uvicorn.run(app, host=host, port=port, **uvicorn_kwargs, log_level="info")


if __name__ == "__main__":
    main()
