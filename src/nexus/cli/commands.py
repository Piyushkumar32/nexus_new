"""NEXUS CLI commands with Rich terminal output."""

from __future__ import annotations

import time
from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from nexus.api.app import create_app
from nexus.core.config import Config
from nexus.core.logging import configure_logging
from nexus.logs.analyzer import analyze_log
from nexus.reporting.generator import generate_report
from nexus.services import NexusService

app = typer.Typer(help="NEXUS — local system intelligence and diagnostics.", no_args_is_help=True)
logs_app = typer.Typer(help="Analyze local log files.", no_args_is_help=True)
reports_app = typer.Typer(help="Manage and export diagnostic reports.", no_args_is_help=True)
api_app = typer.Typer(help="Run local diagnostic REST API.", no_args_is_help=True)
config_app = typer.Typer(help="Inspect and validate configuration.", no_args_is_help=True)

app.add_typer(logs_app, name="logs")
app.add_typer(reports_app, name="reports")
app.add_typer(api_app, name="api")
app.add_typer(config_app, name="config")

console = Console()


@app.callback()
def initialize(
    ctx: typer.Context,
    config: Path | None = typer.Option(None, "--config", help="YAML configuration file."),
) -> None:
    try:
        settings = Config.load(config)
        configure_logging(settings.logging.get("level", "INFO"), settings.logging.get("file"))
        ctx.obj = {"config": settings}
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def get_service(ctx: typer.Context) -> NexusService:
    if "service" not in ctx.obj:
        ctx.obj["service"] = NexusService(ctx.obj["config"])
    return ctx.obj["service"]


def inspect_with_status(ctx: typer.Context) -> dict:
    with console.status("Collecting system metrics and analyzing health…", spinner="dots"):
        return get_service(ctx).inspect()


