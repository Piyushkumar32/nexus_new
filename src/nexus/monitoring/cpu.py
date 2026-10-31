"""Load averages, per-core utilization, and core counts."""

from __future__ import annotations

import os

import psutil


def collect_cpu(interval: float = 0.1) -> dict:
    try:
        frequency = psutil.cpu_freq()
    except (NotImplementedError, OSError):
        frequency = None

    # Load averages (supported on Unix, return None on Windows if not available)
    try:
        load_avg = os.getloadavg() if hasattr(os, "getloadavg") else None
    except (OSError, AttributeError):
        load_avg = None

    return {
        "percent": psutil.cpu_percent(interval=max(0, interval)),
        "logical_cores": psutil.cpu_count(logical=True) or 0,
        "physical_cores": psutil.cpu_count(logical=False) or 0,
        "frequency_mhz": getattr(frequency, "current", None),
        "frequency_min": getattr(frequency, "min", None),
        "frequency_max": getattr(frequency, "max", None),
        "per_cpu_percent": psutil.cpu_percent(interval=None, percpu=True),
        "load_average": list(load_avg) if load_avg else None,
    }