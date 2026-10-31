"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from nexus.api.routes import router
from nexus.services import NexusService


def create_app(service: NexusService | None = None) -> FastAPI:
    application = FastAPI(title="NEXUS API", version="0.1.0", description="Local system diagnostics API")
    application.state.service = service
    application.include_router(router)

    @application.exception_handler(ValueError)
    async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    return application


app = create_app()