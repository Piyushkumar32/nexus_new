"""Report exporters with professional HTML styling and charts."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any


def export_report(report: dict[str, Any], path: str | Path, format: str | None = None) -> Path:
    destination = Path(path).expanduser()
    kind = (format or destination.suffix.lstrip(".") or "json").lower()
    destination.parent.mkdir(parents=True, exist_ok=True)

    if kind == "json":
        destination.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    elif kind == "html":
        destination.write_text(_render_html(report), encoding="utf-8")
    elif kind == "csv":
        with destination.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["section", "key", "value"])
            for section, values in report.items():
                if isinstance(values, dict):
                    writer.writerows((section, k, v) for k, v in values.items())
                elif isinstance(values, list):
                    for item in values:
                        writer.writerow([section, "", json.dumps(item, default=str)])
                else:
                    writer.writerow([section, "", json.dumps(values, default=str)])
    else:
        raise ValueError("Report format must be json, html, or csv")
    return destination


def _render_html(report: dict[str, Any]) -> str:
    generated_at = report.get("generated_at", "Unknown")
    health = report.get("health", {})
    score = health.get("score", 100)
    classification = health.get("classification", "healthy").upper()
    system = report.get("system", {})
    metrics = report.get("metrics", {})
    cpu = metrics.get("cpu", {})
    mem = metrics.get("memory", {})
    findings = report.get("diagnostics", [])
    anomalies = report.get("anomalies", [])
    recs = report.get("recommendations", [])

    score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"

    findings_rows = ""
    for f in findings:
        sev_color = "#ef4444" if f.get("severity") in ("critical", "high") else "#f59e0b"
        findings_rows += f"""<tr>
            <td><span style='background:{sev_color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;'>{html.escape(str(f.get('severity', '')))}</span></td>
            <td>{html.escape(str(f.get('category', '')))}</td>
            <td>{html.escape(str(f.get('description', '')))}</td>
            <td>{html.escape(str(f.get('value', '')))}</td>
            <td>{html.escape(str(f.get('suggested_action', '')))}</td>
        </tr>"""
    if not findings_rows:
        findings_rows = "<tr><td colspan='5' style='text-align:center;color:#6b7280;'>No diagnostic issues found.</td></tr>"

    recs_list = "".join(f"<li>{html.escape(str(r))}</li>" for r in recs) or "<li>System is operating stably.</li>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NEXUS Diagnostic Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }}
  .header h1 {{ margin: 0; font-size: 24px; color: #38bdf8; }}
  .card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #1e293b; border-radius: 8px; padding: 18px; border: 1px solid #334155; }}
  .card h3 {{ margin-top: 0; font-size: 14px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; }}
  .metric-large {{ font-size: 36px; font-weight: bold; margin: 8px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; background: #1e293b; border-radius: 8px; overflow: hidden; }}
  th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }}
  th {{ background: #0f172a; color: #94a3b8; }}
  ul {{ margin: 8px 0 0 20px; padding: 0; }}
  li {{ margin-bottom: 6px; line-height: 1.5; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>NEXUS System Intelligence Report</h1>
      <small style="color:#94a3b8">Host: {html.escape(str(system.get("hostname", "Unknown")))} ({html.escape(str(system.get("os", "")))} {html.escape(str(system.get("os_version", "")))} )</small>
    </div>
    <div style="text-align:right">
      <small style="color:#94a3b8">Generated: {html.escape(str(generated_at))}</small>
    </div>
  </div>

  <div class="card-grid">
    <div class="card">
      <h3>Health Score</h3>
      <div class="metric-large" style="color:{score_color}">{score} / 100</div>
      <div style="color:{score_color};font-weight:600;">{classification}</div>
    </div>
    <div class="card">
      <h3>CPU Utilization</h3>
      <div class="metric-large">{cpu.get('percent', 0.0):.1f}%</div>
      <small style="color:#94a3b8">{cpu.get('logical_cores', 0)} Cores | {cpu.get('frequency_mhz', 'N/A')} MHz</small>
    </div>
    <div class="card">
      <h3>Memory Pressure</h3>
      <div class="metric-large">{mem.get('percent', 0.0):.1f}%</div>
      <small style="color:#94a3b8">{round(mem.get('used_bytes', 0) / (1024**3), 1)} GB / {round(mem.get('total_bytes', 0) / (1024**3), 1)} GB</small>
    </div>
    <div class="card">
      <h3>Active Anomalies</h3>
      <div class="metric-large" style="color:{'#ef4444' if len(anomalies) > 0 else '#10b981'}">{len(anomalies)}</div>
      <small style="color:#94a3b8">{len(findings)} Diagnostic findings</small>
    </div>
  </div>

  <div class="card" style="margin-bottom: 24px;">
    <h3>Actionable Recommendations</h3>
    <ul>{recs_list}</ul>
  </div>

  <div class="card">
    <h3>Diagnostic Findings</h3>
    <table>
      <thead>
        <tr><th>Severity</th><th>Category</th><th>Description</th><th>Observed</th><th>Action</th></tr>
      </thead>
      <tbody>
        {findings_rows}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>"""