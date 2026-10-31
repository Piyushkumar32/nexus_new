# NEXUS REST API Documentation

The NEXUS REST API exposes system observability, health diagnostics, anomalies, alerts, and snapshots over HTTP.
By default, the server binds to 127.0.0.1:8000 to prevent unintended public exposure.

## Starting the API Server

```bash
nexus api start --host 127.0.0.1 --port 8000
```

Interactive OpenAPI documentation is automatically served at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Healthcheck and service heartbeat |
| `GET` | `/api/v1/system/info` | Host information, OS, CPU model, RAM, uptime |
| `GET` | `/api/v1/system/metrics` | Consolidated metrics snapshot (CPU, memory, disk, network) |
| `GET` | `/api/v1/system/cpu` | CPU utilization percentage, per-core breakdown, and load averages |
| `GET` | `/api/v1/system/memory` | RAM and swap usage, available memory, health flag |
| `GET` | `/api/v1/system/disk` | Partition usage, mountpoints, free space, and disk I/O |
| `GET` | `/api/v1/system/network` | Total throughput, packet counters, and network interface status |
| `GET` | `/api/v1/system/processes` | Running processes sorted by `cpu` or `memory` (query params: `sort_by`, `limit`) |
| `GET` | `/api/v1/diagnostics` | Diagnostic findings with severity, categories, and suggested actions |
| `GET` | `/api/v1/anomalies` | Historical resource spikes and recurring log error anomalies |
| `GET` | `/api/v1/alerts` | Active and historical alerts with deduplication |
| `GET` | `/api/v1/reports` | List of historical system snapshots stored in SQLite |
