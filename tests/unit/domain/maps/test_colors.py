from SimplyTransport.domain.maps.colors import Colors


def test_to_hex():
    assert Colors.RED.to_hex() == "#d32f2f"
    assert Colors.BLUE.to_hex() == "#1565c0"
