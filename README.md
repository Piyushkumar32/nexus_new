# NEXUS — System Intelligence & Diagnostic Engine

NEXUS is a local-first Python CLI and diagnostics platform for inspecting system resources, identifying common bottlenecks, analyzing plain-text logs, and saving portable reports. Measurements come from the host through `psutil`; NEXUS does not use machine learning or send telemetry to a service.

## Capabilities

- Cross-platform host, CPU, memory, swap, disk and process inventory.
- Configurable thresholds, weighted health score, actionable diagnostic findings, and simple explainable spike/repeated-error detection.
- Plain-text log severity counts, timestamp parsing, malformed-line accounting, and recurring error summaries.
- Local terminal alerts and SQLite history for snapshots, scores, diagnostics, anomalies and alerts.
- JSON, HTML and CSV report exports; a FastAPI read API sharing the CLI service layer.
- Rich and Typer terminal commands with optional live metric refresh.

## Installation

Requires Python 3.12 or newer on Windows, Linux or macOS.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

On Linux/macOS, activate with `source .venv/bin/activate` instead. The editable install exposes the `nexus` command.

## CLI

```text
nexus --help
nexus info
nexus monitor
nexus monitor --watch --interval 2
nexus health
nexus processes --sort memory --limit 15
nexus diagnose
nexus logs analyze ./application.log
nexus report --output ./reports/current.html
nexus alerts
```

Pass `--config config/default.yaml` before a command to use a YAML file. Running `health`, `diagnose`, or `report` captures and persists a fresh snapshot. The database defaults to `~/.nexus/nexus.db`; process CPU values are instantaneous samples and can initially be zero.

## REST API

Start the API with `uvicorn nexus.api.app:app --app-dir src --host 127.0.0.1 --port 8000`. The API is intended for local use; no authentication is provided, so do not expose it to untrusted networks.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | API liveness |
| GET | `/system/info` | Host information |
| GET | `/system/metrics` | CPU, memory and disk snapshot |
| GET | `/system/processes?sort_by=cpu&limit=20` | Process inventory (`cpu` or `memory`) |
| GET | `/diagnostics` | Persisted diagnostic history |
| GET | `/alerts` | Persisted alert history |
| GET | `/reports` | Recent saved metric snapshots |

Interactive API documentation is available at `/docs`.

## Configuration

`config/default.yaml` documents defaults for monitoring cadence, output paths, resource and process thresholds, anomaly detection, scoring weights, and local logging. NEXUS validates the interval, process limit, threshold ranges, and non-negative scoring weights when loading configuration.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for module responsibilities and data flow. SQLite is the only persistence dependency; reports are ordinary local files.

## Development and tests

```text
python -m pytest
ruff check .
```

System calls are isolated in `monitoring/` and can be mocked in tests. API and CLI tests use temporary configuration/database paths.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md). The initial release intentionally focuses on local snapshots and rule-based diagnostics; it does not offer a background daemon, remote notification integrations, or long-term trend visualization.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please include tests for behavioral changes and keep platform-specific metrics optional.

## License

MIT; see [LICENSE](LICENSE).
