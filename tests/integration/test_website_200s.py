import pytest
from litestar.testing import TestClient

urls = [
    "/",
    "/stops/",
    "/routes/",
    "/maps",
    "/stats",
    "/apidocs",
    "/events/",
    "/delays-explained",
    "/about",
]


@pytest.mark.parametrize("url", urls)
def test_url_200(client: TestClient, url: str) -> None:
    response = client.get(url)
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 1


exception_urls = ["/exception"]


@pytest.mark.parametrize("url", exception_urls)
def test_url_500(client: TestClient, url: str) -> None:
    response = client.get(url)
    assert response.status_code == 500
    assert response.elapsed.total_seconds() < 1
