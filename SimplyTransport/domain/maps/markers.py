import folium as fl

from enum import Enum
from SimplyTransport.domain.route.model import RouteModel

from SimplyTransport.domain.stop.model import StopModel


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
        stop: StopModel,
        routes: list[RouteModel] = None,
        create_link: bool = True,
        create_stop_features: bool = True,
        color: MarkerColors = None,
    ) -> None:
        """
        Initialize a Marker object.

        Args:
            stop (StopModel): The stop associated with the marker.
            routes (list[RouteModel], optional): The routes associated with the marker. Defaults to None.
            create_links (bool, optional): Whether to create links for the marker. Defaults to True.
            create_stop_features (bool, optional): Whether to create stop features for the marker. Defaults to True.
            color (MarkerColors, optional): The color of the marker. Defaults to None.
        """
        self.stop = stop
        self.routes = routes
        self.create_link = create_link
        self.create_stop_features = create_stop_features
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
        stop_heading = ""
        if self.create_link:
            stop_heading = f"""
                <h4 style='white-space: nowrap;'>
                    <a target='_parent' href='/realtime/stop/{self.stop.id}'>
                        {self.stop.code} - {self.stop.name}
                    </a>
                </h4>
            """
        else:
            stop_heading = f"""
                <h4 style='white-space: nowrap;'>
                    {self.stop.code} - {self.stop.name}
                </h4>
            """

        stop_lat_lon = f"""
            <p>
                <a target='_parent' href="https://www.google.com/maps?layer=c&amp;cbll={ self.stop.lat },{ self.stop.lon }&amp;cbp=0,0,,,">Street view</a><br>
                Lat: {self.stop.lat}<br>
                Lon: {self.stop.lon}
                </p>
            """

        stop_features = ""
        if self.create_stop_features and self.stop.stop_feature is not None:
            stop_features = f"""
                <p>
                    Wheelchair accessible: {self.stop.stop_feature.wheelchair_accessability}<br>
                    Bus Shelter: {self.stop.stop_feature.shelter_active}<br>
                    Realtime display: {self.stop.stop_feature.rtpi_active}<br>
                </p>
            """
        else:
            stop_features = f"""
                <p>
                    Lat: {self.stop.lat}<br>
                    Lon: {self.stop.lon}
                </p>
            """

        stop_routes = ""
        if self.routes is not None:
            stop_routes = f"""
                <p>
                    <h5>{len(self.routes)} Routes </h5>
                    {'<br>'.join([f"<a target='_parent' href='/realtime/route/{route.id}/1'>{route.short_name}</a> - {route.long_name}" for route in self.routes])}
                </p>
            """

        self.popup = fl.Popup(f"{stop_heading}{stop_lat_lon}{stop_features}{stop_routes}")

    def create_tooltip(self) -> None:
        """
        Creates a tooltip for the stop marker.

        Returns:
        - None
        """
        self.tooltip = fl.Tooltip(
            f"""
            <h5>
                {self.stop.code} - {self.stop.name}
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
            self.icon = fl.Icon(color=self.color.value, icon="fa-chevron-circle-down", prefix="fa")
        else:
            self.icon = fl.Icon(color="blue", icon="fa-chevron-circle-down", prefix="fa")

    def add_to(self, canvas: fl.Map | fl.FeatureGroup, type_of_marker: str = "regular", radius: float = 7) -> None:
        """
        Adds a marker to the given map or layer.

        Parameters:
        - canvas: The canvas to add the marker to.
        - type_of_marker: The type of marker to add. Defaults to "regular".

        Returns:
        None
        """
        if type_of_marker == "circle":
            fl.CircleMarker(
                [self.stop.lat, self.stop.lon],
                color="#000",
                tooltip=self.tooltip,
                popup=self.popup,
                icon=self.icon,
                fill_color="#ccc",
                fill_opacity=1,
                radius=radius,
                weight=4,
                opacity=1,
            ).add_to(canvas)
        else:
            fl.Marker(
                [self.stop.lat, self.stop.lon],
                tooltip=self.tooltip,
                popup=self.popup,
                icon=self.icon,
            ).add_to(canvas)


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
        fl.Marker([self.lat, self.lon], tooltip=self.tooltip, popup=self.popup, icon=self.icon).add_to(map)
