"""Kubernetes cluster, node, and pod discovery."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


def collect_kubernetes() -> dict[str, Any]:
    """Inspect local/remote Kubernetes cluster context, nodes, and pods."""
    kubectl_bin = shutil.which("kubectl")
    if not kubectl_bin:
        return {"available": False, "nodes": [], "pods": []}

    try:
        # Pods query
        cmd = [kubectl_bin, "get", "pods", "-A", "-o", "json"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3.0, check=False)
        pods: list[dict[str, Any]] = []
        if res.returncode == 0 and res.stdout.strip():
            pod_json = json.loads(res.stdout)
            for item in pod_json.get("items", []):
                meta = item.get("metadata", {})
                status = item.get("status", {})
                pods.append({
                    "name": meta.get("name", ""),
                    "namespace": meta.get("namespace", ""),
                    "phase": status.get("phase", ""),
                    "pod_ip": status.get("podIP", ""),
                    "node_name": item.get("spec", {}).get("nodeName", ""),
                })

        # Nodes query
        cmd_nodes = [kubectl_bin, "get", "nodes", "-o", "json"]
        res_nodes = subprocess.run(cmd_nodes, capture_output=True, text=True, timeout=3.0, check=False)
        nodes: list[dict[str, Any]] = []
        if res_nodes.returncode == 0 and res_nodes.stdout.strip():
            node_json = json.loads(res_nodes.stdout)
            for item in node_json.get("items", []):
                meta = item.get("metadata", {})
                status = item.get("status", {})
                nodes.append({
                    "name": meta.get("name", ""),
                    "ready": any(
                        c.get("type") == "Ready" and c.get("status") == "True"
                        for c in status.get("conditions", [])
                    ),
                    "kubelet_version": status.get("nodeInfo", {}).get("kubeletVersion", ""),
                    "os_image": status.get("nodeInfo", {}).get("osImage", ""),
                })

        return {
            "available": True,
            "nodes": nodes,
            "pods": pods,
        }
    except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
        return {"available": False, "nodes": [], "pods": []}