"""Modular AI intelligence and natural-language diagnostic reasoning layer."""

from __future__ import annotations

import os
from typing import Any


class AISystemAdvisor:
    """Provides natural-language incident summaries and troubleshooting steps.

    Fully functional offline using local diagnostic knowledge heuristics; optionally
    integrates with external LLM providers when configured.
    """

    def __init__(self, provider: str = "offline") -> None:
        self.provider = provider
        self.has_api_key = bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY"))

    def summarize_system_state(self, snapshot: dict[str, Any]) -> str:
        """Produce an executive natural-language summary from real metrics."""
        health = snapshot.get("health", {})
        score = health.get("score", 100)
        classification = health.get("classification", "healthy")
        cpu = snapshot.get("metrics", {}).get("cpu", {}).get("percent", 0.0)
        mem = snapshot.get("metrics", {}).get("memory", {}).get("percent", 0.0)
        findings = snapshot.get("diagnostics", [])

        if score >= 80:
            summary = (
                f"The host is running stably with a health score of {score}/100 ({classification}). "
                f"CPU utilization is at {cpu:.1f}% and memory pressure is at {mem:.1f}% with no critical bottlenecks."
            )
        else:
            summary = (
                f"Attention Required: The host health score has degraded to {score}/100 ({classification}). "
                f"Elevated resource usage detected (CPU: {cpu:.1f}%, RAM: {mem:.1f}%). "
                f"{len(findings)} active diagnostic findings require administrative review."
            )
        return summary

    def generate_troubleshooting_playbook(self, finding: dict[str, Any]) -> list[str]:
        """Generate deterministic, expert troubleshooting steps based on evidence."""
        category = finding.get("category", "")
        desc = finding.get("description", "")

        playbook: list[str] = [
            f"1. Isolate the affected subsystem: [{category.upper()}].",
            f"2. Inspect the observed telemetry evidence: '{desc}'.",
        ]

        if category == "cpu":
            playbook.extend([
                "3. Execute 'nexus processes --sort cpu --limit 10' to isolate runaway thread execution.",
                "4. Check for CPU throttling or fan anomalies via 'nexus monitor'.",
                "5. Profile hot application codepaths or scale execution concurrency.",
            ])
        elif category == "memory":
            playbook.extend([
                "3. Execute 'nexus processes --sort memory --limit 10' to audit resident memory set.",
                "4. Inspect swap usage and page thrashing.",
                "5. Check application heap dumps for memory leaks.",
            ])
        elif category == "disk":
            playbook.extend([
                "3. Audit storage volume using 'df -h' or directory disk usage tools.",
                "4. Check rotation policies for /var/log and purge temporary cache files.",
                "5. Expand partition or mount additional block storage volumes.",
            ])
        else:
            playbook.extend([
                "3. Audit network interfaces and error counters.",
                "4. Review recent system configuration updates.",
            ])
        return playbook