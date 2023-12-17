from litestar.testing import TestClient
from SimplyTransport.domain.stop_times.model import StopTime


def test_get_stop_times_by_stop_id(client: TestClient) -> None:
    response = client.get("api/v1/stoptime/stop/8240DB000324")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1
    assert isinstance(response_json, list)
    for item in response_json:
        StopTime.model_validate(item)
        assert item["stop_id"] == "8240DB000324"


def test_get_stop_times_by_trip_id(client: TestClient) -> None:
    response = client.get("api/v1/stoptime/trip/3623_8603")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 56
    assert isinstance(response_json, list)
    for item in response_json:
        StopTime.model_validate(item)
        assert item["trip_id"] == "3623_8603"
