"""Diagnostic rules and findings engine."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any


def evaluate_rules(metrics: dict[str, Any], processes: list[dict[str, Any]], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    def add(category: str, severity: str, desc: str, val: float, thresh: float, act: str, evidence: str = "") -> None:
        findings.append({
            "id": f"FIND-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": severity,
            "category": category,
            "description": desc,
            "value": round(val, 2),
            "threshold": thresh,
            "evidence": evidence or f"Current {category} value {val:.1f} exceeds threshold {thresh:.1f}",
            "suggested_action": act,
        })

    # CPU rule
    cpu_percent = float(metrics.get("cpu", {}).get("percent", 0.0))
    cpu_warning = float(thresholds.get("cpu_warning", 80.0))
    if cpu_percent >= 95:
        add("cpu", "critical", "Severe CPU bottleneck detected across host.", cpu_percent, 95.0,
            "Identify top CPU-consuming processes immediately and check for run-away tasks.",
            f"Host CPU saturation at {cpu_percent}%.")
    elif cpu_percent >= cpu_warning:
        add("cpu", "high" if cpu_percent >= 90 else "medium",
            "CPU utilization exceeds the configured warning threshold.", cpu_percent, cpu_warning,
            "Inspect CPU-intensive processes and check for sustained workload.",
            f"Host CPU usage at {cpu_percent}%.")

    # Memory rule
    mem_percent = float(metrics.get("memory", {}).get("percent", 0.0))
    mem_warning = float(thresholds.get("memory_warning", 85.0))
    if mem_percent >= 95:
        add("memory", "critical", "Critical memory exhaustion risk: host RAM nearly depleted.", mem_percent, 95.0,
            "Terminate non-essential processes or allocate additional RAM to prevent OOM.",
            f"Host memory usage at {mem_percent}%.")
    elif mem_percent >= mem_warning:
        add("memory", "high" if mem_percent >= 90 else "medium",
            "Memory utilization exceeds the configured warning threshold.", mem_percent, mem_warning,
            "Review memory-heavy processes and close unused workloads.",
            f"Host memory usage at {mem_percent}%.")

    # Disk rule
    disk_warning = float(thresholds.get("disk_warning", 90.0))
    for disk in metrics.get("disks", []):
        d_pct = float(disk.get("percent", 0.0))
        mount = disk.get("mountpoint", "unknown")
        if d_pct >= 95:
            add("disk", "critical", f"Critical disk exhaustion risk on {mount}.", d_pct, 95.0,
                f"Immediately purge temporary files or increase volume capacity on {mount}.",
                f"Mount {mount} is at {d_pct}% capacity.")
        elif d_pct >= disk_warning:
            add("disk", "high" if d_pct >= 92 else "medium",
                f"Disk usage is high on {mount}.", d_pct, disk_warning,
                f"Free disk space or expand the volume on {mount}.",
                f"Mount {mount} is at {d_pct}% capacity.")

    # Process rules
    proc_cpu_thresh = float(thresholds.get("process_cpu_warning", 80.0))
    proc_mem_thresh = float(thresholds.get("process_memory_warning", 20.0))
    for proc in processes:
        p_cpu = float(proc.get("cpu_percent") or 0.0)
        p_mem = float(proc.get("memory_percent") or 0.0)
        p_name = proc.get("name") or str(proc.get("pid"))
        p_pid = proc.get("pid", 0)

        if p_cpu >= proc_cpu_thresh:
            add("process", "high" if p_cpu >= 90 else "medium",
                f"Process '{p_name}' (PID: {p_pid}) has high CPU usage ({p_cpu:.1f}%).", p_cpu, proc_cpu_thresh,
                "Review the process workload; profile or restart if unresponsive.",
                f"Process PID {p_pid} consuming {p_cpu:.1f}% CPU.")

        if p_mem >= proc_mem_thresh:
            add("process", "high" if p_mem >= 40 else "medium",
                f"Process '{p_name}' (PID: {p_pid}) has high memory usage ({p_mem:.1f}%).", p_mem, proc_mem_thresh,
                "Review the process memory footprint and inspect for memory leaks.",
                f"Process PID {p_pid} consuming {p_mem:.1f}% memory.")

    # Network packet errors rule
    network = metrics.get("network", {})
    errin = network.get("errin", 0)
    errout = network.get("errout", 0)
    if (errin + errout) > 100:
        add("network", "medium", "Elevated network packet errors or drops observed.", float(errin + errout), 100.0,
            "Check network interface cables, drivers, and duplex configuration.",
            f"Total packet errors: in={errin}, out={errout}.")

    return findings