import folium as fl

from SimplyTransport.domain.maps.layers import Layer
from SimplyTransport.domain.maps.maps import Map

LAYER_NAME = "TestLayer"

def test_layer_init():
    layer = Layer(name=LAYER_NAME)
    assert layer.name == LAYER_NAME
    assert type(layer.base_layer) is fl.FeatureGroup


def test_layer_add_to():
    layer = Layer(name=LAYER_NAME)
    name_of_layer = layer.base_layer.get_name()
    map_obj = Map()
    layer.add_to(map_obj.map_base)

    html = map_obj.render()
    assert name_of_layer in html