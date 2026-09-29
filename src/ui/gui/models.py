from typing import NamedTuple, TypeAlias

RGB: TypeAlias = tuple[int, int, int]


class Swatch(NamedTuple):
    """Pair of colors for a hub.

    Attributes:
        fill: Inside color.
        ring: Border color.
    """

    fill: RGB
    ring: RGB


class Point(NamedTuple):
    """2D point in pixels.

    Attributes:
        x: X coordinate.
        y: Y coordinate.
    """

    x: float
    y: float
