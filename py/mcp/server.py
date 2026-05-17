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
import time

import psutil
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
os.makedirs(os.path.dirname(config["sqlite"]["path"]), exist_ok=True)
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


# ── MCP 工具 ──────────────────────────────────────────────────────────

@mcp.tool()
def get_top_memory_processes(limit: int = 10) -> list[dict]:
    """
    查询内存占用最高的 N 个进程（RSS，单位 B）。

    参数:
        limit: 返回的进程数量（默认 10）。

    返回:
        字典列表，每项包含 pid, name, memory_bytes，按内存降序排列。
    """
    processes = []
    for proc in psutil.process_iter(attrs=["pid", "name", "memory_info"]):
        try:
            mem_info = proc.info["memory_info"]
            if mem_info is not None:
                processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "memory_bytes": mem_info.rss,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda x: x["memory_bytes"], reverse=True)
    return processes[:limit]


@mcp.tool()
def get_top_cpu_processes(limit: int = 10, interval: float = 0.1) -> list[dict]:
    """
    查询 CPU 占用最高的 N 个进程（每核 100%，多核可超 100%）。

    本函数是同步的，但 FastMCP 会自动将其放入线程池执行，
    因此 time.sleep() 不会阻塞异步事件循环。

    采用 psutil 推荐的批量测量方式:
      1. 对所有进程调用 cpu_percent()（返回 0.0，初始化内部计数器）
      2. 统一等待一个采样周期
      3. 再次对所有进程调用 cpu_percent()（返回真实值）

    参数:
        limit: 返回的进程数量（默认 10）。
        interval: 采样间隔，单位秒（默认 0.1）。

    返回:
        字典列表，每项包含 pid, name, cpu_percent，按 CPU 降序排列。
    """
    # 第一步：收集进程并初始化 CPU 计数器
    proc_objs = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            proc.cpu_percent()  # 首次调用初始化内部计数器，返回 0.0
            proc_objs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # 第二步：等待一个采样周期
    time.sleep(interval)

    # 第三步：读取真实的 CPU 百分比
    results = []
    for proc in proc_objs:
        try:
            cpu = proc.cpu_percent()  # 第二次调用返回距上次调用的差值
            results.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"],
                "cpu_percent": cpu,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    results.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return results[:limit]


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
