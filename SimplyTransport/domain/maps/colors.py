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

    def to_html_square(self):
        """
        Converts the color value to an HTML span element with the corresponding background color.

        Returns:
            str: HTML span element with the background color.
        """
        return f'<span style="display: inline-block; width: 10px; height: 10px; background-color: {self.value};"></span>'
