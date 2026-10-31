"""Report exporters with escaped HTML and CSV output."""

import csv
import html
import json
from pathlib import Path


def export_report(report: dict, path: str | Path, format: str | None = None) -> Path:
    destination = Path(path).expanduser()
    kind = (format or destination.suffix.lstrip(".") or "json").lower()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if kind == "json":
        destination.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    elif kind == "html":
        rows = "".join(f"<tr><th>{html.escape(str(key))}</th><td><pre>{html.escape(json.dumps(value, indent=2, default=str))}</pre></td></tr>"
                       for key, value in report.items())
        destination.write_text(f"<!doctype html><meta charset='utf-8'><title>NEXUS report</title>"
                               f"<h1>NEXUS Diagnostic Report</h1><table>{rows}</table>", encoding="utf-8")
    elif kind == "csv":
        with destination.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["section", "key", "value"])
            for section, values in report.items():
                if isinstance(values, dict):
                    writer.writerows((section, key, value) for key, value in values.items())
                else:
                    writer.writerow([section, "", json.dumps(values, default=str)])
    else:
        raise ValueError("Report format must be json, html, or csv")
    return destination