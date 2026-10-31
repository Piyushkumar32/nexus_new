"""Local automation scheduler for periodic snapshots and health jobs."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class Scheduler:
    """Lightweight in-process background task scheduler."""

    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._jobs: list[dict[str, Any]] = []

    def add_job(self, name: str, interval_seconds: float, func: Callable[[], Any]) -> None:
        self._jobs.append({
            "name": name,
            "interval": interval_seconds,
            "func": func,
            "last_run": 0.0,
        })

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="nexus-scheduler", daemon=True)
        self._thread.start()
        logger.info("NEXUS automation scheduler started.")

    def stop(self, timeout: float = 3.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        logger.info("NEXUS automation scheduler stopped.")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            now = time.time()
            for job in self._jobs:
                if now - job["last_run"] >= job["interval"]:
                    try:
                        job["func"]()
                    except Exception as exc:
                        logger.error("Error executing scheduled job '%s': %s", job["name"], exc)
                    job["last_run"] = time.time()
            self._stop_event.wait(1.0)