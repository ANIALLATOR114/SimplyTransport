from litestar.testing import TestClient


def test_map_returns_iframe(client: TestClient) -> None:
    response = client.get("api/v1/map/8250DB002026")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.text.startswith("<iframe srcdoc=")


def test_map_returns_404_if_stop_not_found(client: TestClient) -> None:
    response = client.get("api/v1/map/fakestop")
    assert response.status_code == 404
    assert response.json() == {
        "path": "/api/v1/map/fakestop",
        "detail": "Stop not found with id fakestop",
        "status_code": 404,
    }
