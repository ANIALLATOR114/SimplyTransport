import folium as fl


class Layer:
    def __init__(self, name: str):
        """
        Initialize a new Layer object.

        Args:
            name (str): The name of the layer.

        Returns:
            None
        """
        self.name = name
        self.base_layer = fl.FeatureGroup(name=name)

    def add_to(self, map: fl.Map):
        """
        Adds the layer to the given map.

        Args:
            map: The map to add the layer to.
        """
        self.base_layer.add_to(map)

    def add_child(self, child):
        """
        Adds a child object to the layer.

        Args:
            child: The child object to be added.

        Returns:
            None
        """
        self.base_layer.add_child(child)
