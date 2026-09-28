from typing import Protocol
from pathlib import Path

from srcs.models import Plan, MapFlyIn
from srcs.algo.pathfinder import Pathfinder
from srcs.parsing import MapBuilder, MapLoader


class MapListener(Protocol):
    def on_map_loaded(self, map_fly: MapFlyIn, plan: Plan) -> None:
        ...


class Session:
    def __init__(self, pathfinder: Pathfinder) -> None:
        self._listeners: list[MapListener] = []
        self._pathfinder = pathfinder

    def subscribe(self, listener: MapListener) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def load(self, path: Path) -> None:
        map_fly = MapBuilder(MapLoader.load(path)).build()
        plan = self._pathfinder.scheduler(map_fly)
        for listener in self._listeners:
            listener.on_map_loaded(map_fly, plan)
