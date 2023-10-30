from httpx import AsyncClient


def test_route_all(client: AsyncClient)-> None:
    response = client.get("api/v1/route/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2
    assert response_json[0]["id"] == "3623_54684"
    assert response_json[0]["agency_id"] == "7778019"
    assert response_json[0]["short_name"] == "4"
    assert response_json[0]["long_name"] == "Monkstown Avenue - Harristown"
    assert response_json[0]["description"] == ""
    assert response_json[0]["route_type"] == 3
    assert response_json[0]["url"] == ""
    assert response_json[0]["color"] == ""
    assert response_json[0]["text_color"] == ""
    assert response_json[0]["dataset"] == "TFI"

    assert response_json[1]["id"] == "3623_54691"
    assert response_json[1]["agency_id"] == "7778019"
    assert response_json[1]["short_name"] == "9"
    assert response_json[1]["long_name"] == "Limekiln Avenue - Charelstown"
    assert response_json[1]["description"] == ""
    assert response_json[1]["route_type"] == 3
    assert response_json[1]["url"] == ""
    assert response_json[1]["color"] == ""
    assert response_json[1]["text_color"] == ""
    assert response_json[1]["dataset"] == "TFI"


def test_route_filtered_by_agency_id(client: AsyncClient)-> None:
    response = client.get("api/v1/route/?agency_id=7778019")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2
    assert response_json[0]["id"] == "3623_54684"
    assert response_json[0]["agency_id"] == "7778019"
    assert response_json[0]["short_name"] == "4"
    assert response_json[0]["long_name"] == "Monkstown Avenue - Harristown"
    assert response_json[0]["description"] == ""
    assert response_json[0]["route_type"] == 3
    assert response_json[0]["url"] == ""
    assert response_json[0]["color"] == ""
    assert response_json[0]["text_color"] == ""
    assert response_json[0]["dataset"] == "TFI"

    assert response_json[1]["id"] == "3623_54691"
    assert response_json[1]["agency_id"] == "7778019"
    assert response_json[1]["short_name"] == "9"
    assert response_json[1]["long_name"] == "Limekiln Avenue - Charelstown"
    assert response_json[1]["description"] == ""
    assert response_json[1]["route_type"] == 3
    assert response_json[1]["url"] == ""
    assert response_json[1]["color"] == ""
    assert response_json[1]["text_color"] == ""
    assert response_json[1]["dataset"] == "TFI"


def test_route_filtered_by_agency_id_not_found(client: AsyncClient)-> None:
    response = client.get("api/v1/route/?agencyId=7778801877788018")
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Routes not found with agency id 7778801877788018"


def test_all_route_and_count(client: AsyncClient)-> None:
    response = client.get("api/v1/route/count")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 2
    assert len(response_json["routes"]) == 2

def test_all_route_and_count_by_agency_id(client: AsyncClient)-> None:
    response = client.get("api/v1/route/count?agency_id=7778019")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total"] == 2
    assert len(response_json["routes"]) == 2

def test_all_route_and_count_by_agency_id_not_found(client: AsyncClient)-> None:
    response = client.get("api/v1/route/count?agencyId=7778801877788018")
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Routes not found with agency id 7778801877788018"

def test_get_route_by_id(client: AsyncClient)-> None:
    response = client.get("api/v1/route/3623_54684")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == "3623_54684"
    assert response_json["agency_id"] == "7778019"
    assert response_json["short_name"] == "4"
    assert response_json["long_name"] == "Monkstown Avenue - Harristown"
    assert response_json["description"] == ""
    assert response_json["route_type"] == 3
    assert response_json["url"] == ""
    assert response_json["color"] == ""
    assert response_json["text_color"] == ""
    assert response_json["dataset"] == "TFI"

    response = client.get("api/v1/route/3623_54691")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == "3623_54691"
    assert response_json["agency_id"] == "7778019"
    assert response_json["short_name"] == "9"
    assert response_json["long_name"] == "Limekiln Avenue - Charelstown"
    assert response_json["description"] == ""
    assert response_json["route_type"] == 3
    assert response_json["url"] == ""
    assert response_json["color"] == ""
    assert response_json["text_color"] == ""
    assert response_json["dataset"] == "TFI"

def test_get_route_by_id_not_found(client: AsyncClient)-> None:
    response = client.get("api/v1/route/3623_54691_")
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Route not found with id 3623_54691_"