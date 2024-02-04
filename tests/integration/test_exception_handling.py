from litestar.testing import TestClient
import pytest

urls = ["fakeroute", "fakerouter/fake", "/api/fakeroute", "/api/fakeroute/fake"]
@pytest.mark.parametrize("url", urls)
def test_api_404_handler(client: TestClient, url:str) -> None:
    response = client.get(url)
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["path"] == url
    assert response.elapsed.total_seconds() < 1


urls = ["fakeroute", "fakerouter/fake", "/api/fakeroute", "/api/fakeroute/fake"]
@pytest.mark.parametrize("url", urls)
def test_website_404_handler(client: TestClient, url:str) -> None:
    headers = {"accept": "text/html"}
    response = client.get(url, headers=headers)
    assert response.status_code == 404
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "404 Not Found" in response.text
    assert "The requested URL was not found on the server" in response.text
    assert response.elapsed.total_seconds() < 1

