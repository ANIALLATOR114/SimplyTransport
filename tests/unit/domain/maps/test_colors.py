from SimplyTransport.domain.maps.colors import Colors


def test_to_hex():
    assert Colors.RED.to_hex() == "#ff0000"
    assert Colors.BLUE.to_hex() == "#3388ff"
