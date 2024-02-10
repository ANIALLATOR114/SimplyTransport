import folium as fl

from enum import Enum


class PolyLineColors(Enum):
    RED = "#FF0000"
    BLUE = "#0000FF"
    GREEN = "#00FF00"
    PURPLE = "#800080"
    ORANGE = "#FFA500"
    DARKRED = "#8B0000"
    LIGHTRED = "#FF6347"
    DARKBLUE = "#00008B"
    LIGHTBLUE = "#ADD8E6"
    DARKGREEN = "#006400"
    LIGHTGREEN = "#90EE90"
    DARKPURPLE = "#800080"
    PINK = "#FFC0CB"
    CADETBLUE = "#5F9EA0"
    BEIGE = "#F5F5DC"
    WHITE = "#FFFFFF"
    GRAY = "#808080"
    LIGHTGRAY = "#D3D3D3"
    BLACK = "#000000"


class RoutePolyLine:
    def __init__(
        self,
        route_id: str,
        route_name: str,
        route_operator: str,
        locations: list[tuple[float, float]],
        route_color: PolyLineColors = PolyLineColors.BLUE,
        create_popup: bool = True,
        create_tooltip: bool = True,
        create_links: bool = True,
        weight: int = 6,
        opacity: float = 1,
    ) -> None:
        """
        Initializes a PolyLine object.

        Args:
            route_id (str): The ID of the route.
            route_name (str): The name of the route.
            route_operator (str): The operator of the route.
            locations (list[tuple[float, float]]): The list of locations that define the polyline.
            route_color (PolyLineColors, optional): The color of the polyline. Defaults to PolyLineColors.BLUE.
            create_popup (bool, optional): Whether to create a popup for the polyline. Defaults to True.
            create_tooltip (bool, optional): Whether to create a tooltip for the polyline. Defaults to True.
            create_links (bool, optional): Whether to create links for the polyline. Defaults to True.
            weight (int, optional): The weight of the polyline. Defaults to 6.
            opacity (float, optional): The opacity of the polyline. Defaults to 1.
        """
        self.route_id = route_id
        self.route_name = route_name
        self.route_color = route_color
        self.route_operator = route_operator
        self.locations = locations
        self.create_links = create_links
        self.weight = weight
        self.opacity = opacity
        self.create_polyline()
        if create_popup:
            self.create_popup()
        if create_tooltip:
            self.create_tooltip()

    def create_polyline(self) -> None:
        """
        Create a polyline object based on the specified locations and properties.

        Args:
            None

        Returns:
            None
        """

        self.polyline = fl.PolyLine(
            locations=self.locations, color=self.route_color.value, weight=self.weight, opacity=self.opacity
        )

    def create_popup(self) -> None:
        """
        Creates a popup for the polyline object.

        If create_links is True, the popup will contain a link to the realtime route.
        Otherwise, the popup will only display the route name and operator.

        Returns:
            None
        """
        if self.create_links:
            self.popup = fl.Popup(
                f"""
                    <h4 style='white-space: nowrap;'>
                        <a target='_parent' href='/realtime/route/{self.route_id}/1'>
                            {self.route_name} - {self.route_operator}
                        </a>
                    </h4>
                """
            )
        else:
            self.popup = fl.Popup(
                f"""
                    <h4 style='white-space: nowrap;'>
                        {self.route_name} - {self.route_operator}
                    </h4>
                """
            )
        self.polyline.add_child(self.popup)

    def create_tooltip(self) -> None:
        """
        Creates a tooltip for the polyline.

        The tooltip displays the route name and operator.

        Returns:
            None
        """
        self.tooltip = fl.Tooltip(
            f"""
            <h5>
                {self.route_name} - {self.route_operator}
            </h5>
        """
        )
        self.polyline.add_child(self.tooltip)

    def add_to(self, map: fl.Map) -> None:
        """
        Adds the polyline to the given map.

        Args:
            map (fl.Map): The map to add the polyline to.

        Returns:
            None
        """
        self.polyline.add_to(map)
