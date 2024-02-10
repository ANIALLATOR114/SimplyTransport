import folium as fl

from SimplyTransport.domain.maps.maps import Map


def test_map_init():
    map = Map()
    assert type(map.map) is fl.Map
    assert map.max_zoom == 20


def test_map_init_with_params():
    map = Map(lat=53.0, lon=-7.0, zoom=10, max_zoom=15)
    assert map.max_zoom == 15
    assert map.map.location == [53.0, -7.0]


def test_map_add_fullscreen():
    map = Map()
    map.add_fullscreen()

    html = map.render()
    assert "fullscreen" in html


def test_map_add_mouse_position():
    map = Map()
    map.add_mouse_position()

    html = map.render()
    print(html)
    assert "MousePosition" in html


def test_map_add_tilelayer():
    map = Map()
    map.add_tilelayer()

    html = map.render()
    assert "OpenStreetMap" in html
