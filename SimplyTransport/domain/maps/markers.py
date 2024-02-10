import folium as fl

from enum import Enum


class MarkerColors(Enum):
    RED = "red"
    DARKRED = "darkred"
    LIGHTRED = "lightred"
    ORANGE = "orange"
    BEIGE = "beige"
    GREEN = "green"
    DARKGREEN = "darkgreen"
    LIGHTGREEN = "lightgreen"
    BLUE = "blue"
    DARKBLUE = "darkblue"
    CADETBLUE = "cadetblue"
    LIGHTBLUE = "lightblue"
    PURPLE = "purple"
    DARKPURPLE = "darkpurple"
    PINK = "pink"
    WHITE = "white"
    GRAY = "gray"
    LIGHTGRAY = "lightgray"
    BLACK = "black"


class StopMarker:
    def __init__(
        self,
        stop_name: str,
        stop_id: str,
        stop_code: str,
        lat: float,
        lon: float,
        create_links: bool = True,
        color: MarkerColors = None,
    ) -> None:
        """
        Initialize a StopMarker object.

        Args:
            stop_name (str): The name of the stop.
            stop_id (str): The ID of the stop.
            stop_code (str): The code of the stop.
            lat (float): The latitude of the stop.
            lon (float): The longitude of the stop.
            create_links (bool): Whether to create links in the popup. Default is True.
            color (MarkerColors): The color of the marker. Default is None.
        """
        self.stop_name = stop_name
        self.stop_id = stop_id
        self.stop_code = stop_code
        self.lat = lat
        self.lon = lon
        self.create_links = create_links
        self.color = color
        self.create_popup()
        self.create_tooltip()
        self.create_icon()

    def create_popup(self) -> None:
        """
        Creates a popup for the stop marker.

        Returns:
        - None
        """
        if self.create_links:
            self.popup = fl.Popup(
                f"""
                <h4 style='white-space: nowrap;'>
                    <a target='_parent' href='/realtime/stop/{self.stop_id}'>
                        {self.stop_code} - {self.stop_name}
                    </a>
                </h4>
                <p>
                    Lat: {self.lat}<br>
                    Lon: {self.lon}
                </p>
            """
            )
        else:
            self.popup = fl.Popup(
                f"""
                <h4 style='white-space: nowrap;'>
                    {self.stop_code} - {self.stop_name}
                </h4>
                <p>
                    Lat: {self.lat}<br>
                    Lon: {self.lon}
                </p>
            """
            )

    def create_tooltip(self) -> None:
        """
        Creates a tooltip for the stop marker.

        Returns:
        - None
        """
        self.tooltip = fl.Tooltip(
            f"""
            <h5>
                {self.stop_code} - {self.stop_name}
            </h5>
        """
        )

    def create_icon(self) -> None:
        """
        Creates an icon for the stop marker.

        Returns:
        - None
        """
        if self.color is not None:
            self.icon = fl.Icon(
                color=self.color.value, icon="fa-chevron-circle-down", prefix="fa"
            )
        else:
            self.icon = fl.Icon(
                color="blue", icon="fa-chevron-circle-down", prefix="fa"
            )

    def add_to(
        self, map: fl.Map, type_of_marker: str = "regular", radius: float = 9
    ) -> None:
        """
        Adds a marker to the given map.

        Parameters:
        - map: The map to add the marker to.
        - type_of_marker: The type of marker to add. Defaults to "regular".

        Returns:
        None
        """
        if type_of_marker == "circle":
            fl.CircleMarker(
                [self.lat, self.lon],
                color="#000",
                tooltip=self.tooltip,
                popup=self.popup,
                icon=self.icon,
                fill_color="#ccc",
                fill_opacity=1,
                radius=radius,
                weight=4,
                opacity=1,
            ).add_to(map)
        else:
            fl.Marker(
                [self.lat, self.lon],
                tooltip=self.tooltip,
                popup=self.popup,
                icon=self.icon,
            ).add_to(map)


class BusMarker:
    def __init__(
        self,
        route_name: str,
        route_id: str,
        operator_name: str,
        lat: float,
        lon: float,
        create_links: bool = True,
        color: MarkerColors = None,
    ) -> None:
        self.route_name = route_name
        self.route_id = route_id
        self.operator_name = operator_name
        self.lat = lat
        self.lon = lon
        self.create_links = create_links
        self.color = color
        self.create_popup()
        self.create_tooltip()
        self.create_icon()

    def create_popup(self) -> None:
        """
        Creates a popup for the bus marker.

        Returns:
        - None
        """
        if self.create_links:
            self.popup = fl.Popup(
                f"""
                <h4 style='white-space: nowrap;'>
                    <a target='_parent' href='/realtime/route/{self.route_id}/1'>
                        {self.route_name} - {self.operator_name}
                    </a>
                </h4>
                <p>
                    Lat: {self.lat}<br>
                    Lon: {self.lon}
                </p>
            """
            )
        else:
            self.popup = fl.Popup(
                f"""
                <h4 style='white-space: nowrap;'>
                    {self.route_name} - {self.operator_name}
                </h4>
                <p>
                    Lat: {self.lat}<br>
                    Lon: {self.lon}
                </p>
            """
            )

    def create_tooltip(self) -> None:
        """
        Creates a tooltip for the bus marker.

        Returns:
        - None
        """
        self.tooltip = fl.Tooltip(
            f"""
            <h5>
                {self.route_name} - {self.operator_name}
            </h5>
        """
        )

    def create_icon(self) -> None:
        """
        Creates an icon for the bus marker.

        Returns:
        - None
        """
        if self.color is not None:
            self.icon = fl.Icon(color=self.color.value, icon="fa-bus", prefix="fa")
        else:
            self.icon = fl.Icon(color="blue", icon="fa-bus", prefix="fa")

    def add_to(self, map: fl.Map) -> None:
        """
        Adds a marker to the given map.

        Parameters:
        - map: The map to add the marker to.

        Returns:
        None
        """
        fl.Marker(
            [self.lat, self.lon], tooltip=self.tooltip, popup=self.popup, icon=self.icon
        ).add_to(map)
