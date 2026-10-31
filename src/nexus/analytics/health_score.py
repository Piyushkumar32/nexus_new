"""Transparent health scoring with multi-component weights and network awareness."""

from __future__ import annotations

from typing import Any


def calculate_health(
    metrics: dict[str, Any],
    weights: dict[str, float] | None = None,
    warning_thresholds: dict[str, float] | None = None,
    class_thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    weights = weights or {"cpu": 0.35, "memory": 0.35, "disk": 0.30}
    warning_thresholds = warning_thresholds or {"cpu": 80, "memory": 85, "disk": 90}
    class_thresholds = class_thresholds or {"healthy": 80, "degraded": 60}

    cpu = float(metrics.get("cpu", {}).get("percent", 0.0))
    memory = float(metrics.get("memory", {}).get("percent", 0.0))
    disks = metrics.get("disks", [])
    disk = max((float(item["percent"]) for item in disks), default=0.0)

    # Component scores: 100 is best, 0 is worst
    components: dict[str, float] = {
        "cpu": round(max(0.0, 100.0 - cpu), 1),
        "memory": round(max(0.0, 100.0 - memory), 1),
        "disk": round(max(0.0, 100.0 - disk), 1),
    }

    # Optional network health component if weighted
    if "network" in weights:
        network = metrics.get("network", {})
        errin = network.get("errin", 0)
        errout = network.get("errout", 0)
        net_score = 100.0 if (errin + errout) == 0 else max(50.0, 100.0 - (errin + errout) * 2)
        components["network"] = round(net_score, 1)

    total_weight = sum(weights.get(k, 0.0) for k in components)
    if total_weight <= 0:
        total_weight = 1.0

    score = round(sum(components[key] * weights.get(key, 0.0) for key in components if key in weights) / total_weight)
    score = max(0, min(100, score))

    label = (
        "healthy"
        if score >= class_thresholds.get("healthy", 80)
        else "degraded"
        if score >= class_thresholds.get("degraded", 60)
        else "critical"
    )

    recommendations: list[str] = []
    for key, usage in (("cpu", cpu), ("memory", memory), ("disk", disk)):
        threshold = warning_thresholds.get(key, 80)
        if usage >= threshold:
            recommendations.append(f"Review elevated {key} utilization ({usage:.1f}% >= {threshold}% threshold).")

    if not recommendations:
        recommendations.append("All primary system resources are within acceptable operating parameters.")

    return {
        "score": score,
        "classification": label,
        "components": components,
        "explanation": "Each component score is 100 minus its utilization; weighted components are averaged.",
        "recommendations": recommendations,
    }