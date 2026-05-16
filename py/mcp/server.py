#!/usr/bin/env python3
"""
FastMCP Server: Process monitoring with AK/SK authentication and HTTPS.

Provides MCP tools to query server process status:
- get_top_memory_processes: Top N processes by memory (RSS in bytes)
- get_top_cpu_processes: Top N processes by CPU percentage (per-core)

Starts with HTTPS (TLS) and AK/SK HMAC signature authentication.
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

logger = logging.getLogger(__name__)

# ── Load Configuration ──────────────────────────────────────────────
config = load_config()
master_key = get_master_key(config)

# ── Initialize Database ─────────────────────────────────────────────
os.makedirs(os.path.dirname(config["sqlite"]["path"]), exist_ok=True)
conn = get_db_connection(config["sqlite"]["path"])
init_db(conn)
conn.close()
logger.info(f"Database initialized at {config['sqlite']['path']}")

# ── FastMCP Server ──────────────────────────────────────────────────
mcp = FastMCP(name="Process Monitor", version="1.0.0")


# ── Custom Routes (no auth required) ────────────────────────────────
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "mcp-process-monitor"})


# ── MCP Tools ───────────────────────────────────────────────────────

@mcp.tool()
def get_top_memory_processes(limit: int = 10) -> list[dict]:
    """
    Get the top N processes by memory usage (RSS in bytes).

    Args:
        limit: Number of processes to return (default: 10).

    Returns:
        List of dicts with keys: pid, name, memory_bytes, sorted descending by memory.
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
    Get the top N processes by CPU usage percentage.

    CPU percent is per-core: each core contributes up to 100%.
    A process using two full cores will show ~200%.

    Args:
        limit: Number of processes to return (default: 10).
        interval: Sampling interval in seconds (default: 0.1).

    Returns:
        List of dicts with keys: pid, name, cpu_percent, sorted descending by CPU.
    """
    # Phase 1: collect processes and initialize CPU counters
    proc_objs = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            proc.cpu_percent()  # First call always returns 0.0, initializes counter
            proc_objs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Phase 2: wait for the sampling interval
    time.sleep(interval)

    # Phase 3: read actual CPU percentages
    results = []
    for proc in proc_objs:
        try:
            cpu = proc.cpu_percent()
            results.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"],
                "cpu_percent": cpu,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    results.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return results[:limit]


# ── Entry Point ─────────────────────────────────────────────────────
def main():
    ssl_config = config.get("ssl", {})

    # Build SSL kwargs for uvicorn
    uvicorn_kwargs = {}
    if ssl_config.get("cert_file") and ssl_config.get("key_file"):
        uvicorn_kwargs["ssl_certfile"] = ssl_config["cert_file"]
        uvicorn_kwargs["ssl_keyfile"] = ssl_config["key_file"]

    # Build the ASGI app with auth middleware wrapping FastMCP
    app = mcp.http_app()
    app.add_middleware(
        AkSkAuthMiddleware,
        db_path=config["sqlite"]["path"],
        master_key=master_key,
        tolerance=config.get("auth", {}).get("timestamp_tolerance_seconds", 300),
    )

    host = config["server"]["host"]
    port = config["server"]["port"]

    logger.info(
        f"Starting MCP server on https://{host}:{port} "
        f"(SSL: {'enabled' if uvicorn_kwargs else 'disabled'})"
    )

    uvicorn.run(app, host=host, port=port, **uvicorn_kwargs, log_level="info")


if __name__ == "__main__":
    main()
