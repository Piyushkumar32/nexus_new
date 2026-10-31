"""Robust SQLite repository with retention, schema initialization, and transactional queries."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class Repository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode = WAL;")
        return connection

    def initialize(self) -> None:
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    captured_at REAL NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS health_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    captured_at REAL NOT NULL,
                    score INTEGER NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS diagnostics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    captured_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    captured_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    captured_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generated_at TEXT NOT NULL,
                    format TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    summary TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_snapshots_captured ON snapshots(captured_at);
                CREATE INDEX IF NOT EXISTS idx_health_captured ON health_scores(captured_at);
            """)

    def save_snapshot(
        self,
        snapshot: dict[str, Any],
        health: dict[str, Any],
        findings: list[dict[str, Any]],
        anomalies: list[dict[str, Any]],
        alerts: list[dict[str, Any]],
    ) -> None:
        captured_at = snapshot.get("captured_at", 0.0)
        with self._connect() as db:
            db.execute(
                "INSERT INTO snapshots(captured_at, payload) VALUES(?, ?)",
                (captured_at, json.dumps(snapshot)),
            )
            db.execute(
                "INSERT INTO health_scores(captured_at, score, payload) VALUES(?, ?, ?)",
                (captured_at, health.get("score", 0), json.dumps(health)),
            )
            for table, records in (("diagnostics", findings), ("anomalies", anomalies), ("alerts", alerts)):
                db.executemany(
                    f"INSERT INTO {table}(captured_at, payload) VALUES(?, ?)",
                    [(str(record.get("timestamp", captured_at)), json.dumps(record)) for record in records],
                )

    def save_events(self, table: str, records: list[dict[str, Any]]) -> None:
        """Persist event records for a log analysis or standalone source."""
        if table not in {"diagnostics", "anomalies", "alerts"}:
            raise ValueError("Unsupported event table")
        with self._connect() as db:
            db.executemany(
                f"INSERT INTO {table}(captured_at, payload) VALUES(?, ?)",
                [(str(record.get("timestamp", "")), json.dumps(record)) for record in records],
            )

    def save_report_meta(self, generated_at: str, report_format: str, file_path: str, summary: str = "") -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO reports(generated_at, format, file_path, summary) VALUES(?, ?, ?, ?)",
                (generated_at, report_format, file_path, summary),
            )

    def recent(self, table: str, limit: int = 50) -> list[dict[str, Any]]:
        valid_tables = {"snapshots", "health_scores", "diagnostics", "anomalies", "alerts", "reports"}
        if table not in valid_tables:
            raise ValueError("Unsupported history table")
        with self._connect() as db:
            rows = db.execute(f"SELECT payload FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def cleanup_old_records(self, max_records_per_table: int = 5000) -> dict[str, int]:
        """Prune tables exceeding max_records_per_table to keep database lightweight."""
        pruned = {}
        with self._connect() as db:
            for table in ("snapshots", "health_scores", "diagnostics", "anomalies", "alerts"):
                count_row = db.execute(f"SELECT COUNT(*) as c FROM {table}").fetchone()
                count = count_row["c"] if count_row else 0
                if count > max_records_per_table:
                    excess = count - max_records_per_table
                    db.execute(
                        f"DELETE FROM {table} WHERE id IN (SELECT id FROM {table} ORDER BY id ASC LIMIT ?)",
                        (excess,),
                    )
                    pruned[table] = excess
                else:
                    pruned[table] = 0
        return pruned