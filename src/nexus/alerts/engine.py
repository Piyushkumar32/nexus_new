"""Alert management engine with deduplication, cooldowns, and suppression."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alert creation, suppression, cooldowns, and lifecycle."""

    def __init__(self, cooldown_seconds: float = 60.0) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._last_alert_times: dict[str, float] = {}
        self._acknowledged: set[str] = set()

    def process_findings(
        self,
        findings: list[dict[str, Any]],
        error_count: int = 0,
        repeated_threshold: int = 3,
        now_ts: float | None = None,
    ) -> list[dict[str, Any]]:
        current_time = now_ts or datetime.now(UTC).timestamp()
        alerts: list[dict[str, Any]] = []

        for finding in findings:
            key = f"{finding.get('category')}:{finding.get('description')}"
            last_time = self._last_alert_times.get(key)
            if last_time is not None and (current_time - last_time) < self.cooldown_seconds:
                continue

            alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
            alert = {
                "id": alert_id,
                "timestamp": finding.get("timestamp", datetime.now(UTC).isoformat()),
                "type": finding.get("category", "system"),
                "severity": finding.get("severity", "medium"),
                "message": finding.get("description", ""),
                "value": finding.get("value"),
                "threshold": finding.get("threshold"),
                "suggested_action": finding.get("suggested_action", ""),
                "status": "active",
            }
            alerts.append(alert)
            self._last_alert_times[key] = current_time
            logger.warning("NEXUS alert [%s]: %s", alert["severity"], alert["message"])

        if error_count >= repeated_threshold:
            key = "log_error:threshold_exceeded"
            last_time = self._last_alert_times.get(key)
            if last_time is None or (current_time - last_time) >= self.cooldown_seconds:
                alert = {
                    "id": f"ALT-{uuid.uuid4().hex[:8].upper()}",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "type": "log_error",
                    "severity": "medium",
                    "message": f"Log file contains {error_count} error entries, exceeding threshold {repeated_threshold}.",
                    "value": error_count,
                    "threshold": repeated_threshold,
                    "suggested_action": "Inspect log stream to identify root cause of repeated errors.",
                    "status": "active",
                }
                alerts.append(alert)
                self._last_alert_times[key] = current_time
                logger.warning("NEXUS alert [%s]: %s", alert["severity"], alert["message"])

        return alerts


def create_alerts(
    findings: list[dict[str, Any]],
    error_count: int = 0,
    repeated_threshold: int = 3,
) -> list[dict[str, Any]]:
    """Stateless alert creation maintaining backward compatibility."""
    manager = AlertManager(cooldown_seconds=0.0)
    return manager.process_findings(findings, error_count, repeated_threshold)