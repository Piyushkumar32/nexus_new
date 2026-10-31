"""Small parameterized SQLite repository for local monitoring history."""

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
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY, captured_at REAL NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS health_scores (
                    id INTEGER PRIMARY KEY, captured_at REAL NOT NULL, score INTEGER NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS diagnostics (
                    id INTEGER PRIMARY KEY, captured_at TEXT NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY, captured_at TEXT NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY, captured_at TEXT NOT NULL, payload TEXT NOT NULL
                );
            """)

    def save_snapshot(self, snapshot: dict, health: dict, findings: list[dict], anomalies: list[dict], alerts: list[dict]) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO snapshots(captured_at,payload) VALUES(?,?)",
                       (snapshot["captured_at"], json.dumps(snapshot)))
            db.execute("INSERT INTO health_scores(captured_at,score,payload) VALUES(?,?,?)",
                       (snapshot["captured_at"], health["score"], json.dumps(health)))
            for table, records in (("diagnostics", findings), ("anomalies", anomalies), ("alerts", alerts)):
                db.executemany(f"INSERT INTO {table}(captured_at,payload) VALUES(?,?)",
                               [(str(record.get("timestamp", snapshot["captured_at"])), json.dumps(record))
                                for record in records])

    def save_events(self, table: str, records: list[dict]) -> None:
        """Persist event records for a log analysis or other standalone source."""
        if table not in {"diagnostics", "anomalies", "alerts"}:
            raise ValueError("Unsupported event table")
        with self._connect() as db:
            db.executemany(
                f"INSERT INTO {table}(captured_at,payload) VALUES(?,?)",
                [(str(record.get("timestamp", "")), json.dumps(record)) for record in records],
            )

    def recent(self, table: str, limit: int = 50) -> list[dict[str, Any]]:
        if table not in {"snapshots", "health_scores", "diagnostics", "anomalies", "alerts"}:
            raise ValueError("Unsupported history table")
        with self._connect() as db:
            rows = db.execute(f"SELECT payload FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(row["payload"]) for row in rows]