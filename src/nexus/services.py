"""Shared application service used by both CLI and REST API."""

from datetime import UTC, datetime

from nexus.alerts.engine import create_alerts
from nexus.analytics.health_score import calculate_health
from nexus.anomaly.detector import AnomalyDetector
from nexus.core.config import Config
from nexus.database.repository import Repository
from nexus.diagnostics.engine import diagnose
from nexus.monitoring.processes import collect_processes
from nexus.monitoring.system import collect_metrics, collect_system_info


class NexusService:
    def __init__(self, config: Config | None = None, repository: Repository | None = None) -> None:
        self.config = config or Config()
        self.config.validate()
        self.repository = repository or Repository(self.config.app["database_path"])
        self.anomaly_detector = AnomalyDetector(
            self.config.thresholds["resource_spike_delta"], int(self.config.thresholds["repeated_log_errors"])
        )

    def info(self) -> dict:
        return collect_system_info()

    def metrics(self) -> dict:
        return collect_metrics()

    def processes(self, sort_by: str = "cpu", limit: int | None = None) -> list[dict]:
        return collect_processes(limit or int(self.config.monitoring["process_limit"]), sort_by)

    def inspect(self, error_messages: list[str] | None = None) -> dict:
        metrics = self.metrics()
        processes = self.processes()
        health = calculate_health(
            metrics,
            self.config.health_weights,
            {key: self.config.thresholds[f"{key}_warning"] for key in ("cpu", "memory", "disk")},
            self.config.health_thresholds,
        )
        findings = diagnose(metrics, processes, self.config.thresholds)
        anomalies = self.anomaly_detector.inspect(metrics, error_messages)
        alerts = create_alerts(findings, len(error_messages or []), int(self.config.thresholds["repeated_log_errors"]))
        self.repository.save_snapshot(metrics, health, findings, anomalies, alerts)
        return {"system": self.info(), "metrics": metrics, "processes": processes, "health": health,
                "diagnostics": findings, "anomalies": anomalies, "alerts": alerts,
                "recommendations": health["recommendations"]}

    def alerts(self) -> list[dict]:
        return self.repository.recent("alerts")

    def diagnostics(self) -> list[dict]:
        return self.repository.recent("diagnostics")

    def reports(self) -> list[dict]:
        return self.repository.recent("snapshots")

    def record_log_analysis(self, summary: dict) -> list[dict]:
        """Persist log-error alerts and recurring-error anomaly records."""
        count = int(summary.get("error_count", 0))
        alerts = create_alerts([], count, int(self.config.thresholds["repeated_log_errors"]))
        anomalies = [
            {"timestamp": datetime.now(UTC).isoformat(), "type": "repeated_error",
             "severity": "medium", "description": item["message"], "value": item["count"]}
            for item in summary.get("recurring_errors", [])
        ]
        self.repository.save_events("alerts", alerts)
        self.repository.save_events("anomalies", anomalies)
        return alerts