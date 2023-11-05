from httpx import AsyncClient


def test_root_200(client: AsyncClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to SimplyTransport" in response.text


def test_healthcheck_200(client: AsyncClient) -> None:
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.text == "OK"
