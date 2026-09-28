import pygame
from pygame.math import smoothstep
from pygame import Surface, Font
from abc import ABC, abstractmethod
from .constants import PALETTE, ZONE_STYLE
from .models import Point, RGB
from src.models import Zone


class Widget(ABC):
    def __init__(self) -> None:
        # self._dirty = False
        self._visible = True
        self._palette = PALETTE

    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: Surface) -> None: ...


class EdgeWidget(Widget):
    def __init__(
        self, from_pos: Point, to_pos: Point, color: str, width: int
    ) -> None:
        super().__init__()

        self._to_pos: Point = to_pos
        self._from_pos: Point = from_pos
        color = color or "white"
        self._color = self._palette.get(color, self._palette["white"]).fill
        self._width = width

    def draw(self, surface: Surface) -> None:
        pygame.draw.aaline(
            surface,
            self._color,
            self._from_pos,
            self._to_pos,
            self._width,
        )


class HubWidget(Widget):
    def __init__(
        self, pos: Point, color: str | None, zone: Zone, radius: float
    ) -> None:
        super().__init__()
        self.pos: Point = pos
        swatch = self._palette.get(color or "white", self._palette["white"])
        self._fill_color: RGB = swatch.fill
        self._ring_color, self._ring_width = ZONE_STYLE[zone]
        self._radius: float = radius

    def draw(self, surface: Surface) -> None:
        pygame.draw.aacircle(surface, self._fill_color, self.pos, self._radius)
        pygame.draw.aacircle(
            surface,
            self._ring_color,
            (self.pos.x, self.pos.y),
            self._radius,
            self._ring_width,
        )


class TextWidget(Widget):
    def __init__(
        self, font: Font, pos: Point, color: RGB = (200, 200, 200)
    ) -> None:
        super().__init__()
        self._font = font
        self._pos = pos
        self._color = color
        self._lines: list[str] = []

    def set_lines(self, lines: list[str]) -> None:
        self._lines = lines

    def draw(self, surface: Surface) -> None:
        y = self._pos.y
        for line in self._lines:
            surface.blit(
                self._font.render(line, True, self._color), (self._pos.x, y)
            )
            y += self._font.get_linesize()


class DroneWidget(Widget):
    def __init__(self, pos: Point, color: RGB, radius: float) -> None:
        self._color: RGB = color
        self._to_pos = self._from_pos = pos
        self._radius: float = radius
        self._t: float = 1
        self._duration: float = 1

    @property
    def pos(self) -> Point:
        return Point(
            smoothstep(self._from_pos.x, self._to_pos.x, self._t),
            smoothstep(self._from_pos.y, self._to_pos.y, self._t),
        )

    def move_to(self, target: Point, duration: float) -> None:
        self._from_pos = self.pos
        self._to_pos = target
        self._t = 0.0
        self._duration = max(0.1, duration)

    def update(self, dt: float) -> None:
        if self._t >= 1.0:
            return
        self._t += dt / self._duration

    def draw(self, surface: Surface) -> None:
        pygame.draw.aacircle(surface, self._color, self.pos, self._radius)
