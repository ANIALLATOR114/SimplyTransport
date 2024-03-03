import datetime
import math
from SimplyTransport.domain.agency.model import AgencyModel
from SimplyTransport.domain.maps.colors import Colors
from SimplyTransport.domain.maps.markers import BusMarker, StopMarker
import folium as fl

import pytest
from SimplyTransport.domain.realtime.vehicle.model import RTVehicleModel
from SimplyTransport.domain.route.model import RouteModel

from SimplyTransport.domain.stop.model import StopModel
from SimplyTransport.domain.trip.model import TripModel


@pytest.fixture
def stop():
    return StopModel(id="test_stop_id", name="Test Stop", lat=53.0, lon=-7.0)


@pytest.fixture
def realtime_vehicle():
    return RTVehicleModel(
        vehicle_id="test_vehicle_id",
        time_of_update=datetime.datetime.strptime("2022-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
        lat=53.0,
        lon=-7.0,
        trip=TripModel(route=RouteModel(short_name="Test Route", agency=AgencyModel(name="Test Agency"))),
    )


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
        Colors.RED,
        Colors.BLUE,
        Colors.GREEN,
        Colors.PURPLE,
        Colors.ORANGE,
        Colors.LIGHTBLUE,
        Colors.PINK,
        Colors.CADETBLUE,
        None,
    ],
)
def test_stop_marker_color(color: Colors, stop: StopModel):
    marker = StopMarker(stop, color=color)
    assert marker.color == color
    assert type(marker.icon) is fl.Icon


@pytest.mark.parametrize("marker_type,expected", [("regular", fl.Marker), ("circle", fl.CircleMarker)])
def test_stop_marker_create_marker(stop: StopModel, marker_type: str, expected: fl.Marker | fl.CircleMarker):
    marker = StopMarker(stop, [])
    assert type(marker.create_marker(type_of_marker=marker_type)) is expected


def test_bus_marker_init(realtime_vehicle: RTVehicleModel):
    bus = BusMarker(realtime_vehicle)
    assert bus.vehicle.vehicle_id == "test_vehicle_id"
    assert bus.vehicle.time_of_update == datetime.datetime.strptime(
        "2022-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"
    )
    assert math.isclose(bus.vehicle.lon, -7.0, abs_tol=1e-09)
    assert math.isclose(bus.vehicle.lat, 53.0, abs_tol=1e-09)
    assert bus.color is None
    assert type(bus.icon) is fl.Icon
    assert type(bus.popup) is fl.Popup
    assert type(bus.tooltip) is fl.Tooltip


@pytest.mark.parametrize("create_links,expected_in_html", [(False, False), (True, True)])
def test_bus_marker_links(create_links: bool, expected_in_html: bool, realtime_vehicle: RTVehicleModel):
    bus = BusMarker(vehicle=realtime_vehicle, create_links=create_links)
    assert bus.create_links is create_links
    assert ("href" in bus.popup.html.render()) is expected_in_html


@pytest.mark.parametrize(
    "color",
    [
        Colors.RED,
        Colors.BLUE,
        Colors.GREEN,
        Colors.PURPLE,
        Colors.ORANGE,
        Colors.LIGHTBLUE,
        Colors.PINK,
        Colors.CADETBLUE,
        None,
    ],
)
def test_bus_marker_color(color: Colors, realtime_vehicle: RTVehicleModel):
    stop = BusMarker(vehicle=realtime_vehicle, color=color)
    assert stop.color == color
    assert type(stop.icon) is fl.Icon


def test_bus_marker_create_marker(realtime_vehicle: RTVehicleModel):
    bus = BusMarker(realtime_vehicle)
    assert type(bus.create_marker()) is fl.Marker
