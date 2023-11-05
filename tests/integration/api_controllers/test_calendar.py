from httpx import AsyncClient


def test_calendar_all(client: AsyncClient) -> None:
    response = client.get("api/v1/calendar/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 117
    assert response_json[0]["id"] == "27"
    assert response_json[0]["monday"] == 0
    assert response_json[0]["tuesday"] == 0
    assert response_json[0]["wednesday"] == 0
    assert response_json[0]["thursday"] == 0
    assert response_json[0]["friday"] == 0
    assert response_json[0]["saturday"] == 0
    assert response_json[0]["sunday"] == 0
    assert response_json[0]["start_date"] == "2023-11-24"
    assert response_json[0]["end_date"] == "2023-11-24"
    assert response_json[0]["dataset"] == "TFI"


def test_calendar_all_and_count(client: AsyncClient) -> None:
    response = client.get("api/v1/calendar/count")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 117
    assert len(response_json["calendars"]) == 117


def test_get_calendar_by_id(client: AsyncClient) -> None:
    response = client.get("api/v1/calendar/27")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == "27"
    assert response_json["monday"] == 0
    assert response_json["tuesday"] == 0
    assert response_json["wednesday"] == 0
    assert response_json["thursday"] == 0
    assert response_json["friday"] == 0
    assert response_json["saturday"] == 0
    assert response_json["sunday"] == 0
    assert response_json["start_date"] == "2023-11-24"
    assert response_json["end_date"] == "2023-11-24"
    assert response_json["dataset"] == "TFI"

    response = client.get("api/v1/calendar/94")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == "94"
    assert response_json["monday"] == 0
    assert response_json["tuesday"] == 0
    assert response_json["wednesday"] == 0
    assert response_json["thursday"] == 0
    assert response_json["friday"] == 0
    assert response_json["saturday"] == 1
    assert response_json["sunday"] == 0
    assert response_json["start_date"] == "2023-10-14"
    assert response_json["end_date"] == "2023-10-14"
    assert response_json["dataset"] == "TFI"


def test_get_calendars_active_on_date(client: AsyncClient) -> None:
    response = client.get("api/v1/calendar/date/2023-11-24")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 84
    assert response_json[0]["id"] == "27"
    assert response_json[0]["monday"] == 0
    assert response_json[0]["tuesday"] == 0
    assert response_json[0]["wednesday"] == 0
    assert response_json[0]["thursday"] == 0
    assert response_json[0]["friday"] == 0
    assert response_json[0]["saturday"] == 0
    assert response_json[0]["sunday"] == 0
    assert response_json[0]["start_date"] == "2023-11-24"
    assert response_json[0]["end_date"] == "2023-11-24"
    assert response_json[0]["dataset"] == "TFI"
