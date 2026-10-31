from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from nexus.alerts.engine import create_alerts
from nexus.analytics.health_score import calculate_health
from nexus.anomaly.detector import AnomalyDetector
from nexus.api.app import create_app
from nexus.cli.commands import app
from nexus.core.config import Config
from nexus.database.repository import Repository
from nexus.diagnostics.engine import diagnose
from nexus.logs.analyzer import analyze_log
from nexus.logs.parser import parse_line
from nexus.monitoring import cpu, disk, memory, processes
from nexus.reporting.exporters import export_report


def test_config_defaults_and_validation(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("monitoring:\n  interval_seconds: 0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="interval_seconds"):
        Config.load(path)
    assert Config().monitoring["interval_seconds"] > 0


def test_config_valid_yaml(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("thresholds:\n  cpu_warning: 70\n", encoding="utf-8")
    assert Config.load(path).thresholds["cpu_warning"] == 70
    assert Config.load(path).thresholds["memory_warning"] == 85


def test_cpu_collector(monkeypatch):
    monkeypatch.setattr(cpu.psutil, "cpu_freq", lambda: SimpleNamespace(current=2400.0))
    monkeypatch.setattr(cpu.psutil, "cpu_percent", lambda interval, **kwargs: [10.0, 20.0] if kwargs else 15.0)
    monkeypatch.setattr(cpu.psutil, "cpu_count", lambda logical: 8 if logical else 4)
    result = cpu.collect_cpu(0)
    assert result["percent"] == 15.0
    assert result["logical_cores"] == 8 and result["physical_cores"] == 4
    assert result["frequency_mhz"] == 2400.0


def test_memory_collector(monkeypatch):
    monkeypatch.setattr(memory.psutil, "virtual_memory", lambda: SimpleNamespace(
        total=1000, used=700, available=300, percent=70.0
    ))
    monkeypatch.setattr(memory.psutil, "swap_memory", lambda: SimpleNamespace(
        total=500, used=100, percent=20.0
    ))
    result = memory.collect_memory()
    assert result["available_bytes"] == 300 and result["swap_percent"] == 20.0
    assert result["health"] == "healthy"


def test_disk_collector_skips_inaccessible_mount(monkeypatch):
    monkeypatch.setattr(disk.psutil, "disk_partitions", lambda all: [
        SimpleNamespace(device="one", mountpoint="/ok", fstype="ext4"),
        SimpleNamespace(device="two", mountpoint="/nope", fstype="ext4"),
    ])

    def usage(path):
        if path == "/nope":
            raise PermissionError("denied")
        return SimpleNamespace(total=100, used=25, free=75, percent=25.0)

    monkeypatch.setattr(disk.psutil, "disk_usage", usage)
    result = disk.collect_disks()
    assert len(result) == 1 and result[0]["free_bytes"] == 75


def test_process_collector_sorts_and_skips_access_denied(monkeypatch):
    good = SimpleNamespace(
        info={"pid": 1, "name": "worker", "status": "running", "create_time": 1.0, "memory_percent": 2.0},
        cpu_percent=lambda interval=None: 30.0,
    )
    denied = SimpleNamespace(
        info={"pid": 2, "name": "private", "status": "running", "create_time": None, "memory_percent": 0},
        cpu_percent=lambda interval=None: (_ for _ in ()).throw(processes.psutil.AccessDenied()),
    )
    monkeypatch.setattr(processes.psutil, "process_iter", lambda **kwargs: iter([good, denied]))
    result = processes.collect_processes(5, "cpu")
    assert len(result) == 1 and result[0]["cpu_percent"] == 30.0
    assert result[0]["running_seconds"] is not None


def test_health_score_and_recommendations():
    result = calculate_health({"cpu": {"percent": 90}, "memory": {"percent": 50}, "disks": [{"percent": 70}]})
    assert result["score"] == 30
    assert result["classification"] == "critical"
    assert any("cpu" in item for item in result["recommendations"])


def test_diagnostic_threshold_rules():
    metrics = {"cpu": {"percent": 91}, "memory": {"percent": 20}, "disks": [{"mountpoint": "/x", "percent": 95}]}
    results = diagnose(metrics, [], {"cpu_warning": 80, "memory_warning": 85, "disk_warning": 90,
                                    "process_cpu_warning": 80, "process_memory_warning": 20})
    assert {item["category"] for item in results} == {"cpu", "disk"}


def test_anomaly_spikes_and_repeat_errors():
    detector = AnomalyDetector(spike_delta=20, repeated_errors=2)
    base = {"cpu": {"percent": 10}, "memory": {"percent": 10}, "disks": []}
    detector.inspect(base, ["same"])
    updated = {"cpu": {"percent": 40}, "memory": {"percent": 10}, "disks": []}
    results = detector.inspect(updated, ["same"])
    assert {item["type"] for item in results} == {"resource_spike", "repeated_error"}
    assert len(detector.history) == 2


def test_parse_log_timestamp_severity_and_malformed():
    parsed = parse_line("2026-10-31T12:00:00Z ERROR disk full", 4)
    assert parsed["severity"] == "ERROR" and parsed["timestamp"].endswith("+00:00")
    assert parse_line("unstructured text")["malformed"] is True


def test_log_analysis_counts_recurring_and_malformed(tmp_path):
    path = tmp_path / "app.log"
    path.write_text("ERROR failed\nERROR failed\nINFO ready\nnot structured\n", encoding="utf-8")
    summary = analyze_log(path, recurring_limit=2)
    assert summary["error_count"] == 2
    assert summary["malformed_count"] == 1
    assert summary["recurring_errors"] == [{"message": "ERROR failed", "count": 2}]


def test_log_recurrence_ignores_changing_timestamps(tmp_path):
    path = tmp_path / "timed.log"
    path.write_text(
        "2026-10-31T12:00:00Z ERROR disk unavailable\n"
        "2026-10-31T12:01:00Z ERROR disk unavailable\n",
        encoding="utf-8",
    )
    assert analyze_log(path, recurring_limit=2)["recurring_errors"][0]["count"] == 2


def test_alert_generation():
    alerts = create_alerts([{"category": "cpu", "severity": "high", "description": "hot"}], 3, 3)
    assert len(alerts) == 2
    assert alerts[1]["type"] == "log_error"


def test_repository_roundtrip_and_allowlist(tmp_path):
    repo = Repository(tmp_path / "state.db")
    snapshot = {"captured_at": 1.0, "cpu": {"percent": 1}}
    health = {"score": 99}
    repo.save_snapshot(snapshot, health, [{"timestamp": "now", "category": "cpu"}], [], [])
    assert repo.recent("snapshots") == [snapshot]
    assert repo.recent("health_scores")[0]["score"] == 99
    with pytest.raises(ValueError):
        repo.recent("snapshots; DROP TABLE alerts")


@pytest.mark.parametrize("format,suffix", [("json", ".json"), ("html", ".html"), ("csv", ".csv")])
def test_report_export_formats(tmp_path, format, suffix):
    output = export_report({"health": {"score": 88}}, tmp_path / f"report{suffix}", format)
    assert output.exists() and output.stat().st_size
    if format == "json":
        assert json.loads(output.read_text(encoding="utf-8"))["health"]["score"] == 88


def test_api_health_and_read_endpoints(tmp_path):
    config = Config(app={"name": "NEXUS", "database_path": str(tmp_path / "api.db"), "report_directory": str(tmp_path)})
    client = TestClient(create_app(__import__("nexus.services", fromlist=["NexusService"]).NexusService(config)))
    assert client.get("/health").status_code == 200
    assert client.get("/system/info").json()["data"]["hostname"]
    assert client.get("/system/metrics").json()["data"]["cpu"]["percent"] >= 0
    assert client.get("/system/processes?sort_by=memory&limit=2").status_code == 200
    assert client.get("/system/processes?sort_by=bad").status_code == 400
    assert client.get("/diagnostics").status_code == 200
    assert client.get("/alerts").status_code == 200
    assert client.get("/reports").status_code == 200


def test_cli_help_and_info(tmp_path):
    runner = CliRunner()
    assert runner.invoke(app, ["--help"]).exit_code == 0
    config = tmp_path / "cli.yaml"
    config.write_text(f"app:\n  name: NEXUS\n  database_path: '{tmp_path / 'cli.db'}'\n  report_directory: '{tmp_path}'\n", encoding="utf-8")
    result = runner.invoke(app, ["--config", str(config), "info"])
    assert result.exit_code == 0, result.output
    assert "System Information" in result.output
    invalid_sort = runner.invoke(app, ["processes", "--sort", "network"])
    assert invalid_sort.exit_code == 2


def test_all_cli_commands(tmp_path):
    runner = CliRunner()
    config = tmp_path / "cli.yaml"
    config.write_text(
        f"app:\n  name: NEXUS\n  database_path: '{tmp_path / 'commands.db'}'\n"
        f"  report_directory: '{tmp_path}'\nlogging:\n  file: null\n",
        encoding="utf-8",
    )
    log_file = tmp_path / "sample.log"
    log_file.write_text("ERROR failed\nERROR failed\n", encoding="utf-8")
    commands = [
        ["monitor"], ["health"], ["processes", "--sort", "memory", "--limit", "2"],
        ["diagnose"], ["logs", "analyze", str(log_file)],
        ["report", "--output", str(tmp_path / "report.json")], ["alerts"],
    ]
    for command in commands:
        result = runner.invoke(app, ["--config", str(config), *command])
        assert result.exit_code == 0, f"{command}: {result.output}"
    assert (tmp_path / "report.json").exists()