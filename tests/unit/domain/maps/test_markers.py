from SimplyTransport.domain.maps.markers import BusMarker, StopMarker, MarkerColors
import folium as fl

import pytest

def test_stop_marker_init():
    stop = StopMarker("Test Stop", "test_stop_id", "test_stop_code", 53.0, -7.0)
    assert stop.stop_name == "Test Stop"
    assert stop.stop_id == "test_stop_id"
    assert stop.stop_code == "test_stop_code"
    assert stop.lat == 53.0
    assert stop.lon == -7.0
    assert stop.create_links is True
    assert stop.color is None
    assert type(stop.popup) is fl.Popup
    assert type(stop.tooltip) is fl.Tooltip
    assert type(stop.icon) is fl.Icon


@pytest.mark.parametrize("create_links,expected_in_html", [
    (False, False),
    (True, True)
])
def test_stop_marker_links(create_links, expected_in_html):
    stop = StopMarker("Test Stop", "test_stop_id", "test_stop_code", 53.0, -7.0, create_links=create_links)
    assert stop.create_links is create_links
    assert ("href" in stop.popup.html.render()) is expected_in_html


@pytest.mark.parametrize("color", [
    MarkerColors.RED,
    MarkerColors.BLUE,
    MarkerColors.GREEN,
    MarkerColors.PURPLE,
    MarkerColors.ORANGE,
    MarkerColors.DARKRED,
    MarkerColors.LIGHTRED,
    MarkerColors.DARKBLUE,
    MarkerColors.LIGHTBLUE,
    MarkerColors.DARKGREEN,
    MarkerColors.LIGHTGREEN,
    MarkerColors.DARKPURPLE,
    MarkerColors.PINK,
    MarkerColors.CADETBLUE,
    MarkerColors.BEIGE,
    MarkerColors.WHITE,
    MarkerColors.GRAY,
    MarkerColors.LIGHTGRAY,
    MarkerColors.BLACK,
    None
])
def test_stop_marker_color(color):
    stop = StopMarker("Test Stop", "test_stop_id", "test_stop_code", 53.0, -7.0, color=color)
    assert stop.color == color
    assert type(stop.icon) is fl.Icon


def test_bus_marker_init():
    bus = BusMarker("Test Bus", "test_bus_id", "test_operator", 53.0, -7.0)
    assert bus.route_name == "Test Bus"
    assert bus.route_id == "test_bus_id"
    assert bus.operator_name == "test_operator"
    assert bus.lat == 53.0
    assert bus.lon == -7.0
    assert bus.color is None
    assert type(bus.icon) is fl.Icon
    assert type(bus.popup) is fl.Popup
    assert type(bus.tooltip) is fl.Tooltip


@pytest.mark.parametrize("create_links,expected_in_html", [
    (False, False),
    (True, True)
])
def test_bus_marker_links(create_links, expected_in_html):
    bus = BusMarker("Test Bus", "test_bus_id", "test_operator", 53.0, -7.0, create_links=create_links)
    assert bus.create_links is create_links
    assert ("href" in bus.popup.html.render()) is expected_in_html

@pytest.mark.parametrize("color", [
    MarkerColors.RED,
    MarkerColors.BLUE,
    MarkerColors.GREEN,
    MarkerColors.PURPLE,
    MarkerColors.ORANGE,
    MarkerColors.DARKRED,
    MarkerColors.LIGHTRED,
    MarkerColors.DARKBLUE,
    MarkerColors.LIGHTBLUE,
    MarkerColors.DARKGREEN,
    MarkerColors.LIGHTGREEN,
    MarkerColors.DARKPURPLE,
    MarkerColors.PINK,
    MarkerColors.CADETBLUE,
    MarkerColors.BEIGE,
    MarkerColors.WHITE,
    MarkerColors.GRAY,
    MarkerColors.LIGHTGRAY,
    MarkerColors.BLACK,
    None
])
def test_bus_marker_color(color):
    stop = BusMarker("Test Bus", "test_bus_id", "test_operator", 53.0, -7.0, color=color)
    assert stop.color == color
    assert type(stop.icon) is fl.Icon