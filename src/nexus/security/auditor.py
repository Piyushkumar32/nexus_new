"""Defensive security intelligence, unexpected port auditing, and process checks."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from nexus.infrastructure.ports import collect_listening_ports


def audit_suspicious_processes(processes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Scan process inventory for known risky patterns or suspicious execution paths."""
    suspicious: list[dict[str, Any]] = []
    risky_names = {"nc", "netcat", "nmap", "cryptominer", "xmrig"}

    for p in processes:
        name = str(p.get("name") or "").lower()
        pid = p.get("pid", 0)
        for risky in risky_names:
            if risky in name:
                suspicious.append({
                    "pid": pid,
                    "name": name,
                    "reason": f"Process matches known security audit signature: '{risky}'",
                    "severity": "high",
                })
    return suspicious


def audit_listening_ports(allowed_ports: set[int] | None = None) -> list[dict[str, Any]]:
    """Identify unexpected ports open on host interfaces."""
    open_ports = collect_listening_ports()
    flagged: list[dict[str, Any]] = []
    # Well-known administrative and common insecure service ports
    sensitive_ports = {21: "FTP", 23: "Telnet", 445: "SMB", 3389: "RDP"}

    for p in open_ports:
        port = p.get("port", 0)
        if port in sensitive_ports:
            flagged.append({
                "port": port,
                "service": sensitive_ports[port],
                "severity": "medium",
                "ip": p.get("ip", ""),
                "pid": p.get("pid"),
                "description": f"Potentially exposed sensitive service ({sensitive_ports[port]}) listening on port {port}.",
            })
    return flagged


def calculate_file_hash(path: str | Path) -> str | None:
    """Compute SHA-256 hash for file integrity monitoring."""
    target = Path(path).expanduser()
    if not target.is_file():
        return None
    try:
        hasher = hashlib.sha256()
        with target.open("rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return None