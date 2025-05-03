import folium as fl
import pytest
from SimplyTransport.domain.agency.model import AgencyModel
from SimplyTransport.domain.maps.colors import Colors
from SimplyTransport.domain.maps.polylines import RoutePolyLine
from SimplyTransport.domain.route.model import RouteModel


@pytest.fixture
def route():
    return RouteModel(id="123", short_name="Test Route", agency=AgencyModel(name="test"))


def test_route_polyline_init(route: RouteModel):
    polyline = RoutePolyLine(route, [(53.0, -7.0), (53.1, -7.1)])
    assert polyline.route.id == "123"
    assert polyline.route.short_name == "Test Route"
    assert polyline.route.agency.name == "test"
    assert polyline.locations == [(53.0, -7.0), (53.1, -7.1)]
    assert polyline.create_links is True
    assert polyline.weight == 8
    assert polyline.opacity == 1
    assert type(polyline.polyline) is fl.PolyLine


@pytest.mark.parametrize(
    "create_popup,expected_in_html",
    [
        (True, True),
        (False, False),
    ],
)
def test_route_polyline_popup(create_popup, expected_in_html, route: RouteModel):
    polyline = RoutePolyLine(
        route,
        [(53.0, -7.0), (53.1, -7.1)],
        create_popup=create_popup,
    )
    map = fl.Map()
    polyline.add_to(map)
    assert ("popup" in map._repr_html_()) is expected_in_html


@pytest.mark.parametrize(
    "create_links,expected_in_html",
    [
        (True, True),
        (False, False),
    ],
)
def test_route_polyline_link(create_links, expected_in_html, route: RouteModel):
    polyline = RoutePolyLine(
        route,
        [(53.0, -7.0), (53.1, -7.1)],
        create_popup=True,
        create_links=create_links,
    )
    figure = fl.Map()
    polyline.add_to(figure)
    html = figure._repr_html_()
    assert ("href=&#x27;/realtime/route/123/1&#x27;&gt;" in html) is expected_in_html


@pytest.mark.parametrize(
    "create_tooltip,expected_in_html",
    [
        (True, True),
        (False, False),
    ],
)
def test_route_polyline_tooltip(create_tooltip, expected_in_html, route: RouteModel):
    polyline = RoutePolyLine(
        route,
        [(53.0, -7.0), (53.1, -7.1)],
        create_tooltip=create_tooltip,
    )
    figure = fl.Map()
    polyline.add_to(figure)
    html = figure._repr_html_()
    assert ("Tooltip" in html) is expected_in_html


@pytest.mark.parametrize(
    "color",
    [
        Colors.RED,
        Colors.BLUE,
        Colors.GREEN,
        Colors.PURPLE,
        Colors.ORANGE,
        Colors.CADETBLUE,
        Colors.LIGHTBLUE,
    ],
)
def test_route_polyline_color(color: Colors, route: RouteModel):
    polyline = RoutePolyLine(route, [(1, 1)], route_color=color)
    map = fl.Map()
    polyline.add_to(map)
    html = map._repr_html_()
    assert color.value in html