def display_mapping(title: str, values: dict) -> None:
    table = Table(title=title, header_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    for key, value in values.items():
        table.add_row(key.replace("_", " ").title(), str(value))
    console.print(table)


def display_findings(findings: list[dict], title: str = "Findings") -> None:
    table = Table(title=title, header_style="bold cyan")
    for column in ("Severity", "Category", "Description", "Value", "Threshold", "Action"):
        table.add_column(column, overflow="fold")
    for item in findings:
        table.add_row(
            item.get("severity", "info"),
            item.get("category", item.get("type", "")),
            item.get("description", item.get("message", "")),
            str(item.get("value", "")),
            str(item.get("threshold", "")),
            item.get("suggested_action", ""),
        )
    if not findings:
        table.add_row("green", "—", "No findings.", "—", "—", "—")
    console.print(table)


@app.command()
def info(ctx: typer.Context) -> None:
    """Display operating system and host information."""
    display_mapping("System Information", get_service(ctx).info())


@app.command()
def monitor(
    ctx: typer.Context,
    watch: bool = typer.Option(False, "--watch", help="Refresh continuously until Ctrl+C."),
    interval: float = typer.Option(2.0, min=0.2, help="Refresh interval in seconds."),
) -> None:
    """Show current resource metrics; optionally run a live-refresh monitor."""
    try:
        while True:
            result = inspect_with_status(ctx)
            metrics = result["metrics"]
            console.clear()
            display_mapping("CPU", metrics["cpu"])
            display_mapping("Memory", metrics["memory"])
            disks = Table(title="Disk Usage", header_style="bold cyan")
            disks.add_column("Mount")
            disks.add_column("Used %", justify="right")
            disks.add_column("Free bytes", justify="right")
            for disk in metrics.get("disks", []):
                disks.add_row(disk["mountpoint"], f"{disk['percent']:.1f}", str(disk["free_bytes"]))
            console.print(disks)
            if not watch:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\nMonitoring stopped.")


@app.command()
def health(ctx: typer.Context) -> None:
    """Calculate an explainable system health score."""
    result = inspect_with_status(ctx)
    display_mapping("Health", result["health"])


@app.command()
def processes(
    ctx: typer.Context,
    sort: str = typer.Option("cpu", "--sort", help="Sort by cpu or memory."),
    limit: int = typer.Option(20, min=1, max=500),
) -> None:
    """List processes sorted by CPU or memory consumption."""
    if sort not in {"cpu", "memory"}:
        raise typer.BadParameter("must be either 'cpu' or 'memory'", param_hint="--sort")
    rows = get_service(ctx).processes(sort, limit)
    table = Table(title="Processes", header_style="bold cyan")
    for heading in ("PID", "Name", "CPU %", "Memory %", "Status", "Running"):
        table.add_column(heading)
    for row in rows:
        runtime = row.get("running_seconds")
        running = f"{runtime // 3600}h {(runtime % 3600) // 60}m" if runtime is not None else "—"
        table.add_row(
            str(row.get("pid", "")),
            str(row.get("name") or "—"),
            f"{row.get('cpu_percent') or 0:.1f}",
            f"{row.get('memory_percent') or 0:.1f}",
            str(row.get("status") or "—"),
            running,
        )
    console.print(table)


@app.command()
def diagnose(ctx: typer.Context) -> None:
    """Run resource diagnostics and show findings and recommendations."""
    result = inspect_with_status(ctx)
    display_findings(result["diagnostics"], "Diagnostics")
    console.print("\n[bold]Recommendations[/bold]")
    for item in result["recommendations"]:
        console.print(f"• {item}")


@app.command()
def anomalies(ctx: typer.Context) -> None:
    """Show detected resource and log anomalies."""
    history = get_service(ctx).anomalies()
    display_findings(history, "Historical Anomalies")


@app.command()
def alerts(ctx: typer.Context) -> None:
    """Show locally persisted alert history."""
    display_findings(get_service(ctx).alerts(), "Recent Alerts")


@logs_app.command("analyze")
def logs_analyze(
    ctx: typer.Context,
    file: Path = typer.Argument(..., exists=True, readable=True, help="Plain-text log file."),
) -> None:
    """Analyze severity counts and recurring errors in a log file."""
    try:
        with console.status("Reading and analyzing log file…", spinner="dots"):
            result = analyze_log(file)
        get_service(ctx).record_log_analysis(result)
        display_mapping("Log Summary", {key: value for key, value in result.items() if key != "entries"})
        display_findings(
            [
                {"severity": "medium", "type": "recurring error", "message": item["message"], "value": item["count"]}
                for item in result["recurring_errors"]
            ],
            "Recurring Errors",
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(2) from exc


@reports_app.command("generate")
def reports_generate(
    ctx: typer.Context,
    output: Path = typer.Option(Path("nexus-report.html"), "--output", "-o"),
    format: str | None = typer.Option(None, help="json, html, or csv (defaults to file extension)."),
) -> None:
    """Generate and save an executive diagnostic report."""
    try:
        result = inspect_with_status(ctx)
        payload = {
            "system": result["system"],
            "metrics": result["metrics"],
            "health": result["health"],
            "diagnostics": result["diagnostics"],
            "anomalies": result["anomalies"],
            "recommendations": result["recommendations"],
        }
        path = generate_report(payload, str(output), format)
        get_service(ctx).repository.save_report_meta(
            str(time.time()), format or path.suffix.lstrip("."), str(path), "Executive report"
        )
        console.print(f"Report written to [green]{path}[/green]")
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to generate report: {exc}[/red]")
        raise typer.Exit(2) from exc


@reports_app.command("list")
def reports_list(ctx: typer.Context) -> None:
    """List historical monitoring snapshots and generated reports."""
    rows = get_service(ctx).reports()
    table = Table(title="Historical Snapshots", header_style="bold cyan")
    table.add_column("Timestamp")
    table.add_column("CPU %")
    table.add_column("Memory %")
    table.add_column("Disks")
    for r in rows:
        captured = time.ctime(r.get("captured_at", 0))
        cpu_pct = f"{r.get('cpu', {}).get('percent', 0.0):.1f}%"
        mem_pct = f"{r.get('memory', {}).get('percent', 0.0):.1f}%"
        disks = len(r.get("disks", []))
        table.add_row(captured, cpu_pct, mem_pct, str(disks))
    console.print(table)


# Backward-compatible report command
@app.command("report", hidden=True)
def report_legacy(
    ctx: typer.Context,
    output: Path = typer.Option(Path("nexus-report.json"), "--output", "-o"),
    format: str | None = typer.Option(None, help="json, html, or csv (defaults to file extension)."),
) -> None:
    reports_generate(ctx, output=output, format=format)


@api_app.command("start")
def api_start(
    ctx: typer.Context,
    host: str = typer.Option("127.0.0.1", "--host", help="Host interface to bind to."),
    port: int = typer.Option(8000, "--port", help="Port to listen on."),
) -> None:
    """Start the local NEXUS REST API server."""
    service = get_service(ctx)
    application = create_app(service)
    console.print(f"[bold green]Starting NEXUS REST API on http://{host}:{port}[/bold green]")
    uvicorn.run(application, host=host, port=port, log_level="info")


@config_app.command("validate")
def config_validate(ctx: typer.Context) -> None:
    """Validate current YAML configuration."""
    cfg = ctx.obj["config"]
    cfg.validate()
    console.print("[bold green]Configuration is valid and ready for use.[/bold green]")


if __name__ == "__main__":
    app()