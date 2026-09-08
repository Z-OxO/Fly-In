import pygame
from pygame import Surface
from abc import ABC, abstractmethod
from typing import TypeAlias, NamedTuple

from srcs.models import Plan
from srcs.models.map_types import MapFlyIn
from .renderer import Renderer

RGB: TypeAlias = tuple[int, int, int]


class Point(NamedTuple):
    x: int
    y: int


class Swatch(NamedTuple):
    fill: RGB
    ring: RGB


PALETTE: dict[str, Swatch] = {
    "red": Swatch(fill=(255, 106, 106), ring=(255, 166, 166)),
    "orange": Swatch(fill=(255, 158, 64), ring=(255, 197, 140)),
    "yellow": Swatch(fill=(232, 230, 116), ring=(241, 240, 172)),
    "green": Swatch(fill=(126, 217, 126), ring=(178, 232, 178)),
    "cyan": Swatch(fill=(110, 210, 240), ring=(168, 228, 246)),
    "blue": Swatch(fill=(114, 168, 255), ring=(170, 203, 255)),
    "purple": Swatch(fill=(186, 142, 246), ring=(214, 187, 250)),
    "pink": Swatch(fill=(250, 150, 186), ring=(252, 192, 214)),
    "white": Swatch(fill=(238, 242, 250), ring=(245, 247, 252)),
}


class Widget(ABC):
    def __init__(self) -> None:
        # self._dirty = False
        self._visible = True
        self._palette = PALETTE

    @abstractmethod
    def draw(self, surface: Surface) -> None: ...


class HubWidget(Widget):
    def __init__(self, x: int, y: int, color: str | None, radius: int) -> None:
        super().__init__()
        self.pos: Point = Point(x, y)
        color = color or "white"
        self._fill_color: RGB = self._palette.get(
            color, self._palette["white"]
        ).fill
        self._ring_color: RGB = self._palette.get(
            color, self._palette["white"]
        ).ring
        self._radius: int = radius

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


class GuiRenderer(Renderer):
    def __init__(self, fly_map: MapFlyIn, plan: Plan) -> None:
        super().__init__(fly_map, plan)

        pygame.init()
        self._screen = pygame.display.set_mode((1000, 1000))
        self._clock = pygame.time.Clock()
        self._running = True

    def run(self):
        while self._running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

            self._clock.tick(60)
            self._screen.fill("black")
            for name, hub in self._map.hubs.items():
                HubWidget(
                    ((hub.x) * 100) + 50,
                    ((hub.y) * 100) + 150,
                    hub.color,
                    25,
                ).draw(self._screen)
            pygame.display.flip()
