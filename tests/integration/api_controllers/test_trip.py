from litestar.testing import TestClient


def test_trip_by_id(client: TestClient) -> None:
    response = client.get("api/v1/trip/3623_8603")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == "3623_8603"
    assert response_json["route_id"] == "3623_54684"
    assert response_json["service_id"] == "290"
    assert response_json["headsign"] == "Monkstown Ave"
    assert response_json["short_name"] == "2616"
    assert response_json["direction"] == 0
    assert response_json["block_id"] == "4002"
    assert response_json["dataset"] == "TFI"

    response = client.get("api/v1/trip/3623_14142")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == "3623_14142"
    assert response_json["route_id"] == "3623_54691"
    assert response_json["service_id"] == "290"
    assert response_json["headsign"] == "Limekiln Avenue"
    assert response_json["short_name"] == "6551"
    assert response_json["direction"] == 0
    assert response_json["block_id"] == "7009004"
    assert response_json["dataset"] == "TFI"


def test_trip_by_id_not_found(client: TestClient) -> None:
    response = client.get("api/v1/trip/3623_860544")
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Trip not found with id 3623_860544"


def test_all_trips_by_route_id(client: TestClient) -> None:
    response = client.get("api/v1/trip/route/3623_54684")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 380
    assert response_json[0]["id"] == "3623_8603"
    assert response_json[0]["route_id"] == "3623_54684"
    assert response_json[0]["service_id"] == "290"
    assert response_json[0]["headsign"] == "Monkstown Ave"
    assert response_json[0]["short_name"] == "2616"
    assert response_json[0]["direction"] == 0
    assert response_json[0]["block_id"] == "4002"
    assert response_json[0]["dataset"] == "TFI"
    for trip in response_json:
        assert trip["route_id"] == "3623_54684"

    response = client.get("api/v1/trip/route/3623_54691")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 363
    assert response_json[0]["id"] == "3623_14142"
    assert response_json[0]["route_id"] == "3623_54691"
    assert response_json[0]["service_id"] == "290"
    assert response_json[0]["headsign"] == "Limekiln Avenue"
    assert response_json[0]["short_name"] == "6551"
    assert response_json[0]["direction"] == 0
    assert response_json[0]["block_id"] == "7009004"
    assert response_json[0]["dataset"] == "TFI"
    for trip in response_json:
        assert trip["route_id"] == "3623_54691"


def test_all_trips_by_route_id_and_count(client: TestClient) -> None:
    response = client.get("api/v1/trip/route/count/3623_54684")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 380
    assert len(response_json["trips"]) == 380

    response = client.get("api/v1/trip/route/count/3623_54691")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 363
    assert len(response_json["trips"]) == 363
