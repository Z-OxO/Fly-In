import pygame
import pygame_gui
from pathlib import Path
from pygame import Clock, Font, Surface
from typing import TypeAlias

from srcs.models import MapFlyIn, Hub, Plan
from srcs.ui.session import Session
from .gui_widgets import TextWidget, HubWidget, Widget, EdgeWidget, DroneWidget
from .pygame_gui_theme import THEME
from ..renderer import Renderer
from .models import Point
from srcs.models import MapError

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
    def __init__(self, session: Session) -> None:

        pygame.init()
        info = pygame.display.Info()
        self._size = Point(info.current_w / 1.5, info.current_h / 1.5)
        self._screen: Surface = pygame.display.set_mode(
            (int(self._size.x), int(self._size.y))
        )
        self._session = session
        self._ui_manager = pygame_gui.UIManager(
            (int(self._size.x), int(self._size.y)), theme_path=THEME
        )
        self._clock: Clock = pygame.time.Clock()
        self._running: bool = True
        self._turn: int = 0
        self._font: Font = pygame.font.SysFont("monospace", 25)
        self._debug: TextWidget = TextWidget(self._font, Point(10.0, 10.0))

    @property
    def size(self) -> Point:
        return self._size

    def on_map_loaded(self, map_fly: MapFlyIn, plan: Plan) -> None:
        self._map = map_fly
        self._turn = 0
        self._viewport = ViewPort(self._size, list(map_fly.hubs.values()))
        self._widgets: list[Widget] = self._build_widgets()
        self._position_plan: list[dict[int, Point]] = self._build_positions(
            map_fly.start_hub.name, plan
        )

    def _build_widgets(self) -> list[Widget]:
        place = self._viewport.place
        hubs = self._map.hubs
        radius = self._viewport.radius
        width = min(30, max(1, int(0.10 * self._viewport._scale)))

        edges: list[Widget] = [
            EdgeWidget(
                place(hubs[link.from_hub]),
                place(hubs[link.to_hub]),
                "white",
                width,
            )
            for link in self._map.links.values()
        ]
        self._nodes: dict[str, HubWidget] = {
            name: HubWidget(place(hub), hub.color, hub.zone, radius)
            for name, hub in hubs.items()
        }
        start = self._viewport.place(self._map.start_hub)
        self._drones = {
            i: DroneWidget(
                start, (146, 182, 240), self._viewport.radius * 0.32
            )
            for i in range(1, self._map.nb_drones + 1)
        }
        return edges + list(self._nodes.values()) + list(self._drones.values())

    def _build_positions(
        self, start: str, plan: Plan
    ) -> list[dict[int, Point]]:
        current: dict[int, Point] = {
            d: self._nodes[start].pos for d in self._drones
        }
        positions = [dict(current)]
        for turn in plan:
            for drone_id, label in turn:
                if "-" in label:
                    u, v = label.split("-")
                    (x1, y1), (x2, y2) = self._nodes[u].pos, self._nodes[v].pos
                    current[drone_id] = Point((x1 + x2) / 2, (y1 + y2) / 2)
                else:
                    current[drone_id] = self._nodes[label].pos
            positions.append(dict(current))
        return positions

    def _handle_dropdown(self, path: Path) -> None:
        try:
            self._session.load(path)
        except (MapError, ValueError) as e:
            print(f"{path}: {e}")

    def move_drones(self, turn: int) -> None:
        for drone_id, pos in self._position_plan[turn].items():
            self._drones[drone_id].move_to(pos, 0.75)

    def _build_dropdown(self) -> None:
        self._folder = Path("data/maps")
        self._maps = sorted(
            p.relative_to(self._folder).as_posix()
            for p in self._folder.rglob("*.txt")
            if p.is_file()
        )
        options: list[str | tuple[str, str]] = list(self._maps) or [
            "(aucune map)"
        ]
        width = min(420, int(self._size.x * 0.25))
        height, margin = 40, 20
        pygame_gui.elements.UIDropDownMenu(
            options_list=options,
            starting_option=self._maps[1] if self._maps else "(aucune map)",
            relative_rect=pygame.Rect(-width - margin, margin, width, height),
            manager=self._ui_manager,
            anchors={"right": "right", "top": "top"},
        )

    def _handle_keys(self, key: int) -> None:
        if key == pygame.K_RIGHT:
            self._turn = min(len(self._position_plan) - 1, self._turn + 1)
            self.move_drones(self._turn)
        if key == pygame.K_LEFT:
            self._turn = max(0, self._turn - 1)
            self.move_drones(self._turn)

    def _handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and self._maps:
            path = Path(self._folder / event.text)
            self._handle_dropdown(path)
        elif event.type == pygame.KEYUP:
            self._handle_keys(event.key)
        self._ui_manager.process_events(event)

    def _update(self, dt: float) -> None:
        for widget in self._widgets:
            widget.update(dt)
        self._ui_manager.update(dt)

    def _draw(self) -> None:
        self._screen.fill((14, 17, 17))
        for widget in self._widgets:
            widget.draw(self._screen)

        self._debug.set_lines(
            [
                f"hubs: {len(self._map.hubs)}",
                f"links: {len(self._map.links)}",
                f"drones: {self._map.nb_drones}",
                f"turns: {self._turn}/{len(self._position_plan) - 1}",
                f"fps: {self._clock.get_fps():.0f}",
            ]
        )
        self._ui_manager.draw_ui(self._screen)
        self._debug.draw(self._screen)
        pygame.display.flip()

    def run(self) -> None:
        self._build_dropdown()
        while self._running:
            dt = min(self._clock.tick(60) / 1000.0, 0.05)
            for event in pygame.event.get():
                self._handle_event(event)
            self._update(dt)
            self._draw()
