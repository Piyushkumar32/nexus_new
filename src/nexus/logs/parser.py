"""Parse severity and common timestamp formats from text log lines."""

import re
from datetime import datetime

TIMESTAMP = re.compile(r"^(\d{4}-\d{2}-\d{2}[T ][0-9:.+-]+Z?)")
LEVEL = re.compile(r"\b(ERROR|WARNING|WARN|INFO|DEBUG)\b", re.IGNORECASE)


def parse_line(line: str, line_number: int = 1) -> dict:
    text = line.rstrip("\r\n")
    timestamp = None
    match = TIMESTAMP.match(text)
    if match:
        candidate = match.group(1).replace("Z", "+00:00")
        try:
            timestamp = datetime.fromisoformat(candidate).isoformat()
        except ValueError:
            timestamp = None
    severity_match = LEVEL.search(text)
    severity = severity_match.group(1).upper() if severity_match else "UNKNOWN"
    if severity == "WARN":
        severity = "WARNING"
    return {"line_number": line_number, "timestamp": timestamp, "severity": severity,
            "message": text, "malformed": severity == "UNKNOWN" or bool(match and timestamp is None)}