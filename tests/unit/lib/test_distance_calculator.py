import pytest
from SimplyTransport.lib.distance_calculator import calculate_min_max_coordinates, distance_between_points


@pytest.mark.parametrize(
    "test_case",
    [
        pytest.param(
            {"point1": (0, 0), "point2": (0, 0), "expected_meters": 0, "description": "Same point"},
            id="same_point",
        ),
        pytest.param(
            {
                "point1": (53.34689, -6.25913),  # O'Connell Bridge
                "point2": (53.34337, -6.25614),  # Trinity College
                "expected_meters": 439,
                "description": "O'Connell Bridge to Trinity College",
            },
            id="dublin_landmarks",
        ),
        pytest.param(
            {
                "point1": (53.34689, -6.25913),
                "point2": (53.34691, -6.25915),
                "expected_meters": 3,
                "description": "Very close points (~10m apart)",
            },
            id="close_points",
        ),
        pytest.param(
            {
                "point1": (90, 0),  # North pole
                "point2": (-90, 0),  # South pole
                "expected_meters": 20015087,
                "description": "Poles (half earth circumference)",
            },
            id="antipodes",
        ),
    ],
)
def test_distance_between_points(test_case):
    """Test distance calculations between geographical points."""
    lat1, lon1 = test_case["point1"]
    lat2, lon2 = test_case["point2"]
    expected = test_case["expected_meters"]

    actual = round(distance_between_points(lat1, lon1, lat2, lon2))

    assert actual == expected, f"Failed: {test_case['description']}"


@pytest.mark.parametrize(
    "test_case",
    [
        pytest.param(
            {
                "center": (53.34689, -6.25913),  # O'Connell Bridge
                "distance_meters": 500,  # 500m radius
                "expected": {
                    "min_lat": 53.34239,
                    "max_lat": 53.35139,
                    "min_lon": -6.26666,
                    "max_lon": -6.25160,
                },
                "description": "500m radius around O'Connell Bridge",
            },
            id="dublin_500m",
        ),
        pytest.param(
            {
                "center": (0, 0),  # Equator intersection with Greenwich
                "distance_meters": 1000,  # 1km radius
                "expected": {
                    "min_lat": -0.00899,
                    "max_lat": 0.00899,
                    "min_lon": -0.00899,
                    "max_lon": 0.00899,
                },
                "description": "1km radius at equator intersection",
            },
            id="equator_1km",
        ),
    ],
)
def test_calculate_min_max_coordinates(test_case):
    """Test bounding box calculations for different locations and distances."""
    lat, lon = test_case["center"]
    distance = test_case["distance_meters"]
    expected = test_case["expected"]

    result = calculate_min_max_coordinates(lat, lon, distance)

    # Round to 5 decimal places for comparison
    assert round(result.min_latitude, 5) == round(expected["min_lat"], 5), (
        f"Min latitude mismatch: {test_case['description']}"
    )
    assert round(result.max_latitude, 5) == round(expected["max_lat"], 5), (
        f"Max latitude mismatch: {test_case['description']}"
    )
    assert round(result.min_longitude, 5) == round(expected["min_lon"], 5), (
        f"Min longitude mismatch: {test_case['description']}"
    )
    assert round(result.max_longitude, 5) == round(expected["max_lon"], 5), (
        f"Max longitude mismatch: {test_case['description']}"
    )

    # Verify the box size is reasonable
    lat_diff = result.max_latitude - result.min_latitude
    lon_diff = result.max_longitude - result.min_longitude

    # Box should be roughly square
    assert abs(lat_diff - lon_diff) < 0.01, f"Box should be roughly square: {test_case['description']}"
