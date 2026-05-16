#!/usr/bin/env python3
"""
进程内存监控 MCP Server
查询系统中所有进程的内存占用，并按内存使用量排序返回。
"""

import psutil
from fastmcp import FastMCP

# 创建 MCP Server 实例
mcp = FastMCP(name="Process Memory Monitor")

@mcp.tool()
def get_top_memory_processes(limit: int = 10) -> list:
    """
    获取当前系统中内存占用最高的进程列表。
    
    Args:
        limit: 返回的进程数量，默认返回前 10 个占用最高的进程
        
    Returns:
        每个进程包含 pid、name、memory_mb（MB 单位）三个字段的列表，
        按内存占用从高到低排序。
    """
    processes = []
    
    # 遍历所有正在运行的进程
    for proc in psutil.process_iter(attrs=['pid', 'name', 'memory_info']):
        try:
            # 获取进程内存信息（RSS = 常驻物理内存）
            mem_info = proc.info['memory_info']
            if mem_info is not None:
                # 将字节转换为 MB
                mem_mb = mem_info.rss / (1024 * 1024)
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory_mb': round(mem_mb, 2)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # 忽略无法访问（权限不足）或已结束的进程，继续处理下一个
            continue
    
    # 按内存占用从大到小排序
    processes.sort(key=lambda x: x['memory_mb'], reverse=True)
    
    # 返回指定数量的进程列表
    return processes[:limit]

if __name__ == "__main__":
    # 以 stdio 模式运行 MCP 服务器（与 AI 客户端通信的标准方式）
    mcp.run()
