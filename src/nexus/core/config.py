"""Validated configuration loading for NEXUS."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Config:
    app: dict[str, Any] = field(default_factory=lambda: {
        "name": "NEXUS", "database_path": "~/.nexus/nexus.db", "report_directory": "./reports"
    })
    monitoring: dict[str, Any] = field(default_factory=lambda: {
        "interval_seconds": 2, "process_limit": 20
    })
    thresholds: dict[str, float] = field(default_factory=lambda: {
        "cpu_warning": 80, "memory_warning": 85, "disk_warning": 90,
        "process_cpu_warning": 80, "process_memory_warning": 20,
        "repeated_log_errors": 3, "resource_spike_delta": 25,
    })
    health_weights: dict[str, float] = field(default_factory=lambda: {
        "cpu": 0.35, "memory": 0.35, "disk": 0.30
    })
    health_thresholds: dict[str, float] = field(default_factory=lambda: {"healthy": 80, "degraded": 60})
    logging: dict[str, Any] = field(default_factory=lambda: {
        "level": "INFO", "file": "~/.nexus/nexus.log"
    })

    @classmethod
    def load(cls, path: str | Path | None = None) -> Config:
        """Load YAML settings, falling back to defaults when no file is supplied."""
        if path is None:
            return cls()
        config_path = Path(path).expanduser()
        try:
            raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except OSError as exc:
            raise ValueError(f"Cannot read configuration {config_path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ValueError("Configuration root must be a YAML mapping")
        defaults = cls()
        values = {}
        for key in defaults.__dataclass_fields__:
            default_value = getattr(defaults, key)
            supplied = raw.get(key, {})
            if isinstance(default_value, dict) and isinstance(supplied, dict):
                values[key] = {**default_value, **supplied}
            else:
                values[key] = supplied if key in raw else default_value
        config = cls(**values)
        config.validate()
        return config

    def validate(self) -> None:
        """Reject invalid intervals, limits, thresholds, and health weights."""
        for name in ("app", "monitoring", "thresholds", "health_weights", "health_thresholds", "logging"):
            if not isinstance(getattr(self, name), dict):
                raise ValueError(f"{name} must be a YAML mapping")
        for key in ("name", "database_path", "report_directory"):
            if not isinstance(self.app.get(key), str) or not self.app[key].strip():
                raise ValueError(f"app.{key} must be a non-empty string")
        if self.logging.get("level", "INFO") not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("logging.level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
        log_file = self.logging.get("file")
        if log_file is not None and not isinstance(log_file, str):
            raise ValueError("logging.file must be a path string or null")
        interval = self.monitoring.get("interval_seconds")
        if not isinstance(interval, (int, float)) or not isfinite(interval) or interval <= 0:
            raise ValueError("monitoring.interval_seconds must be greater than zero")
        process_limit = self.monitoring.get("process_limit")
        if not isinstance(process_limit, int) or isinstance(process_limit, bool) or process_limit < 1:
            raise ValueError("monitoring.process_limit must be at least one")
        for key, value in self.thresholds.items():
            if not isinstance(value, (int, float)) or not isfinite(value) or not 0 <= value <= 100:
                raise ValueError(f"thresholds.{key} must be between 0 and 100")
        if set(self.health_weights) != {"cpu", "memory", "disk"}:
            raise ValueError("health_weights must define cpu, memory, and disk")
        if any(not isinstance(value, (int, float)) or not isfinite(value) for value in self.health_weights.values()):
            raise ValueError("health_weights values must be finite numbers")
        if (any(value < 0 for value in self.health_weights.values())
            or sum(self.health_weights.values()) <= 0):
            raise ValueError("health_weights must be non-negative with a positive total")
        if set(self.health_thresholds) != {"healthy", "degraded"}:
            raise ValueError("health_thresholds must define healthy and degraded")
        if any(not isinstance(value, (int, float)) or not isfinite(value)
               for value in self.health_thresholds.values()):
            raise ValueError("health_thresholds values must be finite numbers")
        if not 0 <= self.health_thresholds["degraded"] <= self.health_thresholds["healthy"] <= 100:
            raise ValueError("health_thresholds must satisfy 0 <= degraded <= healthy <= 100")