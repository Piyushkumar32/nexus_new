"""Alert notification channels (Webhook, Email, Slack) with safe execution."""

from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


def dispatch_webhook(url: str, payload: dict[str, Any], timeout: float = 3.0) -> bool:
    """Send alert notification payload to an external HTTP webhook."""
    if not url.startswith(("http://", "https://")):
        return False
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "NEXUS-Alert-Engine/2.0"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return 200 <= response.status < 300
    except Exception as exc:
        logger.error("Failed to dispatch alert webhook to %s: %s", url, exc)
        return False