from litestar.testing import TestClient


def test_get_schedule(client: TestClient) -> None:
    response = client.get("/api/v1/schedule/8220DB000039?start_time=05%3A00%3A00&end_time=07%3A00%3A00&day=1")
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == 2
    assert "route" in response_json[0]
    assert "stop_time" in response_json[0]
    assert "trip" in response_json[0]
    assert response_json[0]["route"]["long_name"] == "Monkstown Avenue - Harristown"


def test_get_schedule_with_backwards_time_throws_error(client: TestClient) -> None:
    response = client.get("/api/v1/schedule/8220DB000039?start_time=07%3A00%3A00&end_time=05%3A00%3A00&day=1")
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Start time cannot be after end time"


def test_get_schedule_with_same_time_throws_error(client: TestClient) -> None:
    response = client.get("/api/v1/schedule/8220DB000039?start_time=07%3A00%3A00&end_time=07%3A00%3A00&day=1")
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Start time cannot be equal to end time"


def test_get_schedule_with_too_big_gap_throws_error(client: TestClient) -> None:
    response = client.get("/api/v1/schedule/8220DB000039?start_time=07%3A00%3A00&end_time=16%3A00%3A00&day=1")
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Start time and end time cannot be more than 3 hours apart"