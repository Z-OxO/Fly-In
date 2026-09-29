from typing import Protocol
from pathlib import Path

from src.models import Plan, MapFlyIn
from src.algo.pathfinder import Pathfinder
from src.parsing import MapBuilder, MapLoader


class MapListener(Protocol):
    """Anything that wants to know when a map is loaded."""

    def on_map_loaded(
        self, map_fly: MapFlyIn, plan: Plan, curr_map: Path
    ) -> None:
        """Called when a new map has been solved.

        Args:
            map_fly: The map.
            plan: Plan for the drones.
            curr_map: Path of the map file.
        """


class Session:
    """Load maps, solve them and notify the listeners."""

    def __init__(self, pathfinder: Pathfinder) -> None:
        """Create a session with no listener.

        Args:
            pathfinder: Used to solve each map.
        """
        self._listeners: list[MapListener] = []
        self._pathfinder = pathfinder

    def subscribe(self, listener: MapListener) -> None:
        """Add a listener, if not already added.

        Args:
            listener: The listener.
        """
        if listener not in self._listeners:
            self._listeners.append(listener)

    def load(self, path: Path) -> None:
        """Load and solve a map, then notify the listeners.

        Args:
            path: Path of the map file.

        Raises:
            MapError: If the map is invalid.
            NoSolutionFind: If the map can't be solved.
        """
        map_fly = MapBuilder(MapLoader.load(path)).build()
        plan = self._pathfinder.scheduler(map_fly)
        for listener in self._listeners:
            listener.on_map_loaded(map_fly, plan, path)
