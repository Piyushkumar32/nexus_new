"""CPU metrics collected through psutil."""

import psutil


def collect_cpu(interval: float = 0.1) -> dict:
    try:
        frequency = psutil.cpu_freq()
    except (NotImplementedError, OSError):
        frequency = None
    return {
        "percent": psutil.cpu_percent(interval=max(0, interval)),
        "logical_cores": psutil.cpu_count(logical=True) or 0,
        "physical_cores": psutil.cpu_count(logical=False) or 0,
        "frequency_mhz": frequency.current if frequency else None,
        "per_cpu_percent": psutil.cpu_percent(interval=None, percpu=True),
    }