from httpx import AsyncClient


def test_favicon(client: AsyncClient) -> None:
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    content_types = [
        "image/vnd.microsoft.icon",
        "image/x-icon",
    ]
    assert response.headers["content-type"] in content_types


def test_htmx_js(client: AsyncClient) -> None:
    response = client.get("/static/1.9.7.htmx.min.js")
    assert response.status_code == 200
    assert response.headers["content-length"] == "46674"
