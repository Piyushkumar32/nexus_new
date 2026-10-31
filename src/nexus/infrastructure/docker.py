"""Docker container discovery and resource monitoring."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


def collect_containers() -> list[dict[str, Any]]:
    """Discover running and stopped Docker containers with resource stats."""
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return []

    try:
        # Check if Docker daemon is running by listing containers
        cmd = [docker_bin, "ps", "-a", "--format", "{{json .}}"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=2.5, check=False)
        if res.returncode != 0 or not res.stdout.strip():
            return []

        containers: list[dict[str, Any]] = []
        for line in res.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                containers.append({
                    "id": data.get("ID", ""),
                    "name": data.get("Names", ""),
                    "image": data.get("Image", ""),
                    "status": data.get("Status", ""),
                    "state": data.get("State", ""),
                    "created_at": data.get("CreatedAt", ""),
                    "ports": data.get("Ports", ""),
                })
            except json.JSONDecodeError:
                continue
        return containers
    except (subprocess.TimeoutExpired, OSError):
        return []