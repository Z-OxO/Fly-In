import os
import sys
from pathlib import Path

from src.models import Hub, MapFlyIn, Plan
from ..renderer import Renderer


class TuiRenderer(Renderer):

    def _clear_terminal(self) -> None:
        # dumb if terminal does not support escape sequences
        if not sys.stdout.isatty() or os.environ.get("TERM") == "dumb":
            return
        if os.name == "nt":
            os.system("cls")
        else:
            sys.stdout.write("\033[H\033[2J\033[3J")
            sys.stdout.flush()

    def on_map_loaded(
        self, map_fly: MapFlyIn, plan: Plan, curr_map: Path
    ) -> None:
        self._curr_map = curr_map
        self._map = map_fly
        self._plan = plan
        self._hubs_caps = self._build_hubs_caps()
        self._clear_terminal()
        self._print_output()

    def _build_hubs_caps(self) -> dict[str, tuple[int, int]]:
        hubs: dict[str, Hub] = self._map.hubs

        hubs_caps: dict[str, tuple[int, int]] = {}
        for name, hub in hubs.items():
            hubs_caps[name] = 0, hub.max_drones
        return hubs_caps

    def _print_output(self) -> None:

        output = "\n".join(
            " ".join(
                f"D{drone_id}-{destination}" for drone_id, destination in move
            )
            for move in self._plan
        )
        print(output)
