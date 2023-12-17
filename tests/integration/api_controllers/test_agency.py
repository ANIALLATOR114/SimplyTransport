from litestar.testing import TestClient


def test_agency_list_all(client: TestClient) -> None:
    response = client.get("api/v1/agency/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 7
    assert response_json[0]["id"] == "7778006"
    assert response_json[0]["name"] == "Go-Ahead Ireland"
    assert response_json[0]["url"] == "https://www.goaheadireland.ie/"
    assert response_json[0]["timezone"] == "Europe/London"
    assert response_json[0]["dataset"] == "TFI"


def test_agency_list_all_and_count(client: TestClient) -> None:
    response = client.get("api/v1/agency/count")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 7
    assert len(response_json["agencies"]) == 7
    assert response_json["agencies"][0]["id"] == "7778006"
    assert response_json["agencies"][0]["name"] == "Go-Ahead Ireland"
    assert response_json["agencies"][0]["url"] == "https://www.goaheadireland.ie/"
    assert response_json["agencies"][0]["timezone"] == "Europe/London"
    assert response_json["agencies"][0]["dataset"] == "TFI"


def test_agency_get_by_id(client: TestClient) -> None:
    response = client.get("api/v1/agency/7778006")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == "7778006"
    assert response_json["name"] == "Go-Ahead Ireland"
    assert response_json["url"] == "https://www.goaheadireland.ie/"
    assert response_json["timezone"] == "Europe/London"
    assert response_json["dataset"] == "TFI"


def test_agency_get_by_id_not_found(client: TestClient) -> None:
    response = client.get("api/v1/agency/7778007")
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Agency not found with id 7778007"
