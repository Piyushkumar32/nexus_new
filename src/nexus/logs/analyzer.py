"""Summarize local text log files without requiring an external service."""

import re
from collections import Counter
from pathlib import Path

from nexus.logs.parser import parse_line


def analyze_log(path: str | Path, recurring_limit: int = 3) -> dict:
    file_path = Path(path).expanduser()
    counts: Counter[str] = Counter()
    parsed = []
    try:
        with file_path.open(encoding="utf-8", errors="replace") as stream:
            for number, line in enumerate(stream, 1):
                item = parse_line(line, number)
                parsed.append(item)
                if item["severity"] != "UNKNOWN":
                    counts[item["severity"]] += 1
    except OSError as exc:
        raise ValueError(f"Cannot read log file {file_path}: {exc}") from exc
    errors = [item["message"] for item in parsed if item["severity"] == "ERROR"]
    signatures: Counter[str] = Counter()
    samples: dict[str, str] = {}
    for message in errors:
        signature = re.sub(r"\bERROR\b[:\s-]*", "", message, count=1)
        signature = re.sub(r"^\d{4}-\d{2}-\d{2}[T ][^ ]+\s+", "", signature)
        signature = " ".join(signature.split())
        signatures[signature] += 1
        samples.setdefault(signature, message)
    recurring = [
        {"message": samples[text], "count": count}
        for text, count in signatures.most_common()
        if count >= recurring_limit
    ]
    return {"path": str(file_path), "total_lines": len(parsed), "severity_counts": dict(counts),
            "error_count": counts["ERROR"], "warning_count": counts["WARNING"],
            "malformed_count": sum(item["malformed"] for item in parsed),
            "recurring_errors": recurring, "entries": parsed}