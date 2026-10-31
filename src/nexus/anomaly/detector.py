"""Threshold and first-difference anomaly detection with historical baselines."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any


class AnomalyDetector:
    def __init__(self, spike_delta: float = 25.0, repeated_errors: int = 3) -> None:
        self.spike_delta = spike_delta
        self.repeated_errors = repeated_errors
        self.previous: dict[str, float] = {}
        self.history: list[dict[str, Any]] = []
        self.error_counts: dict[str, int] = defaultdict(int)

    def inspect(
        self,
        metrics: dict[str, Any],
        error_messages: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []

        values = {
            "cpu": float(metrics.get("cpu", {}).get("percent", 0.0)),
            "memory": float(metrics.get("memory", {}).get("percent", 0.0)),
            "disk": max((float(item["percent"]) for item in metrics.get("disks", [])), default=0.0),
        }

        for key, value in values.items():
            old = self.previous.get(key)
            if old is not None and (value - old) >= self.spike_delta:
                found.append(
                    self._make(
                        "resource_spike",
                        "medium",
                        f"{key.upper()} utilization abruptly spiked by {value - old:.1f} points (from {old:.1f}% to {value:.1f}%).",
                        round(value, 2),
                        expected=round(old, 2),
                        suggested_action=f"Investigate active processes causing sudden {key} surge.",
                    )
                )
            self.previous[key] = value

        for message in error_messages or []:
            self.error_counts[message] += 1
            if self.error_counts[message] == self.repeated_errors:
                found.append(
                    self._make(
                        "repeated_error",
                        "medium",
                        f"Error repeated {self.error_counts[message]} times: {message}",
                        float(self.error_counts[message]),
                        expected=float(self.repeated_errors - 1),
                        suggested_action="Review application stack trace and resolve recurring exceptions.",
                    )
                )

        self.history.extend(found)
        return found

    @staticmethod
    def _make(
        kind: str,
        severity: str,
        description: str,
        value: float,
        expected: float | None = None,
        suggested_action: str = "",
    ) -> dict[str, Any]:
        return {
            "id": f"ANOM-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now(UTC).isoformat(),
            "type": kind,
            "category": kind,
            "severity": severity,
            "description": description,
            "value": value,
            "expected_value": expected,
            "suggested_action": suggested_action,
        }