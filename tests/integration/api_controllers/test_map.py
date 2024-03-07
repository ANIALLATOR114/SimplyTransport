from litestar.testing import TestClient


def test_stop_map_returns_iframe(client: TestClient) -> None:
    response = client.get("api/v1/map/stop/8250DB002026")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.text.startswith("<iframe srcdoc=")


def test_stop_map_returns_404_if_stop_not_found(client: TestClient) -> None:
    response = client.get("api/v1/map/stop/fakestop")
    assert response.status_code == 404
    assert response.json() == {
        "path": "/api/v1/map/stop/fakestop",
        "detail": "Stop not found with id fakestop",
        "status_code": 404,
    }


def test_route_map_returns_iframe(client: TestClient) -> None:
    response = client.get("api/v1/map/route/3623_54684/0")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.text.startswith("<iframe srcdoc=")


def test_route_map_returns_404_if_route_not_found(client: TestClient) -> None:
    response = client.get("api/v1/map/route/fakeroute/0")
    assert response.status_code == 404
    assert response.json() == {
        "path": "/api/v1/map/route/fakeroute/0",
        "detail": "Route not found with id fakeroute and direction 0",
        "status_code": 404,
    }
