import pytest
from fastapi.testclient import TestClient

from fastapi_starter.__about__ import __version__


def test_app_health(api_client: TestClient):
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK", "app_version": __version__}


def test_app_error(api_client: TestClient):
    with pytest.raises(RuntimeError) as exc_info:
        api_client.get("/error")

    assert str(exc_info.value) == "triggered error for debugging purposes"
