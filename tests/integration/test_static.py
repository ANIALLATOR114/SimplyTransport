from httpx import AsyncClient


def test_favicon(client: AsyncClient) -> None:
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    content_types = [
        "image/vnd.microsoft.icon",
        "image/x-icon",
    ]
    assert response.headers["content-type"] in content_types