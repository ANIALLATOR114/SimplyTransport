import folium as fl
from SimplyTransport.domain.maps.maps import Map


def test_map_init():
    map_obj = Map()
    assert type(map_obj.map_base) is fl.Map
    assert map_obj.max_zoom == 20


def test_map_init_with_params():
    map_obj = Map(lat=53.0, lon=-7.0, zoom=10, max_zoom=15)
    assert map_obj.max_zoom == 15
    assert isinstance(map_obj.map_base, fl.Map)
    assert map_obj.map_base.location == [53.0, -7.0]


def test_map_add_fullscreen():
    map_obj = Map()
    map_obj.add_fullscreen()

    html = map_obj.render()
    assert "fullscreen" in html


def test_map_add_mouse_position():
    map_obj = Map()
    map_obj.add_mouse_position()

    html = map_obj.render()
    print(html)
    assert "MousePosition" in html


def test_map_add_tilelayer():
    map_obj = Map()
    map_obj.add_tilelayer()

    html = map_obj.render()
    assert "OpenStreetMap" in html


def test_map_add_tilelayer_with_params():
    map_obj = Map()
    map_obj.add_tilelayer(name="Test", tiles="Test", attribution="Test")

    html = map_obj.render()
    assert "Test" in html
    assert "Test" in html
    assert "Test" in html


def test_add_layer_control():
    map_obj = Map()
    map_obj.add_layer_control()

    html = map_obj.render()
    assert "layer_control" in html
