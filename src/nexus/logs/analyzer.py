"""Summarize local text log files without requiring an external service."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from nexus.logs.parser import parse_line


def analyze_log(path: str | Path, recurring_limit: int = 3, max_entries_in_memory: int = 1000) -> dict[str, Any]:
    """Stream and analyze large log files without loading everything into RAM."""
    file_path = Path(path).expanduser()
    counts: Counter[str] = Counter()
    entries_sample: list[dict[str, Any]] = []
    signatures: Counter[str] = Counter()
    samples: dict[str, str] = {}
    total_lines = 0
    malformed_count = 0

    try:
        with file_path.open(encoding="utf-8", errors="replace") as stream:
            for number, line in enumerate(stream, 1):
                total_lines = number
                item = parse_line(line, number)
                if item["malformed"]:
                    malformed_count += 1
                if item["severity"] != "UNKNOWN":
                    counts[item["severity"]] += 1

                # Keep a bounded sample in memory for preview
                if len(entries_sample) < max_entries_in_memory:
                    entries_sample.append(item)

                if item["severity"] == "ERROR":
                    msg = item["message"]
                    signature = re.sub(r"\bERROR\b[:\s-]*", "", msg, count=1, flags=re.IGNORECASE)
                    signature = re.sub(r"^\d{4}-\d{2}-\d{2}[T ][^ ]+\s+", "", signature)
                    signature = " ".join(signature.split())
                    signatures[signature] += 1
                    samples.setdefault(signature, msg)

    except OSError as exc:
        raise ValueError(f"Cannot read log file {file_path}: {exc}") from exc

    recurring = [
        {"message": samples[text], "count": count}
        for text, count in signatures.most_common()
        if count >= recurring_limit
    ]

    return {
        "path": str(file_path),
        "total_lines": total_lines,
        "severity_counts": dict(counts),
        "error_count": counts["ERROR"],
        "warning_count": counts["WARNING"],
        "info_count": counts["INFO"],
        "debug_count": counts["DEBUG"],
        "malformed_count": malformed_count,
        "recurring_errors": recurring,
        "entries": entries_sample,
    }