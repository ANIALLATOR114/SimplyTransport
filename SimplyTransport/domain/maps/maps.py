from pathlib import Path

import folium as fl
import folium.plugins as flp

ATTRIBUTION = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a>'


class Map:
    def __init__(
        self,
        height: int | None = None,
        lat: float = 53.44928237017178,
        lon: float = -7.514413484752406,
        zoom: int = 8,
        max_zoom: int = 20,
    ) -> None:
        """
        Initializes a Maps object.

        Args:
            height (int, optional): The height of the map in pixels. Defaults to None.
            If not provided the map will maintain 16:9 aspect ratio.
            lat (float, optional): The latitude of the map's center. Defaults to 53.44928237017178.
            lon (float, optional): The longitude of the map's center. Defaults to -7.514413484752406.
            zoom (int, optional): The initial zoom level of the map. Defaults to 8.
            max_zoom (int, optional): The maximum allowed zoom level of the map. Defaults to 20.
        """
        location = [lat, lon]

        if height:
            f = fl.Figure(height=height)
            self.map_base = fl.Map(
                location=location, zoom_start=zoom, prefer_canvas=True, max_zoom=max_zoom, tiles=None
            ).add_to(f)
        else:
            self.map_base = fl.Map(
                location=location, zoom_start=zoom, prefer_canvas=True, max_zoom=max_zoom, tiles=None
            )

        self.max_zoom = max_zoom

    def add_fullscreen(self) -> None:
        """
        Adds a fullscreen button to the map.

        :return: None
        """
        flp.Fullscreen(force_separate_button=True).add_to(self.map_base)

    def add_mouse_position(self) -> None:
        """
        This method adds a mouse position control to the map, which displays the current
        coordinates of the mouse cursor on the map.

        Returns:
            None
        """
        flp.MousePosition().add_to(self.map_base)

    def add_tilelayer(
        self,
        name: str = "Detailed",
        tiles: str = "OpenStreetMap",
        attribution: str | None = None,
        max_zoom: int | None = None,
    ) -> None:
        """
        Adds a tile layer to the map.

        Args:
            name (str): The name of the tile layer. Defaults to "Detailed".
            tiles (str): The type of tiles to use. Defaults to "OpenStreetMap".
            max_zoom (int): The maximum zoom level for the tile layer. If not provided, the maximum zoom
            level of the map will be used.

        Returns:
            None
        """
        if max_zoom is None:
            max_zoom = self.max_zoom
        fl.TileLayer(tiles, name=name, max_zoom=max_zoom, attr=attribution).add_to(self.map_base)

    def add_layer_control(self) -> None:
        """
        Adds a layer control to the map.

        Returns:
            None
        """
        fl.LayerControl(collapsed=False).add_to(self.map_base)

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
            name="Light",
            tiles="https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png",
            attribution=ATTRIBUTION,
        )
        self.add_tilelayer(
            name="Terrain",
            tiles="https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png",
            attribution=ATTRIBUTION,
        )
        self.add_tilelayer(
            name="Dark",
            tiles="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
            attribution=ATTRIBUTION,
        )

    def render(self) -> str:
        """
        Renders the map and returns it as an HTML string.

        Returns:
            str: The HTML representation of the map.
        """
        return self.map_base._repr_html_()  # type: ignore[no-any-return]

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

        self.map_base.save(path + filename + ".html")
