"""API Key authentication and basic access control."""

from __future__ import annotations

import os

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-Nexus-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> bool:
    """Validate request API key against NEXUS_API_KEY environment variable.

    Defaults to permissive open mode for localhost unless NEXUS_API_KEY is configured.
    """
    configured_key = os.environ.get("NEXUS_API_KEY")
    if not configured_key:
        return True  # Localhost mode without mandatory authentication
    if api_key != configured_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Nexus-API-Key header")
    return True