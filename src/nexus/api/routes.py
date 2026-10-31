"""API routes delegate all work to NexusService."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from nexus.api.schemas import DataResponse, StatusResponse
from nexus.services import NexusService

router = APIRouter()


def service(request: Request) -> NexusService:
    if getattr(request.app.state, "service", None) is None:
        request.app.state.service = NexusService()
    return request.app.state.service


@router.get("/health", response_model=StatusResponse)
def health() -> dict[str, str]:
    return {"status": "ok", "name": "NEXUS"}


@router.get("/api/v1/system/info", response_model=DataResponse)
@router.get("/system/info", response_model=DataResponse)
def system_info(request: Request) -> dict[str, Any]:
    return {"data": service(request).info()}


@router.get("/api/v1/system/metrics", response_model=DataResponse)
@router.get("/system/metrics", response_model=DataResponse)
def system_metrics(request: Request) -> dict[str, Any]:
    return {"data": service(request).metrics()}


@router.get("/api/v1/system/cpu", response_model=DataResponse)
def system_cpu(request: Request) -> dict[str, Any]:
    return {"data": service(request).metrics().get("cpu", {})}


@router.get("/api/v1/system/memory", response_model=DataResponse)
def system_memory(request: Request) -> dict[str, Any]:
    return {"data": service(request).metrics().get("memory", {})}


@router.get("/api/v1/system/disk", response_model=DataResponse)
def system_disk(request: Request) -> dict[str, Any]:
    metrics = service(request).metrics()
    return {"data": {"disks": metrics.get("disks", []), "io": metrics.get("disk_io", {})}}


@router.get("/api/v1/system/network", response_model=DataResponse)
def system_network(request: Request) -> dict[str, Any]:
    return {"data": service(request).metrics().get("network", {})}


@router.get("/api/v1/system/processes", response_model=DataResponse)
@router.get("/system/processes", response_model=DataResponse)
def system_processes(
    request: Request,
    sort_by: str = Query("cpu", description="Sort by 'cpu' or 'memory'"),
    limit: int = Query(20, ge=1, le=500, description="Process count limit"),
) -> dict[str, Any]:
    if sort_by not in {"cpu", "memory"}:
        raise HTTPException(status_code=400, detail="sort_by must be 'cpu' or 'memory'")
    return {"data": service(request).processes(sort_by, limit)}


@router.get("/api/v1/diagnostics", response_model=DataResponse)
@router.get("/diagnostics", response_model=DataResponse)
def diagnostics(request: Request) -> dict[str, Any]:
    return {"data": service(request).diagnostics()}


@router.get("/api/v1/anomalies", response_model=DataResponse)
@router.get("/anomalies", response_model=DataResponse)
def anomalies(request: Request) -> dict[str, Any]:
    return {"data": service(request).anomalies()}


@router.get("/api/v1/alerts", response_model=DataResponse)
@router.get("/alerts", response_model=DataResponse)
def alerts(request: Request) -> dict[str, Any]:
    return {"data": service(request).alerts()}


@router.get("/api/v1/reports", response_model=DataResponse)
@router.get("/reports", response_model=DataResponse)
def reports(request: Request) -> dict[str, Any]:
    return {"data": service(request).reports()}