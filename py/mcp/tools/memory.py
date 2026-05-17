import psutil


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


_tools = [get_top_memory_processes]


def register_tools(mcp):
    for tool in _tools:
        mcp.tool()(tool)
