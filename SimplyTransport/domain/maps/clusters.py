import folium as fl

from folium.plugins import MarkerCluster

class Cluster:
    def __init__(self, name: str = "Cluster") -> None:
        """
        Initialize a Cluster object.

        Args:
            name (str, optional): The name of the cluster. Defaults to "Cluster".
        """

        self.name = name
        self.create_cluster()

    def create_cluster(self) -> None:
        """
        Creates a cluster.

        Returns:
        - None
        """
        self.cluster = MarkerCluster(name=self.name)

    
    def add_to(self, map: fl.Map) -> None:
        """
        Adds the cluster to the map.

        Args:
        - map (fl.Map): The map to add the cluster to.

        Returns:
        - None
        """
        self.cluster.add_to(map)

    
    def add_marker(self, marker: fl.Marker) -> None:
        """
        Adds a marker to the cluster.

        Args:
        - marker (fl.Marker): The marker to add to the cluster.

        Returns:
        - None
        """
        marker.add_to(self.cluster)