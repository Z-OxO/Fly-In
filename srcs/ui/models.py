from typing import NamedTuple, TypeAlias


RGB: TypeAlias = tuple[int, int, int]


class Swatch(NamedTuple):
    fill: RGB
    ring: RGB


class Point(NamedTuple):
    x: float
    y: float
