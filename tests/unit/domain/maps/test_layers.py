import folium as fl
from SimplyTransport.domain.maps.layers import Layer


def test_init_layer():
    layer = Layer(name="test_layer")
    assert layer.name == "test_layer"
    assert type(layer.base_layer) is fl.FeatureGroup
