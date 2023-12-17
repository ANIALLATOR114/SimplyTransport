from litestar.testing import TestClient
from SimplyTransport.domain.calendar_dates.model import CalendarDate


def test_calendar_date_all(client: TestClient) -> None:
    response = client.get("api/v1/calendardate/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 238
    assert isinstance(response_json, list)
    for item in response_json:
        CalendarDate.model_validate(item)


def test_calendar_date_all_and_count(client: TestClient) -> None:
    response = client.get("api/v1/calendardate/count")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 238
    assert len(response_json["calendar_dates"]) == 238


def test_get_calendar_date_by_service_id(client: TestClient) -> None:
    response = client.get("api/v1/calendardate/154")
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == 3
    assert response_json[0]["service_id"] == "154"
    assert response_json[0]["date"] == "2023-10-30"
    assert response_json[0]["exception_type"] == "removed"
    assert response_json[0]["dataset"] == "TFI"
    for each_date in response_json:
        assert each_date["service_id"] == "154"


def test_get_active_calendar_dates_on_date(client: TestClient) -> None:
    response = client.get("api/v1/calendardate/date/2023-10-30")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 24
    for each_date in response_json:
        assert each_date["date"] == "2023-10-30"

    response = client.get("api/v1/calendardate/date/2024-01-01")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 9
    for each_date in response_json:
        assert each_date["date"] == "2024-01-01"
