import folium as fl


class Layer:
    def __init__(self, name: str) -> None:
        """
        Initializes a new instance of the Layer class.

        Args:
            name (str): The name of the layer.

        Returns:
            None
        """
        self.name = name
        self.base_layer = fl.FeatureGroup(name=name)

    def add_to(self, map: fl.Map) -> None:
        """
        Adds the layer to the given map.

        Args:
            map (fl.Map): The map to add the layer to.

        Returns:
            None
        """
        self.base_layer.add_to(map)
