from src.models import MapFlyIn, Plan
from abc import abstractmethod, ABC
from pathlib import Path


class Renderer(ABC):
    """Base class for the ways to show a result."""

    @abstractmethod
    def on_map_loaded(
        self, map_fly: MapFlyIn, plan: Plan, curr_map: Path
    ) -> None:
        """Called when a new map has been solved.

        Args:
            map_fly: The map.
            plan: Plan for the drones.
            curr_map: Path of the map file.
        """
