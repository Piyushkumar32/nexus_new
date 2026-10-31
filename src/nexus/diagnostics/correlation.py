"""Correlated multi-metric anomaly detection and root cause analyzer."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any


def analyze_correlated_incidents(
    metrics: dict[str, Any],
    findings: list[dict[str, Any]],
    anomalies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Correlate simultaneous metrics pressure into high-confidence root-cause incidents."""
    incidents: list[dict[str, Any]] = []

    cpu = float(metrics.get("cpu", {}).get("percent", 0.0))
    mem = float(metrics.get("memory", {}).get("percent", 0.0))
    disks = metrics.get("disks", [])
    max_disk = max((float(d.get("percent", 0.0)) for d in disks), default=0.0)

    # Correlation 1: CPU + Memory saturation (Thrashing / System Overload)
    if cpu >= 85.0 and mem >= 85.0:
        incidents.append({
            "incident_id": f"INC-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now(UTC).isoformat(),
            "title": "Severe System Thrashing & Host Saturation",
            "severity": "critical",
            "confidence": 0.95,
            "root_cause": "Simultaneous CPU exhaustion and memory saturation detected.",
            "evidence": [f"CPU: {cpu:.1f}%", f"Memory: {mem:.1f}%"],
            "suggested_remediation": (
                "Review top memory-consuming processes and page-fault rates. "
                "Restart non-essential background daemons."
            ),
        })

    # Correlation 2: Disk I/O or Capacity exhaustion with process warnings
    proc_findings = [f for f in findings if f.get("category") == "process"]
    if max_disk >= 90.0 and proc_findings:
        incidents.append({
            "incident_id": f"INC-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now(UTC).isoformat(),
            "title": "Storage Bottleneck Under Heavy Process Load",
            "severity": "high",
            "confidence": 0.88,
            "root_cause": f"Mountpoint near capacity ({max_disk:.1f}%) while processes show high resource usage.",
            "evidence": [f"Max Disk: {max_disk:.1f}%", f"Rogue Processes: {len(proc_findings)}"],
            "suggested_remediation": "Clean application temporary directories and archive logs to alternate storage.",
        })

    return incidents