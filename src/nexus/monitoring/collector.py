"""System metrics collector coordination."""

from __future__ import annotations

from typing import Any

from nexus.monitoring.cpu import collect_cpu
from nexus.monitoring.disk import collect_disk_io, collect_disks
from nexus.monitoring.memory import collect_memory
from nexus.monitoring.network import collect_network
from nexus.monitoring.processes import collect_processes
from nexus.monitoring.system import collect_metrics, collect_system_info


class MetricsCollector:
    """Consolidated collector for system intelligence snapshots."""

    def __init__(self, process_limit: int = 20) -> None:
        self.process_limit = process_limit

    def snapshot(self) -> dict[str, Any]:
        return {
            "system": collect_system_info(),
            "metrics": collect_metrics(),
            "processes": collect_processes(limit=self.process_limit),
        }

    def collect_cpu(self) -> dict[str, Any]:
        return collect_cpu()

    def collect_memory(self) -> dict[str, Any]:
        return collect_memory()

    def collect_disk(self) -> dict[str, Any]:
        return {"disks": collect_disks(), "io": collect_disk_io()}

    def collect_network(self) -> dict[str, Any]:
        return collect_network()

    def collect_processes(self, sort_by: str = "cpu", limit: int | None = None) -> list[dict[str, Any]]:
        return collect_processes(limit=limit or self.process_limit, sort_by=sort_by)