import folium as fl
import folium.plugins as flp
from pathlib import Path


class Map:
    def __init__(
        self,
        lat: float = 53.44928237017178,
        lon: float = -7.514413484752406,
        zoom: int = 8,
        max_zoom: int = 20,
    ) -> None:
        """
        Initializes a Map object with the specified latitude, longitude, and zoom level.

        Parameters:
        - lat (float): The latitude of the map center. Default is 53.44928237017178.
        - lon (float): The longitude of the map center. Default is -7.514413484752406.
        - zoom (int): The zoom level of the map. Default is 8.
        """
        location = [lat, lon]
        self.map = fl.Map(
            location=location, zoom_start=zoom, prefer_canvas=True, max_zoom=max_zoom, tiles=None
        )
        self.max_zoom = max_zoom

    def add_fullscreen(self) -> None:
        """
        Adds a fullscreen button to the map.

        :return: None
        """
        flp.Fullscreen(force_separate_button=True).add_to(self.map)

    def add_mouse_position(self) -> None:
        """
        This method adds a mouse position control to the map, which displays the current
        coordinates of the mouse cursor on the map.

        Returns:
            None
        """
        flp.MousePosition().add_to(self.map)

    def add_tilelayer(
        self,
        name: str = "Detailed",
        tiles: str = "OpenStreetMap",
        attribution: str = None,
        max_zoom: int = None,
    ) -> None:
        """
        Adds a tile layer to the map.

        Args:
            name (str): The name of the tile layer. Defaults to "Detailed".
            tiles (str): The type of tiles to use. Defaults to "OpenStreetMap".
            max_zoom (int): The maximum zoom level for the tile layer. If not provided, the maximum zoom level of the map will be used.

        Returns:
            None
        """
        if max_zoom is None:
            max_zoom = self.max_zoom
        fl.TileLayer(tiles, name=name, max_zoom=max_zoom, attr=attribution).add_to(self.map)

    def add_layer_control(self) -> None:
        """
        Adds a layer control to the map.

        Returns:
            None
        """
        fl.LayerControl(collapsed=False).add_to(self.map)

    def setup_defaults(self) -> None:
        """
        Sets up the default settings for the map service.

        Returns:
            None
        """
        self.add_fullscreen()
        self.add_mouse_position()
        self.add_tilelayer()
        self.add_tilelayer(
            name="Dark",
            tiles="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
        )
        self.add_tilelayer(
            name="Light",
            tiles="https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png",
            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
        )
        self.add_tilelayer(
            name="Terrain",
            tiles="https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png",
            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
        )

    def render(self) -> str:
        """
        Renders the map and returns it as an HTML string.

        Returns:
            str: The HTML representation of the map.
        """
        return self.map._repr_html_()

    def save(self, path: str, filename: str) -> None:
        """
        Save the map as an HTML file.

        Args:
            path (str): The path where the file should be saved.
            filename (str): The name of the file (without extension).

        Returns:
            None
        """
        check_if_file_exists = Path(path + filename + ".html")
        check_if_file_exists.touch(exist_ok=True)

        self.map.save(path + filename + ".html")
