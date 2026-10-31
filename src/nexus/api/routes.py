"""API routes delegate all work to NexusService."""

from fastapi import APIRouter, Request

from nexus.api.schemas import DataResponse, StatusResponse
from nexus.services import NexusService

router = APIRouter()


def service(request: Request) -> NexusService:
    if request.app.state.service is None:
        request.app.state.service = NexusService()
    return request.app.state.service


@router.get("/health", response_model=StatusResponse)
def health() -> dict:
    return {"status": "ok"}


@router.get("/system/info", response_model=DataResponse)
def system_info(request: Request) -> dict:
    return {"data": service(request).info()}


@router.get("/system/metrics", response_model=DataResponse)
def system_metrics(request: Request) -> dict:
    return {"data": service(request).metrics()}


@router.get("/system/processes", response_model=DataResponse)
def system_processes(request: Request, sort_by: str = "cpu", limit: int = 20) -> dict:
    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")
    return {"data": service(request).processes(sort_by, limit)}


@router.get("/diagnostics", response_model=DataResponse)
def diagnostics(request: Request) -> dict:
    return {"data": service(request).diagnostics()}


@router.get("/alerts", response_model=DataResponse)
def alerts(request: Request) -> dict:
    return {"data": service(request).alerts()}


@router.get("/reports", response_model=DataResponse)
def reports(request: Request) -> dict:
    return {"data": service(request).reports()}