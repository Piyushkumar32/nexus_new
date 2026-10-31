# NEXUS Architecture

NEXUS separates host sampling, analysis, persistence, and presentation. It is local-first: the application has no remote telemetry dependency.

## Components

- `monitoring/`: psutil-based system, CPU, memory, disk, and process collectors; OS-only details use the Python standard library.
- `core/`: YAML configuration validation and local logging setup.
- `analytics/`, `diagnostics/`, `anomaly/`, `alerts/`: deterministic scoring and explainable rules.
- `logs/`: resilient line parsing and aggregate log analysis.
- `database/`: isolated SQLite schema and parameterized repository operations.
- `reporting/`: report assembly and JSON, escaped HTML, and CSV exporters.
- `services.py`: shared use-case orchestration consumed by CLI and HTTP routes.
- `cli/`: Typer commands and Rich tables.
- `api/`: FastAPI app factory, Pydantic response contracts, and service-backed routes.

## Data flow

```text
psutil collectors -> NexusService -> health / diagnostics / anomalies / alerts
                                  -> SQLite repository
                                  -> CLI output / report exporters / REST API
```

Every `inspect` operation captures a resource snapshot and persists it with its health score and generated events. Process collection skips access-denied or exited processes. Disk mounts that cannot be read are omitted. API diagnostics and alert endpoints return persisted history; `/health` is a liveness check.

## Boundaries and limitations

Sampling is on demand except for CLI `monitor --watch`. Process CPU percentages are psutil's instantaneous values and may be zero on an initial sample. Anomaly comparisons and repeated-error counters are in memory for the lifetime of one service instance; persisted anomaly records remain queryable. The API has no authentication and should stay on loopback or behind an appropriately secured boundary.