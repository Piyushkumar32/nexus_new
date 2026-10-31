"""GPU hardware utilization collector supporting NVIDIA via nvidia-smi."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any


def collect_gpu() -> list[dict[str, Any]]:
    """Query available GPUs using nvidia-smi with cross-platform fallback."""
    binary = shutil.which("nvidia-smi")
    if not binary:
        return []

    try:
        cmd = [
            binary,
            "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
            "--format=csv,noheader,nounits",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=2.0,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []

        gpus: list[dict[str, Any]] = []
        for line in result.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 5:
                name = parts[0]
                total = float(parts[1]) if parts[1].replace(".", "", 1).isdigit() else 0.0
                used = float(parts[2]) if parts[2].replace(".", "", 1).isdigit() else 0.0
                free = float(parts[3]) if parts[3].replace(".", "", 1).isdigit() else 0.0
                util = float(parts[4]) if parts[4].replace(".", "", 1).isdigit() else 0.0
                temp = float(parts[5]) if len(parts) >= 6 and parts[5].replace(".", "", 1).isdigit() else None

                mem_percent = round((used / total * 100.0), 1) if total > 0 else 0.0

                gpus.append({
                    "name": name,
                    "memory_total_mb": total,
                    "memory_used_mb": used,
                    "memory_free_mb": free,
                    "memory_percent": mem_percent,
                    "utilization_percent": util,
                    "temperature_celsius": temp,
                })
        return gpus
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return []