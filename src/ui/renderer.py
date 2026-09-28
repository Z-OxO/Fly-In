from src.models import MapFlyIn, Plan
from abc import abstractmethod, ABC


class Renderer(ABC):
    @abstractmethod
    def on_map_loaded(self, map_fly: MapFlyIn, plan: Plan) -> None: ...
