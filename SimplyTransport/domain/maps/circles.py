import folium as fl
from SimplyTransport.domain.maps.colors import Colors


class Circle:
    def __init__(
        self,
        location: tuple[float, float],
        radius: int,
        color: Colors = Colors.RED,
        fill: bool = False,
        fill_color: Colors = Colors.RED,
        fill_opacity: float = 0.1,
        weight: int = 6,
        opacity: float = 1,
    ) -> None:
        """
        Initializes a Circle object.

        Args:
            location (tuple[float, float]): The location (latitude, longitude) of the circle.
            radius (int): The radius of the circle.
            color (Colors, optional): The color of the circle. Defaults to Colors.RED.
                Defaults to PolyLineColors.BLUE.
            fill (bool, optional): Whether to fill the circle. Defaults to False.
            fill_color (Colors, optional): The color of the circle when filled. Defaults to Colors.RED.
            fill_opacity (float, optional): The opacity of the circle when filled. Defaults to 0.1.
            weight (int, optional): The weight of the circle. Defaults to 6.
            opacity (float, optional): The opacity of the circle. Defaults to 1.
        """

        self.location = location
        self.radius = radius
        self.color = color
        self.fill = fill
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.weight = weight
        self.opacity = opacity
        self.create_circle()

    def create_circle(self) -> None:
        """
        Create a circle object based on the specified location and properties.

        Args:
            None

        Returns:
            None
        """

        if self.fill:
            self.circle = fl.Circle(
                location=self.location,
                radius=self.radius,
                color=self.color.value,
                weight=self.weight,
                opacity=self.opacity,
                fill=self.fill,
                fill_color=self.fill_color.value,
                fill_opacity=self.fill_opacity,
            )
        else:
            self.circle = fl.Circle(
                location=self.location,
                radius=self.radius,
                color=self.color.value,
                weight=self.weight,
                opacity=self.opacity,
                fill=self.fill,
            )

    def add_to(self, map: fl.Map) -> None:
        """
        Adds the polyline to the given map.

        Args:
            map (fl.Map): The map to add the polyline to.

        Returns:
            None
        """
        self.circle.add_to(map)
