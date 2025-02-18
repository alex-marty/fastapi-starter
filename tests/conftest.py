import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_starter.app import make_app
from fastapi_starter.config import AppConfig, get_config


@pytest.fixture()
def app_config() -> AppConfig:
    """Provide an instance of the application configuration."""
    return AppConfig(
        API_ENABLE_DOC_ENDPOINTS=True,
        ENABLE_DEBUG=True,
    )


@pytest.fixture()
def api_app(app_config: AppConfig) -> FastAPI:
    """Provide a FastAPI application instance."""
    api_app = make_app(app_config)
    api_app.dependency_overrides[get_config] = lambda: app_config
    return api_app


@pytest.fixture()
def api_client(api_app: FastAPI) -> TestClient:
    """Provide a test client for the FastAPI application."""
    return TestClient(api_app)
