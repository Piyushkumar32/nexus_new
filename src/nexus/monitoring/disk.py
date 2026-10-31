"""Disk usage metrics, with inaccessible mounts skipped safely."""

import psutil


def collect_disks() -> list[dict]:
    disks = []
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except (OSError, PermissionError):
            continue
        disks.append({
            "device": partition.device, "mountpoint": partition.mountpoint,
            "filesystem": partition.fstype, "total_bytes": usage.total,
            "used_bytes": usage.used, "free_bytes": usage.free, "percent": usage.percent,
        })
    return disks