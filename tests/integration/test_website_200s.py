import pytest
from litestar.testing import AsyncTestClient

urls = ["/", "/events/", "/stops/", "/routes/", "/apidocs", "/about"]


@pytest.mark.parametrize("url", urls)
@pytest.mark.asyncio
async def test_url_200(async_client: AsyncTestClient, url: str) -> None:
    response = await async_client.get(url)
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 1
