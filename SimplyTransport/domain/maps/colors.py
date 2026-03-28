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
    YELLOW = "yellow"
    TEAL = "teal"
    CYAN = "cyan"
    BROWN = "brown"
    LIME = "lime"
    MAGENTA = "magenta"
    NAVY = "navy"
    INDIGO = "indigo"
    CORAL = "coral"
    GOLD = "gold"
    OLIVE = "olive"
    CRIMSON = "crimson"
    TURQUOISE = "turquoise"
    VIOLET = "violet"

    def to_hex(self) -> str:
        """CSS hex of the color."""
        return COLORS_HEX[self]


COLORS_HEX: dict[Colors, str] = {
    Colors.RED: "#d32f2f",
    Colors.GREEN: "#2e7d32",
    Colors.ORANGE: "#ef6c00",
    Colors.BLUE: "#1565c0",
    Colors.PINK: "#c2185b",
    Colors.PURPLE: "#6a1b9a",
    Colors.CADETBLUE: "#006064",
    Colors.LIGHTBLUE: "#0277bd",
    Colors.YELLOW: "#f9a825",
    Colors.TEAL: "#00796b",
    Colors.CYAN: "#00838f",
    Colors.BROWN: "#5d4037",
    Colors.LIME: "#558b2f",
    Colors.MAGENTA: "#c218b8",
    Colors.NAVY: "#1a237e",
    Colors.INDIGO: "#311b92",
    Colors.CORAL: "#e64a19",
    Colors.GOLD: "#f57f17",
    Colors.OLIVE: "#827717",
    Colors.CRIMSON: "#b71c1c",
    Colors.TURQUOISE: "#00695c",
    Colors.VIOLET: "#8e24aa",
}
