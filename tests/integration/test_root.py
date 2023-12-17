from litestar.testing import AsyncTestClient
import pytest

@pytest.mark.asyncio
async def test_root_200(async_client: AsyncTestClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "Welcome to SimplyTransport" in response.text

@pytest.mark.asyncio
async def test_healthcheck_200(async_client: AsyncTestClient) -> None:
    response = await async_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.text == "OK"
