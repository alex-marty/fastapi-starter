from fastapi.testclient import TestClient


def test_say_hello(api_client: TestClient):
    response = api_client.get("/v1/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!", "debug_enabled": True}

    response = api_client.get("/v1/hello", params={"name": "Alice"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Alice!", "debug_enabled": True}
