"""Pydantic response schemas for the REST interface."""

from typing import Any

from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str
    name: str = "NEXUS"


class DataResponse(BaseModel):
    data: dict[str, Any] | list[Any]