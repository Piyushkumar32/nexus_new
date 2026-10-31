"""Transparent health scoring from resource utilization."""


def calculate_health(
    metrics: dict,
    weights: dict[str, float] | None = None,
    warning_thresholds: dict[str, float] | None = None,
    class_thresholds: dict[str, float] | None = None,
) -> dict:
    weights = weights or {"cpu": 0.35, "memory": 0.35, "disk": 0.30}
    warning_thresholds = warning_thresholds or {"cpu": 80, "memory": 85, "disk": 90}
    class_thresholds = class_thresholds or {"healthy": 80, "degraded": 60}
    cpu = float(metrics["cpu"]["percent"])
    memory = float(metrics["memory"]["percent"])
    disks = metrics.get("disks", [])
    disk = max((float(item["percent"]) for item in disks), default=0.0)
    components = {"cpu": round(max(0, 100 - cpu), 1), "memory": round(max(0, 100 - memory), 1),
                  "disk": round(max(0, 100 - disk), 1)}
    total_weight = sum(weights.values())
    score = round(sum(components[key] * value for key, value in weights.items()) / total_weight)
    label = ("healthy" if score >= class_thresholds["healthy"]
             else "degraded" if score >= class_thresholds["degraded"] else "critical")
    recommendations = []
    for key, usage in (("cpu", cpu), ("memory", memory), ("disk", disk)):
        if usage >= warning_thresholds[key]:
            recommendations.append(f"Review elevated {key} utilization ({usage:.1f}%).")
    if not recommendations:
        recommendations.append("No immediate resource action is indicated.")
    return {"score": score, "classification": label, "components": components,
            "explanation": "Each component score is 100 minus its utilization; weighted components are averaged.",
            "recommendations": recommendations}