from SimplyTransport.domain.maps.layers import Layer
import folium as fl


def test_init_layer():
    layer = Layer(name="test_layer")
    assert layer.name == "test_layer"
    assert type(layer.layer) is fl.FeatureGroup
