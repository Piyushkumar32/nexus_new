# NEXUS — System Intelligence & Diagnostic Engine

NEXUS is a local-first Python CLI and diagnostics platform for inspecting system resources, identifying bottlenecks, analyzing plain-text logs, and exporting executive reports. Built with transparent, explainable algorithms and cross-platform compatibility.

[![CI](https://github.com/Piyushkumar32/nexus_new/actions/workflows/ci.yml/badge.svg)](https://github.com/Piyushkumar32/nexus_new/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Core Capabilities

- **System Observability**: Comprehensive CPU, memory, disk, network throughput, and running process inventory.
- **Explainable Health Scoring**: Deterministic 0–100 health evaluation with configurable component weights and threshold warnings.
- **Root-Cause Diagnostics**: Rule-based detection of resource bottlenecks, storage saturation, and rogue processes with concrete remediation actions.
- **Streaming Log Intelligence**: Fast line-by-line parsing of local log files with severity distribution analysis and recurring error grouping without memory bloat.
- **Anomaly Detection**: Detection of sudden resource spikes and recurring error patterns with historical context.
- **Alert Suppression & Deduplication**: Smart alert engine with cooldown windows to avoid alert fatigue.
- **Local Persistence**: Zero-setup SQLite persistence (WAL mode) for snapshots, health history, diagnostics, and reports.
- **Executive Reporting**: High-quality HTML dashboards, JSON bundles, and CSV tables.
- **Dual Interfaces**: Interactive terminal interface (`Typer` + `Rich`) and local REST API (`FastAPI` + `Uvicorn`).

## Installation

```bash
git clone https://github.com/Piyushkumar32/nexus_new.git
cd nexus_new
python -m venv .venv
# Activate environment:
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -e .[dev]
```

## Quick Start (CLI)

```bash
# Host system overview
nexus info

# Point-in-time metrics
nexus monitor

# Continuous live-updating monitor
nexus monitor --watch

# System health assessment
nexus health

# Process inventory
nexus processes --sort cpu --limit 10

# System diagnostics & recommendations
nexus diagnose

# Analyze application logs
nexus logs analyze /path/to/logfile.log

# Generate executive HTML report
nexus reports generate -o executive_report.html

# Start local REST API
nexus api start --port 8000
```

## REST API

When the API server is active (`nexus api start`), interactive documentation is available:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

Core endpoints include:
- `GET /health`
- `GET /api/v1/system/info`
- `GET /api/v1/system/metrics`
- `GET /api/v1/system/cpu`
- `GET /api/v1/system/memory`
- `GET /api/v1/system/disk`
- `GET /api/v1/system/network`
- `GET /api/v1/system/processes`
- `GET /api/v1/diagnostics`
- `GET /api/v1/anomalies`
- `GET /api/v1/alerts`
- `GET /api/v1/reports`

## Testing & Quality

```bash
pytest tests
ruff check src tests
```

## Documentation

Detailed guides are available in the [`docs/`](docs/) directory:
- [Architecture](docs/ARCHITECTURE.md)
- [CLI Reference](docs/CLI.md)
- [REST API Reference](docs/API.md)
- [Configuration](docs/CONFIGURATION.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Testing Guide](docs/TESTING.md)
- [Roadmap](docs/ROADMAP.md)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
