from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from fastapi_starter.__about__ import __version__
from fastapi_starter.api.routes import main_router
from fastapi_starter.config import AppConfig, get_config
from fastapi_starter.utils import (
    git_revision_hash,
    git_root_path,
    git_working_directory_is_clean,
)


# Base technical routers: root and debug

root_router = APIRouter()


class HealthResponse(BaseModel):
    message: str
    app_version: str
    git_hash: str | None
    git_dirty: bool | None


@root_router.get("/health")
def get_health() -> HealthResponse:
    in_git_repo = git_root_path(allow_none=True) is not None
    return HealthResponse(
        message="OK",
        app_version=__version__,
        git_hash=git_revision_hash() if in_git_repo else None,
        git_dirty=not git_working_directory_is_clean() if in_git_repo else None,
    )


debug_router = APIRouter()


@debug_router.get("/error")
def trigger_server_error() -> None:
    msg = "triggered error for debugging purposes"
    raise RuntimeError(msg)


# FastAPI app


def make_app(config: AppConfig | None = None) -> FastAPI:
    if config is None:
        config = get_config()

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
