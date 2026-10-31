"""Threshold and first-difference anomaly detection with an in-memory history."""

from collections import defaultdict
from datetime import datetime, timezone


class AnomalyDetector:
    def __init__(self, spike_delta: float = 25, repeated_errors: int = 3) -> None:
        self.spike_delta = spike_delta
        self.repeated_errors = repeated_errors
        self.previous: dict[str, float] = {}
        self.history: list[dict] = []
        self.error_counts: dict[str, int] = defaultdict(int)

    def inspect(self, metrics: dict, error_messages: list[str] | None = None) -> list[dict]:
        found = []
        values = {"cpu": metrics.get("cpu", {}).get("percent", 0),
                  "memory": metrics.get("memory", {}).get("percent", 0),
                  "disk": max((item["percent"] for item in metrics.get("disks", [])), default=0)}
        for key, value in values.items():
            old = self.previous.get(key)
            if old is not None and value - old >= self.spike_delta:
                found.append(self._make("resource_spike", "medium", f"{key} utilization increased by {value-old:.1f} points.", value))
            self.previous[key] = value
        for message in error_messages or []:
            self.error_counts[message] += 1
            if self.error_counts[message] == self.repeated_errors:
                found.append(self._make("repeated_error", "medium", f"Error repeated {self.error_counts[message]} times: {message}",
                                        self.error_counts[message]))
        self.history.extend(found)
        return found

    @staticmethod
    def _make(kind: str, severity: str, description: str, value: float) -> dict:
        return {"timestamp": datetime.now(timezone.utc).isoformat(), "type": kind,
                "severity": severity, "description": description, "value": value}