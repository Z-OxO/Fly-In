import pygame
from pygame import Surface, Clock, Font
from typing import TypeAlias

from srcs.models import Plan
from srcs.models.map_types import MapFlyIn, Hub
from ..renderer import Renderer
from .gui_widgets import TextWidget, HubWidget, Widget, EdgeWidget
from .models import Point

RGB: TypeAlias = tuple[int, int, int]


class ViewPort:
    def __init__(
        self, screen_size: Point, hubs: list[Hub], margin: float = 70.0
    ) -> None:

        max_x = max(hubs, key=lambda x: x.x).x
        max_y = max(hubs, key=lambda x: x.y).y
        min_x = min(hubs, key=lambda x: x.x).x
        min_y = min(hubs, key=lambda x: x.y).y

        span_x, span_y = max_x - min_x, max_y - min_y

        avail_x = screen_size.x - 2 * margin
        avail_y = screen_size.y - 2 * margin

        scale_x = avail_x / span_x if span_x > 0 else float("inf")
        scale_y = avail_y / span_y if span_y > 0 else float("inf")

        self._scale = min(scale_x, scale_y)
        if self._scale == float("inf"):
            self._scale = min(avail_x, avail_y)

        self.off_x = (
            screen_size.x - span_x * self._scale
        ) / 2 - min_x * self._scale
        self.off_y = (
            screen_size.y - span_y * self._scale
        ) / 2 - min_y * self._scale

    def place(self, hub: Hub) -> Point:
        return Point(
            hub.x * self._scale + self.off_x,
            hub.y * self._scale + self.off_y,
        )

    @property
    def radius(self) -> float:
        return max(6.0, min(40.0, self._scale * 0.20))


class GuiRenderer(Renderer):

    def __init__(self, fly_map: MapFlyIn, plan: Plan) -> None:
        super().__init__(fly_map, plan)

        pygame.init()
        info = pygame.display.Info()
        self._size = Point(info.current_w / 2, info.current_h / 2)
        self._screen: Surface = pygame.display.set_mode(
            (int(self._size.x), int(self._size.y))
        )
        self._clock: Clock = pygame.time.Clock()
        self._running: bool = True
        self._viewport: ViewPort = ViewPort(
            self._size, list(self._map.hubs.values())
        )
        self._font: Font = pygame.font.SysFont("monospace", 14)
        self._debug: TextWidget = TextWidget(self._font, Point(10.0, 10.0))
        self._widgets: list[Widget] = []

    @property
    def size(self) -> Point:
        return self._size

    def _build_widgets(self) -> list[Widget]:
        place = self._viewport.place
        hubs = self._map.hubs
        radius = self._viewport.radius
        width = max(1, int(0.10 * self._viewport._scale))

        edges: list[Widget] = [
            EdgeWidget(
                place(hubs[link.from_hub]),
                place(hubs[link.to_hub]),
                "white",
                width,
            )
            for link in self._map.links.values()
        ]
        nodes: list[Widget] = [
            HubWidget(place(hub), hub.color, radius) for hub in hubs.values()
        ]
        return edges + nodes

    def run(self):

        self._widgets = self._build_widgets()
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

            self._clock.tick(60)
            self._screen.fill("black")
            for widget in self._widgets:
                widget.draw(self._screen)
            self._debug.set_lines([
                f"hubs: {len(self._map.hubs)}",
                f"links: {len(self._map.links)}",
                f"drones: {self._map.nb_drone}",
                f"fps: {self._clock.get_fps():.0f}",
            ])
            self._debug.draw(self._screen)
            pygame.display.flip()
