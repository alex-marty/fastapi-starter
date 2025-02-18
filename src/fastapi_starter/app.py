from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from fastapi_starter.__about__ import __version__
from fastapi_starter.config import AppConfig, get_config
from fastapi_starter.routes import main_router


# Base technical routers: root and debug

root_router = APIRouter()


class HealthResponse(BaseModel):
    message: str
    app_version: str


@root_router.get("/health")
def get_health() -> HealthResponse:
    return HealthResponse(message="OK", app_version=__version__)


debug_router = APIRouter()


@debug_router.get("/error")
def trigger_server_error() -> None:
    msg = "triggered error for debugging purposes"
    raise RuntimeError(msg)


# FastAPI app


def make_app(config: AppConfig | None = None) -> FastAPI:
    if config is None:
        config = AppConfig()

    app = FastAPI(
        title="FastAPI Starter",
        version=__version__,
        docs_url="/docs" if config.API_ENABLE_DOC_ENDPOINTS else None,
        redoc_url="/redoc" if config.API_ENABLE_DOC_ENDPOINTS else None,
    )

    app.dependency_overrides[get_config] = lambda: config

    app.include_router(root_router)
    if config.ENABLE_DEBUG:
        app.include_router(debug_router)
    app.include_router(main_router)

    return app


app = make_app()
