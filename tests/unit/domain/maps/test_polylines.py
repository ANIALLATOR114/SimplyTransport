from SimplyTransport.domain.maps.polylines import PolyLineColors, RoutePolyLine
import folium as fl

import pytest

def test_route_polyline_init():
    route = RoutePolyLine("test_route_id", "Test Route", "Test Operator", [(53.0, -7.0), (53.1, -7.1)])
    assert route.route_id == "test_route_id"
    assert route.route_name == "Test Route"
    assert route.route_operator == "Test Operator"
    assert route.locations == [(53.0, -7.0), (53.1, -7.1)]
    assert route.create_links is True
    assert route.weight == 6
    assert route.opacity == 1
    assert type(route.polyline) is fl.PolyLine


@pytest.mark.parametrize("create_popup,expected_in_html", [
    (True, True),
    (False, False),
])
def test_route_polyline_popup(create_popup,expected_in_html):
    route = RoutePolyLine("test_route_id", "Test Route", "Test Operator", [(53.0, -7.0), (53.1, -7.1)], create_popup=create_popup)
    figure = fl.Figure()
    route.add_to(figure)
    html = figure.render()
    assert ("popup" in html) is expected_in_html


@pytest.mark.parametrize("create_link,expected_in_html", [
    (True, True),
    (False, False),
])
def test_route_polyline_link(create_link,expected_in_html):
    route = RoutePolyLine("test_route_id", "Test Route", "Test Operator", [(53.0, -7.0), (53.1, -7.1)], create_popup=True, create_links=create_link)
    figure = fl.Figure()
    route.add_to(figure)
    html = figure.render()
    assert ("href" in html) is expected_in_html


@pytest.mark.parametrize("create_tooltip,expected_in_html", [
    (True, True),
    (False, False),
])
def test_route_polyline_tooltip(create_tooltip,expected_in_html):
    route = RoutePolyLine("test_route_id", "Test Route", "Test Operator", [(53.0, -7.0), (53.1, -7.1)], create_tooltip=create_tooltip)
    figure = fl.Figure()
    route.add_to(figure)
    html = figure.render()
    print(html)
    assert ("Tooltip" in html) is expected_in_html


@pytest.mark.parametrize("color", [
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
])
def test_route_polyline_color(color: PolyLineColors):
    route = RoutePolyLine("test_route_id", "Test Route", "Test Operator", [(53.0, -7.0), (53.1, -7.1)], route_color=color)
    figure = fl.Figure()
    route.add_to(figure)
    html = figure.render()
    assert color.value in html
