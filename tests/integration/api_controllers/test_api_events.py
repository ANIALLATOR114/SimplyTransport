from litestar.testing import TestClient

def test_events_paginated_resturns_results(client: TestClient) -> None:
    response = client.get("api/v1/events/")
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["total"] > 1
    assert len(response_json["events"]) > 1


def test_events_paginated_by_type_returns_results(client: TestClient) -> None:
    response = client.get("api/v1/events/gtfs.database.updated")
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["total"] > 1
    assert len(response_json["events"]) > 1


def test_events_paginated_by_type_non_existent_returns_400(client: TestClient) -> None:
    response = client.get("api/v1/events/something.that.does.not.exist")
    assert response.status_code == 400


def test_events_most_recent_by_type_returns_results(client: TestClient) -> None:
    response = client.get("api/v1/events/gtfs.database.updated/most-recent")
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["event_type"] == "gtfs.database.updated"
    assert response_json["created_at"] is not None