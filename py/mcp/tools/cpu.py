import time

import psutil


def get_top_cpu_processes(limit: int = 10, interval: float = 0.1) -> list[dict]:
    """
    查询 CPU 占用最高的 N 个进程（每核 100%，多核可超 100%）。

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
    proc_objs = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            proc.cpu_percent()
            proc_objs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(interval)

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


_tools = [get_top_cpu_processes]


def register_tools(mcp):
    for tool in _tools:
        mcp.tool()(tool)
