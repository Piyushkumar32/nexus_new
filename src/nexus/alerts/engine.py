"""Convert diagnostic findings to locally logged alerts."""

import logging
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


def create_alerts(findings: list[dict], error_count: int = 0, repeated_threshold: int = 3) -> list[dict]:
    alerts = [{**finding, "type": finding["category"], "message": finding["description"]} for finding in findings]
    if error_count >= repeated_threshold:
        alerts.append({"timestamp": datetime.now(UTC).isoformat(), "type": "log_error",
                   "severity": "medium", "message": f"Log contains {error_count} errors."})
    for alert in alerts:
        logger.warning("NEXUS alert [%s]: %s", alert["severity"], alert["message"])
    return alerts