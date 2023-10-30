from httpx import AsyncClient


def test_calendar_date_all(client: AsyncClient)-> None:
    response = client.get("api/v1/calendardate/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 238
    assert response_json[0]["id"] == 3571
    assert response_json[0]["service_id"] == "27"
    assert response_json[0]["date"] == "2023-11-24"
    assert response_json[0]["exception_type"] == "added"
    assert response_json[0]["dataset"] == "TFI"


def test_calendar_date_all_and_count(client: AsyncClient)-> None:
    response = client.get("api/v1/calendardate/count")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 238
    assert len(response_json["calendar_dates"]) == 238


def test_get_calendar_date_by_id(client: AsyncClient)-> None:
    response = client.get("api/v1/calendardate/3571")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == 3571
    assert response_json["service_id"] == "27"
    assert response_json["date"] == "2023-11-24"
    assert response_json["exception_type"] == "added"
    assert response_json["dataset"] == "TFI"

    response = client.get("api/v1/calendardate/3572")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == 3572
    assert response_json["service_id"] == "124"
    assert response_json["date"] == "2023-10-30"
    assert response_json["exception_type"] == "removed"
    assert response_json["dataset"] == "TFI"


def test_get_active_calendar_dates_on_date(client: AsyncClient)-> None:
    response = client.get("api/v1/calendardate/date/2023-10-30")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 24
    assert response_json[0]["id"] == 3572
    assert response_json[0]["service_id"] == "124"
    assert response_json[0]["date"] == "2023-10-30"
    assert response_json[0]["exception_type"] == "removed"
    assert response_json[0]["dataset"] == "TFI"
    for each_date in response_json:
        assert each_date["date"] == "2023-10-30"

    response = client.get("api/v1/calendardate/date/2024-01-01")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 9
    assert response_json[0]["id"] == 3574
    assert response_json[0]["service_id"] == "154"
    assert response_json[0]["date"] == "2024-01-01"
    assert response_json[0]["exception_type"] == "removed"
    assert response_json[0]["dataset"] == "TFI"
    for each_date in response_json:
        assert each_date["date"] == "2024-01-01"