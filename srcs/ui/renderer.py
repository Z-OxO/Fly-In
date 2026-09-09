from srcs.models import MapFlyIn, Plan
from abc import abstractmethod, ABC


class Renderer(ABC):
    def __init__(self, fly_map: MapFlyIn, plan: Plan) -> None:
        self._map: MapFlyIn = fly_map
        self._plan = plan

    @abstractmethod
    def run(self): ...
