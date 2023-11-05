from httpx import AsyncClient


def test_favicon(client: AsyncClient) -> None:
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/x-icon"


def test_htmx_js(client: AsyncClient) -> None:
    response = client.get("/static/1.9.7.htmx.min.js")
    assert response.status_code == 200
    assert response.headers["content-length"] == "46674"
