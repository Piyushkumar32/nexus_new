"""Physical and swap memory metrics."""

import psutil


def collect_memory() -> dict:
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_bytes": memory.total, "used_bytes": memory.used,
        "available_bytes": memory.available, "percent": memory.percent,
        "swap_total_bytes": swap.total, "swap_used_bytes": swap.used,
        "swap_percent": swap.percent,
        "health": "critical" if memory.percent >= 95 else "warning" if memory.percent >= 85 else "healthy",
    }