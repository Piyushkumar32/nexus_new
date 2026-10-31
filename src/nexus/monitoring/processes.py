"""Process inventory that tolerates processes disappearing or denying access."""

from __future__ import annotations

import time
from typing import Any

import psutil


def collect_processes(limit: int = 20, sort_by: str = "cpu") -> list[dict[str, Any]]:
    """Enumerate running processes with threads, status, and resource metrics."""
    if sort_by not in {"cpu", "memory"}:
        raise ValueError("sort_by must be 'cpu' or 'memory'")
    results = []
    attrs = ["pid", "name", "status", "create_time", "memory_percent", "num_threads", "username"]
    for process in psutil.process_iter(attrs=attrs, ad_value=None):
        try:
            info = process.info
            info["cpu_percent"] = process.cpu_percent(interval=None)
            created = info.get("create_time")
            info["running_seconds"] = max(0, int(time.time() - created)) if created else None
            results.append(info)
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    return sorted(results, key=lambda item: item.get(f"{sort_by}_percent") or 0, reverse=True)[:limit]