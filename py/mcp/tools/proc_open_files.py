import itertools
import logging

import psutil

logger = logging.getLogger(__name__)


def _lsof(pid: int = 0, quick_filter: list[str] | None = None):
    """查询进程打开的文件句柄。pid=0 表示所有进程。"""
    qfs = [f.lower() for f in (quick_filter or [])]
    res = {}
    for p in psutil.process_iter():
        try:
            info = p.as_dict(["pid", "open_files", "cmdline", "username"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        p_ofs = info.get("open_files") or []
        p_cmd = " ".join(c for c in (info.get("cmdline") or []) if c)
        p_user = info.get("username", "")
        p_pid = info["pid"]

        if pid != 0 and pid != p_pid:
            continue

        if qfs and p_ofs:
            matched = [of for of in p_ofs
                       if any(qf in (of.path or "").lower() for qf in qfs)]
            if matched:
                res[str(p_pid)] = _build_entry(matched, p_cmd, p_user)
        elif not qfs:
            res[str(p_pid)] = _build_entry(p_ofs, p_cmd, p_user)

    return res


def _build_entry(open_files, cmd, user):
    return {
        "open_files": [
            {
                "path": str(getattr(of, "path", "")),
                "fd": getattr(of, "fd", ""),
                "mode": getattr(of, "mode", "Nosupport"),
            }
            for of in open_files
        ],
        "cmd": cmd,
        "user": user,
    }


def proc_open_files(
    pid: int = 0,
    file_filter: list[str] | None = None,
    verbose: bool = False,
) -> dict:
    """
    列出进程打开的文件句柄（类似 lsof）。

    参数:
        pid: 按 PID 筛选，0 表示所有进程（默认 0）。
        file_filter: 按文件名关键词筛选，大小写不敏感。
        verbose: True 输出每个 PID 的所有打开文件详情；False 仅按 file_filter 过滤。

    返回:
        {"<pid>": {"open_files": [...], "cmd": "...", "user": "..."}, ...}
    """
    result = _lsof(pid, file_filter)
    if not result:
        return {}

    if verbose:
        return result

    # 非 verbose 模式: 只保留匹配 file_filter 的文件
    qfs = [f.lower() for f in (file_filter or [])]
    if not qfs:
        return result

    filtered = {}
    for pid_str, entry in result.items():
        ofs = entry["open_files"]
        if len(ofs) == 1 and ofs[0]["path"] == "":
            continue
        filtered[pid_str] = entry
    return filtered


_tools = [proc_open_files]


def register_tools(mcp):
    for tool in _tools:
        mcp.tool()(tool)
