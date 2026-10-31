"""Rule-based resource and process diagnostics."""

from datetime import datetime, timezone


def diagnose(metrics: dict, processes: list[dict], thresholds: dict) -> list[dict]:
    findings = []

    def add(category: str, value: float, threshold: float, description: str, action: str) -> None:
        findings.append({"timestamp": datetime.now(timezone.utc).isoformat(), "severity": "high" if value >= 95 else "medium",
                         "category": category, "description": description, "value": round(value, 2),
                         "threshold": threshold, "suggested_action": action})

    cpu = metrics["cpu"]["percent"]
    if cpu >= thresholds["cpu_warning"]:
        add("cpu", cpu, thresholds["cpu_warning"], "CPU utilization exceeds the configured warning threshold.",
            "Inspect CPU-intensive processes and check for sustained workload.")
    memory = metrics["memory"]["percent"]
    if memory >= thresholds["memory_warning"]:
        add("memory", memory, thresholds["memory_warning"], "Memory utilization exceeds the configured warning threshold.",
            "Review memory-heavy processes and close unused workloads.")
    for disk in metrics.get("disks", []):
        if disk["percent"] >= thresholds["disk_warning"]:
            add("disk", disk["percent"], thresholds["disk_warning"],
                f"Disk usage is high on {disk['mountpoint']}.", "Free disk space or expand the volume.")
    for process in processes:
        if (process.get("cpu_percent") or 0) >= thresholds["process_cpu_warning"]:
            add("process", process["cpu_percent"], thresholds["process_cpu_warning"],
                f"Process {process.get('name') or process.get('pid')} has high CPU usage.",
                "Review the process workload; stop it only if safe to do so.")
        if (process.get("memory_percent") or 0) >= thresholds["process_memory_warning"]:
            add("process", process["memory_percent"], thresholds["process_memory_warning"],
                f"Process {process.get('name') or process.get('pid')} has high memory usage.",
                "Review the process and its memory demand.")
    return findings