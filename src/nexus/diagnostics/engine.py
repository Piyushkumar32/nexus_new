"""Diagnostic engine coordinating rule evaluations and findings."""

from __future__ import annotations

from typing import Any

from nexus.diagnostics.rules import evaluate_rules


def diagnose(
    metrics: dict[str, Any],
    processes: list[dict[str, Any]],
    thresholds: dict[str, float],
) -> list[dict[str, Any]]:
    """Evaluate system metrics and process inventory against diagnostic rules."""
    return evaluate_rules(metrics, processes, thresholds)