"""Disk usage and I/O metrics, with inaccessible mounts skipped safely."""

from __future__ import annotations

import psutil


def collect_disks() -> list[dict]:
    disks = []
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except (OSError, PermissionError):
            continue
        disks.append({
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "filesystem": partition.fstype,
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "percent": usage.percent,
        })
    return disks


def collect_disk_io() -> dict:
    """Collect system-wide disk I/O activity."""
    try:
        counters = psutil.disk_io_counters(perdisk=False)
        if not counters:
            return {}
        return {
            "read_count": counters.read_count,
            "write_count": counters.write_count,
            "read_bytes": counters.read_bytes,
            "write_bytes": counters.write_bytes,
            "read_time": counters.read_time,
            "write_time": counters.write_time,
        }
    except (OSError, PermissionError):
        return {}