from litestar.testing import AsyncTestClient
import pytest


@pytest.mark.asyncio
async def test_favicon(async_client: AsyncTestClient) -> None:
    response = await async_client.get("/favicon.ico")
    assert response.status_code == 200
    content_types = [
        "image/vnd.microsoft.icon",
        "image/x-icon",
    ]
    assert response.headers["content-type"] in content_types
