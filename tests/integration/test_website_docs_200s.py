import pytest
from litestar.testing import TestClient

urls = [
    "",
    "/swagger/",
    "/elements",
    "/redoc",
    "/rapidoc",
    "/openapi.json",
    "/openapi.yaml",
]


@pytest.mark.parametrize("url", urls)
def test_url_200(client: TestClient, url: str) -> None:
    response = client.get(f"/docs{url}")
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 1


def test_default_is_stoplight(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "stoplight" in response.text
    assert "elements" in response.text