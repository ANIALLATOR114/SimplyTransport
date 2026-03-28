import math

from litestar.testing import TestClient


def test_get_stop_by_id(client: TestClient) -> None:
    response = client.get("/api/v1/stop/8240DB000324")
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["id"] == "8240DB000324"
    assert response_json["code"] == "324"
    assert response_json["name"] == "Harristown"
    assert response_json["description"] == ""
    assert math.isclose(response_json["lat"], 53.41772268, abs_tol=1e-09)
    assert math.isclose(response_json["lon"], -6.278644169, abs_tol=1e-09)
    assert response_json["zone_id"] == ""
    assert response_json["url"] == ""
    assert response_json["location_type"] is None
    assert response_json["parent_station"] is None
    assert response_json["dataset"] == "TFI"

    response = client.get("/api/v1/stop/8240DB007132")
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["id"] == "8240DB007132"
    assert response_json["code"] == "7132"
    assert response_json["name"] == "Charlestown SC"
    assert response_json["description"] == ""
    assert math.isclose(response_json["lat"], 53.40308897, abs_tol=1e-09)
    assert math.isclose(response_json["lon"], -6.304306560, abs_tol=1e-09)
    assert response_json["zone_id"] == ""
    assert response_json["url"] == ""
    assert response_json["location_type"] is None
    assert response_json["parent_station"] is None
    assert response_json["dataset"] == "TFI"


def test_get_stop_by_id_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/stop/8240DB0003241")
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Stop not found with id 8240DB0003241"


def test_get_stop_detailed(client: TestClient) -> None:
    response = client.get("/api/v1/stop/8240DB000324/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["stop"]["id"] == "8240DB000324"
    assert data["stop"]["code"] == "324"
    assert data["stop"]["name"]
    assert isinstance(data["routes"], list)
    assert len(data["routes"]) >= 1
    assert "route_id" in data["routes"][0]
    assert "short_name" in data["routes"][0]
    assert "long_name" in data["routes"][0]
    assert "stop_features" in data
    assert "street_view_url" in data
    assert isinstance(data["street_view_url"], str)


def test_get_stop_detailed_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/stop/__no_such_stop__/detailed")
    assert response.status_code == 404
    assert response.json()["detail"] == "Stop not found with id __no_such_stop__"


def test_get_stop_by_code(client: TestClient) -> None:
    response = client.get("/api/v1/stop/code/324")
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["id"] == "8240DB000324"
    assert response_json["code"] == "324"
    assert response_json["name"] == "Harristown"
    assert response_json["description"] == ""
    assert math.isclose(response_json["lat"], 53.41772268, abs_tol=1e-09)
    assert math.isclose(response_json["lon"], -6.278644169, abs_tol=1e-09)
    assert response_json["zone_id"] == ""
    assert response_json["url"] == ""
    assert response_json["location_type"] is None
    assert response_json["parent_station"] is None
    assert response_json["dataset"] == "TFI"

    response = client.get("/api/v1/stop/code/7132")
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["id"] == "8240DB007132"
    assert response_json["code"] == "7132"
    assert response_json["name"] == "Charlestown SC"
    assert response_json["description"] == ""
    assert math.isclose(response_json["lat"], 53.40308897, abs_tol=1e-09)
    assert math.isclose(response_json["lon"], -6.304306560, abs_tol=1e-09)
    assert response_json["zone_id"] == ""
    assert response_json["url"] == ""
    assert response_json["location_type"] is None
    assert response_json["parent_station"] is None
    assert response_json["dataset"] == "TFI"


def test_get_stop_by_code_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/stop/code/3241")
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Stop not found with code 3241"


def test_search_stops_by_name(client: TestClient) -> None:
    response = client.get("/api/v1/stop/search?search=Harristown")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 1
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == "8240DB000324"
    assert response_json["items"][0]["name"] == "Harristown"

    response = client.get("/api/v1/stop/search?search=harris")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 1
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == "8240DB000324"
    assert response_json["items"][0]["name"] == "Harristown"

    response = client.get("/api/v1/stop/search?search=Charle")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 1
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == "8240DB007132"
    assert response_json["items"][0]["name"] == "Charlestown SC"


def test_search_stops_by_code(client: TestClient) -> None:
    response = client.get("/api/v1/stop/search?search=324")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 1
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == "8240DB000324"
    assert response_json["items"][0]["name"] == "Harristown"

    response = client.get("/api/v1/stop/search?search=7132")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 1
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == "8240DB007132"
    assert response_json["items"][0]["name"] == "Charlestown SC"


def test_search_stops_offsetpagination(client: TestClient) -> None:
    response = client.get("/api/v1/stop/search?search=Harristown&currentPage=1&pageSize=10")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 1
    assert response_json["offset"] == 0
    assert response_json["limit"] == 10
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == "8240DB000324"
    assert response_json["items"][0]["name"] == "Harristown"

    response = client.get("/api/v1/stop/search?search=Harristown&currentPage=2&pageSize=10")
    assert response.status_code == 404  # No results on the second page
