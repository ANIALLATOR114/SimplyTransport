import math

from litestar.testing import TestClient


def test_get_shape_by_shape_id_asc(client: TestClient) -> None:
    response = client.get("/api/v1/shape/3623_278?orderBy=sequence&sortOrder=asc'")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1027

    assert response_json[0]["shape_id"] == "3623_278"
    assert math.isclose(response_json[0]["lat"], 53.2885228473561, abs_tol=1e-09)
    assert math.isclose(response_json[0]["lon"], -6.15376290729341, abs_tol=1e-09)
    assert response_json[0]["sequence"] == 1
    assert response_json[0]["distance"] == 0
    assert response_json[0]["dataset"] == "TFI"

    for i in range(1, len(response_json)):
        assert response_json[i]["sequence"] > response_json[i - 1]["sequence"]
        assert response_json[0]["shape_id"] == "3623_278"


def test_get_shape_by_shape_id_desc(client: TestClient) -> None:
    response = client.get("/api/v1/shape/3623_278?orderBy=sequence&sortOrder=desc")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1027

    assert response_json[0]["shape_id"] == "3623_278"
    assert math.isclose(response_json[0]["lat"], 53.2885228473561, abs_tol=1e-09)
    assert math.isclose(response_json[0]["lon"], -6.15376290729341, abs_tol=1e-09)
    assert response_json[0]["sequence"] == 1027
    assert math.isclose(response_json[0]["distance"], 20883.358, abs_tol=1e-09)
    assert response_json[0]["dataset"] == "TFI"

    for i in range(1, len(response_json)):
        assert response_json[i]["sequence"] < response_json[i - 1]["sequence"]
        assert response_json[0]["shape_id"] == "3623_278"


def test_get_shape_by_shape_id_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/shape/3623323_279?orderBy=sequence&sortOrder=asc'")
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Shapes not found with id 3623323_279"
