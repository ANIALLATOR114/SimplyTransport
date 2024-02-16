import math
from SimplyTransport.domain.maps.markers import BusMarker, StopMarker, MarkerColors
import folium as fl

import pytest

from SimplyTransport.domain.stop.model import StopModel


@pytest.fixture
def stop():
    return StopModel(id="test_stop_id", name="Test Stop", lat=53.0, lon=-7.0)


def test_stop_marker_init(stop: StopModel):
    marker = StopMarker(stop, [])
    assert marker.stop.id == "test_stop_id"
    assert marker.stop.name == "Test Stop"
    assert math.isclose(marker.stop.lon, -7.0, abs_tol=1e-09)
    assert math.isclose(marker.stop.lat, 53.0, abs_tol=1e-09)
    assert marker.create_link is True
    assert marker.color is None
    assert type(marker.popup) is fl.Popup
    assert type(marker.tooltip) is fl.Tooltip
    assert type(marker.icon) is fl.Icon


@pytest.mark.parametrize("create_links", [(False), (True)])
def test_stop_marker_links(create_links, stop: StopModel):
    marker = StopMarker(stop, create_link=create_links)
    assert marker.create_link is create_links


@pytest.mark.parametrize(
    "color",
    [
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
        None,
    ],
)
def test_stop_marker_color(color: MarkerColors, stop: StopModel):
    marker = StopMarker(stop, color=color)
    assert marker.color == color
    assert type(marker.icon) is fl.Icon


def test_bus_marker_init():
    bus = BusMarker("Test Bus", "test_bus_id", "test_operator", 53.0, -7.0)
    assert bus.route_name == "Test Bus"
    assert bus.route_id == "test_bus_id"
    assert bus.operator_name == "test_operator"
    assert math.isclose(bus.lon, -7.0, abs_tol=1e-09)
    assert math.isclose(bus.lat, 53.0, abs_tol=1e-09)
    assert bus.color is None
    assert type(bus.icon) is fl.Icon
    assert type(bus.popup) is fl.Popup
    assert type(bus.tooltip) is fl.Tooltip


@pytest.mark.parametrize("create_links,expected_in_html", [(False, False), (True, True)])
def test_bus_marker_links(create_links, expected_in_html):
    bus = BusMarker("Test Bus", "test_bus_id", "test_operator", 53.0, -7.0, create_links=create_links)
    assert bus.create_links is create_links
    assert ("href" in bus.popup.html.render()) is expected_in_html


@pytest.mark.parametrize(
    "color",
    [
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
        None,
    ],
)
def test_bus_marker_color(color):
    stop = BusMarker("Test Bus", "test_bus_id", "test_operator", 53.0, -7.0, color=color)
    assert stop.color == color
    assert type(stop.icon) is fl.Icon
