"""Host and consolidated resource information."""

import platform
import socket
import sys
import time

import psutil

from nexus.monitoring.cpu import collect_cpu
from nexus.monitoring.disk import collect_disks
from nexus.monitoring.memory import collect_memory


def collect_system_info() -> dict:
    boot_time = psutil.boot_time()
    return {
        "os": platform.system(), "os_version": platform.version(),
        "platform": platform.platform(), "hostname": socket.gethostname(),
        "python_version": sys.version.split()[0], "cpu_model": platform.processor() or "unknown",
        "logical_cores": psutil.cpu_count(logical=True) or 0,
        "physical_cores": psutil.cpu_count(logical=False) or 0,
        "total_ram_bytes": psutil.virtual_memory().total,
        "uptime_seconds": max(0, int(time.time() - boot_time)),
    }


def collect_metrics() -> dict:
    return {"captured_at": time.time(), "cpu": collect_cpu(), "memory": collect_memory(), "disks": collect_disks()}