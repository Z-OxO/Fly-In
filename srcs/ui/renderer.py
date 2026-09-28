from srcs.models import MapFlyIn
from srcs.algo.pathfinder import Pathfinder
from abc import abstractmethod, ABC


class Renderer(ABC):
    def __init__(self, fly_map: MapFlyIn, pathfinder: Pathfinder) -> None:
        self._map: MapFlyIn = fly_map
        self._pathfinder = pathfinder

    @abstractmethod
    def run(self) -> None: ...
