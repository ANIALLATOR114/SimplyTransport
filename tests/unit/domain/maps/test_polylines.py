import folium as fl
import pytest
from SimplyTransport.domain.agency.model import AgencyModel
from SimplyTransport.domain.maps.polylines import PolyLineColors, RoutePolyLine
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
    figure = fl.Figure()
    polyline.add_to(figure)
    html = figure.render()
    assert ("popup" in html) is expected_in_html


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
    figure = fl.Figure()
    polyline.add_to(figure)
    html = figure.render()
    assert ("href" in html) is expected_in_html


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
    figure = fl.Figure()
    polyline.add_to(figure)
    html = figure.render()
    print(html)
    assert ("Tooltip" in html) is expected_in_html


@pytest.mark.parametrize(
    "color",
    [
        PolyLineColors.RED,
        PolyLineColors.BLUE,
        PolyLineColors.GREEN,
        PolyLineColors.PURPLE,
        PolyLineColors.ORANGE,
        PolyLineColors.DARKRED,
        PolyLineColors.LIGHTRED,
        PolyLineColors.DARKBLUE,
        PolyLineColors.LIGHTBLUE,
        PolyLineColors.DARKGREEN,
        PolyLineColors.LIGHTGREEN,
        PolyLineColors.DARKPURPLE,
        PolyLineColors.PINK,
        PolyLineColors.CADETBLUE,
        PolyLineColors.BEIGE,
        PolyLineColors.WHITE,
        PolyLineColors.GRAY,
        PolyLineColors.LIGHTGRAY,
        PolyLineColors.BLACK,
    ],
)
def test_route_polyline_color(color: PolyLineColors, route: RouteModel):
    polyline = RoutePolyLine(route, [(1, 1)], route_color=color)
    figure = fl.Figure()
    polyline.add_to(figure)
    html = figure.render()
    assert color.value in html
