"""Network port discovery, active listeners, and socket inventory."""

from __future__ import annotations

from typing import Any

import psutil


def collect_listening_ports() -> list[dict[str, Any]]:
    """Enumerate network sockets listening on host interfaces."""
    listeners: list[dict[str, Any]] = []
    try:
        connections = psutil.net_connections(kind="inet")
        for conn in connections:
            if conn.status == psutil.CONN_LISTEN:
                listeners.append({
                    "fd": conn.fd,
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                    "ip": conn.laddr.ip if conn.laddr else "",
                    "port": conn.laddr.port if conn.laddr else 0,
                    "pid": conn.pid,
                })
    except (psutil.AccessDenied, OSError):
        pass
    return listeners