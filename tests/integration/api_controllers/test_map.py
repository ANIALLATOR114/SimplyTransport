from urllib.parse import quote

from litestar.testing import TestClient


def test_stop_map_returns_json(client: TestClient) -> None:
    response = client.get("/api/v1/map/stop/8250DB002026")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert "center" in data
    assert len(data["center"]) == 2
    assert "zoom" in data
    assert "focus_stop_id" in data
    assert "direction" in data
    assert "routes" in data
    assert "vehicles" in data
    assert "stops" in data
    assert isinstance(data["routes"], list)
    assert isinstance(data["stops"], list)
    if data["stops"]:
        s0 = data["stops"][0]
        assert "stop_id" in s0
        assert "routes" not in s0
        assert "stop_features" not in s0
        assert "street_view_url" not in s0


def test_stop_map_returns_404_if_stop_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/map/stop/fakestop")
    assert response.status_code == 404
    assert response.json() == {
        "path": "/api/v1/map/stop/fakestop",
        "detail": "Stop not found with id fakestop",
        "status_code": 404,
    }


def test_route_map_returns_json(client: TestClient) -> None:
    response = client.get("/api/v1/map/route/3623_54684/0")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert "center" in data
    assert len(data["center"]) == 2
    assert data.get("zoom") == 12
    assert "route_id" in data
    assert "direction" in data
    assert "route" in data
    assert data["route"]["route_id"] == "3623_54684"
    assert "vehicles" in data
    assert "stops" in data
    assert isinstance(data["stops"], list)


def test_route_map_returns_404_if_route_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/map/route/fakeroute_id/0")
    assert response.status_code == 404
    assert response.json() == {
        "path": "/api/v1/map/route/fakeroute_id/0",
        "detail": "Route map not found for route fakeroute_id and direction 0",
        "status_code": 404,
    }


def test_nearby_map_returns_json(client: TestClient) -> None:
    response = client.get("/api/v1/map/stop/nearby?latitude=53.44928&longitude=-7.51441")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert "center" in data
    assert len(data["center"]) == 2
    assert data.get("zoom") == 15
    assert "user_lat" in data
    assert "user_lon" in data
    assert "radius_meters" in data
    assert data["radius_meters"] == 1200
    assert "stops" in data
    assert isinstance(data["stops"], list)


def test_nearby_map_accepts_radius_meters(client: TestClient) -> None:
    response = client.get("/api/v1/map/stop/nearby?latitude=53.44928&longitude=-7.51441&radius_meters=900")
    assert response.status_code == 200
    assert response.json()["radius_meters"] == 900


def test_nearby_map_rejects_radius_meters_out_of_range(client: TestClient) -> None:
    r0 = client.get("/api/v1/map/stop/nearby?latitude=53.44928&longitude=-7.51441&radius_meters=0")
    assert r0.status_code == 400
    r_hi = client.get("/api/v1/map/stop/nearby?latitude=53.44928&longitude=-7.51441&radius_meters=1501")
    assert r_hi.status_code == 400


def test_agency_map_returns_json(client: TestClient) -> None:
    agency_id = "7778019"
    response = client.get(f"/api/v1/map/route/agency/{agency_id}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert "center" in data
    assert len(data["center"]) == 2
    assert data.get("agency_id") == agency_id
    assert "routes" in data
    assert isinstance(data["routes"], list)


def test_agency_map_returns_404_for_unknown_agency(client: TestClient) -> None:
    response = client.get("/api/v1/map/route/agency/__no_such_agency__")
    assert response.status_code == 404
    assert "No routes found" in response.json().get("detail", "")


def test_static_stop_map_returns_json(client: TestClient) -> None:
    mt = quote("All Stops")
    response = client.get(f"/api/v1/map/stop/aggregated/{mt}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert "center" in data
    assert len(data["center"]) == 2
    assert "map_type" in data
    assert "stops" in data
    assert isinstance(data["stops"], list)


def test_static_stop_map_returns_400_for_invalid_map_type(client: TestClient) -> None:
    response = client.get("/api/v1/map/stop/aggregated/not-a-valid-map-type")
    assert response.status_code == 400
