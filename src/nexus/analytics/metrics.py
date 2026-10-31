"""Metrics aggregation, statistics, and baseline calculators."""

from __future__ import annotations

from typing import Any


def calculate_aggregations(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate min, max, average, and latest metrics across historical snapshots."""
    if not snapshots:
        return {}

    cpu_values = []
    memory_values = []
    disk_values = []

    for snap in snapshots:
        metrics = snap.get("metrics", snap)
        if "cpu" in metrics and "percent" in metrics["cpu"]:
            cpu_values.append(float(metrics["cpu"]["percent"]))
        if "memory" in metrics and "percent" in metrics["memory"]:
            memory_values.append(float(metrics["memory"]["percent"]))
        if "disks" in metrics and metrics["disks"]:
            disk_values.append(max(float(d.get("percent", 0.0)) for d in metrics["disks"]))

    def stats(vals: list[float]) -> dict[str, float]:
        if not vals:
            return {"min": 0.0, "max": 0.0, "avg": 0.0, "latest": 0.0}
        return {
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
            "avg": round(sum(vals) / len(vals), 2),
            "latest": round(vals[-1], 2),
        }

    return {
        "sample_count": len(snapshots),
        "cpu": stats(cpu_values),
        "memory": stats(memory_values),
        "disk": stats(disk_values),
    }