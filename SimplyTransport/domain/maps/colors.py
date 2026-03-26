from enum import Enum


class Colors(Enum):
    RED = "red"
    GREEN = "green"
    ORANGE = "orange"
    BLUE = "blue"
    PINK = "pink"
    PURPLE = "purple"
    CADETBLUE = "cadetblue"
    LIGHTBLUE = "lightblue"

    def to_hex(self) -> str:
        """CSS hex of the color."""
        return COLORS_HEX[self]


COLORS_HEX: dict[Colors, str] = {
    Colors.RED: "#ff0000",
    Colors.GREEN: "#008000",
    Colors.ORANGE: "#ffa500",
    Colors.BLUE: "#3388ff",
    Colors.PINK: "#ffc0cb",
    Colors.PURPLE: "#800080",
    Colors.CADETBLUE: "#5f9ea0",
    Colors.LIGHTBLUE: "#add8e6",
}
