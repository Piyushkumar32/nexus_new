# Roadmap

## Available in the first version

- On-demand cross-platform resource and process inspection.
- Configurable resource warnings, weighted health scoring, deterministic diagnostics, and basic resource-spike/repeated-error detection.
- Plain-text log severity and recurrence summaries.
- Local SQLite history, JSON/HTML/CSV reports, Typer CLI, and FastAPI read endpoints.

## Next

- Persistent baseline-aware anomaly analysis and configurable rule severity/action policies.
- Bounded history retention and database migration/version strategy.
- Dedicated service lifecycle for API deployments, authentication options, and access controls.
- Better sampling windows for per-process CPU measurements and platform-specific sensor support.
- Optional charts and longitudinal reporting, using plotting/data packages only when requested.

## Not in scope for the initial local-first release

Cloud telemetry, paid notification services, machine-learning claims, and a web frontend.