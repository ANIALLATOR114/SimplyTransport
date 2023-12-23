import pytest
from litestar.testing import TestClient

urls = ["/", "/events/", "/stops/", "/routes/", "/apidocs", "/about"]


@pytest.mark.parametrize("url", urls)
@pytest.mark.asyncio
def test_url_200(client: TestClient, url: str) -> None:
    response = client.get(url)
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 1
