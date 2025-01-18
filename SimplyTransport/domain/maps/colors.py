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

    def to_html_square(self) -> str:
        """
        Converts the color value to an HTML span element with the corresponding background color.

        Returns:
            str: HTML span element with the background color.
        """
        return (
            '<span style="display: inline-block; width: 10px; height: 10px; '
            f'background-color: {self.value};"></span>'
        )
