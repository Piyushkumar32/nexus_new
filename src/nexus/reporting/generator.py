"""Build and export a complete point-in-time report."""

from datetime import datetime, timezone

from nexus.reporting.exporters import export_report


def build_report(bundle: dict) -> dict:
    return {"generated_at": datetime.now(timezone.utc).isoformat(), **bundle}


def generate_report(bundle: dict, path: str, format: str | None = None):
    return export_report(build_report(bundle), path, format)