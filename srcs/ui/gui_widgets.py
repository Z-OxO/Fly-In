import pygame
from pygame import Surface, Font
from abc import ABC, abstractmethod
from .constants import PALETTE
from .models import Point, RGB


class Widget(ABC):
    def __init__(self) -> None:
        # self._dirty = False
        self._visible = True
        self._palette = PALETTE

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

    def draw(self, surface: Surface):
        pygame.draw.aaline(
            surface,
            self._color,
            self._from_pos,
            self._to_pos,
            self._width,
        )


class HubWidget(Widget):
    def __init__(self, pos: Point, color: str | None, radius: float) -> None:
        super().__init__()
        self.pos: Point = pos
        color = color or "white"
        self._fill_color: RGB = self._palette.get(
            color, self._palette["white"]
        ).fill
        self._ring_color: RGB = self._palette.get(
            color, self._palette["white"]
        ).ring
        self._radius: float = radius

    def draw(self, surface: Surface):
        pygame.draw.aacircle(
            surface, self._fill_color, (self.pos.x, self.pos.y), self._radius
        )
        pygame.draw.aacircle(
            surface,
            self._ring_color,
            (self.pos.x, self.pos.y),
            self._radius,
            3,
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
