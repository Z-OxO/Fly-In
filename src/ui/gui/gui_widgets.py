import pygame
from pygame.math import smoothstep
from pygame import Surface, Font
from abc import ABC, abstractmethod
from .constants import PALETTE, ZONE_STYLE
from .models import Point, RGB
from src.models import Zone


class Widget(ABC):
    """Base class for everything drawn on screen."""

    def __init__(self) -> None:
        """Set the default state and palette."""
        # self._dirty = False
        self._visible = True
        self._palette = PALETTE

    def update(self, dt: float) -> None:
        """Update the widget, does nothing by default.

        Args:
            dt: Time since last frame, in seconds.
        """

    @abstractmethod
    def draw(self, surface: Surface) -> None:
        """Draw the widget.

        Args:
            surface: Surface to draw on.
        """


class EdgeWidget(Widget):
    """Line between two hubs."""

    def __init__(
        self, from_pos: Point, to_pos: Point, color: str, width: int
    ) -> None:
        """Create the line.

        Args:
            from_pos: Start point.
            to_pos: End point.
            color: Palette color name, white if unknown.
            width: Line width in pixels.
        """
        super().__init__()

        self._to_pos: Point = to_pos
        self._from_pos: Point = from_pos
        color = color or "white"
        self._color = self._palette.get(color, self._palette["white"]).fill
        self._width = width

    def draw(self, surface: Surface) -> None:
        """Draw the line.

        Args:
            surface: Surface to draw on.
        """
        pygame.draw.aaline(
            surface,
            self._color,
            self._from_pos,
            self._to_pos,
            self._width,
        )


class HubWidget(Widget):
    """Circle for a hub, with its capacity written inside."""

    def __init__(
        self,
        pos: Point,
        color: str | None,
        font: Font,
        zone: Zone,
        radius: float,
        cap: int,
    ) -> None:
        """Create the hub circle.

        Args:
            pos: Center of the circle.
            color: Palette color name, white if None or unknown.
            font: Font for the capacity.
            zone: Zone type, sets the ring style.
            radius: Radius in pixels.
            cap: Max drones, 0 is shown as infinite.
        """
        super().__init__()
        self._font = font
        self.pos: Point = pos
        swatch = self._palette.get(color or "white", self._palette["white"])
        self._fill_color: RGB = swatch.fill
        self._ring_color, self._ring_width = ZONE_STYLE[zone]
        self._radius: float = radius
        self._cap = str(cap) if cap != 0 else "∞"
        self._label = font.render(self._cap, True, "black")
        self._label_rect = self._label.get_rect(center=pos)

    def draw(self, surface: Surface) -> None:
        """Draw the circle, the ring and the capacity.

        Args:
            surface: Surface to draw on.
        """
        pygame.draw.aacircle(surface, self._fill_color, self.pos, self._radius)
        pygame.draw.aacircle(
            surface,
            self._ring_color,
            (self.pos.x, self.pos.y),
            self._radius,
            self._ring_width,
        )
        surface.blit(self._label, self._label_rect)


class TextWidget(Widget):
    """Block of text lines."""

    def __init__(
        self, font: Font, pos: Point, color: RGB = (200, 200, 200)
    ) -> None:
        """Create an empty text block.

        Args:
            font: Font to use.
            pos: Top left corner.
            color: Text color.
        """
        super().__init__()
        self._font = font
        self._pos = pos
        self._color = color
        self._lines: list[str] = []

    def set_lines(self, lines: list[str]) -> None:
        """Replace the lines to show.

        Args:
            lines: New lines.
        """
        self._lines = lines

    def draw(self, surface: Surface) -> None:
        """Draw the lines one under the other.

        Args:
            surface: Surface to draw on.
        """
        y = self._pos.y
        for line in self._lines:
            surface.blit(
                self._font.render(line, True, self._color), (self._pos.x, y)
            )
            y += self._font.get_linesize()


class DroneWidget(Widget):
    """Animated circle for a drone."""

    def __init__(self, pos: Point, color: RGB, radius: float) -> None:
        """Create the drone at a position.

        Args:
            pos: Start position.
            color: Fill color.
            radius: Radius in pixels.
        """
        self._color: RGB = color
        self._to_pos = self._from_pos = pos
        self._radius: float = radius
        self._t: float = 1
        self._duration: float = 1

    @property
    def pos(self) -> Point:
        """Current position, smoothed along the animation."""
        return Point(
            smoothstep(self._from_pos.x, self._to_pos.x, self._t),
            smoothstep(self._from_pos.y, self._to_pos.y, self._t),
        )

    def move_to(self, target: Point, duration: float) -> None:
        """Start moving the drone to a new position.

        Args:
            target: Position to reach.
            duration: Animation time in seconds (min 0.1).
        """
        self._from_pos = self.pos
        self._to_pos = target
        self._t = 0.0
        self._duration = max(0.1, duration)

    def update(self, dt: float) -> None:
        """Move the animation forward.

        Args:
            dt: Time since last frame, in seconds.
        """
        if self._t >= 1.0:
            return
        self._t += dt / self._duration

    def draw(self, surface: Surface) -> None:
        """Draw the drone.

        Args:
            surface: Surface to draw on.
        """
        pygame.draw.aacircle(surface, self._color, self.pos, self._radius)
