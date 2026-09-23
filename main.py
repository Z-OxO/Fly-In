import sys
from srcs.parsing import MapBuilder, MapLoader
from srcs.models import MapError
from srcs.ui.gui.gui_renderer import GuiRenderer
from pathlib import Path
from srcs.models.algo_types import Network
from srcs.algo.shortest_path_algo import Spfa
from srcs.algo.pathfinder import Pathfinder


def main() -> None:
    try:
        lines = MapLoader.load(
            Path("data") / "maps" / "test" / "test2path.txt"
        )
        map_fly = MapBuilder(lines).build()
    except MapError as e:
        print(f"{e}")
        sys.exit(1)
    network = Network.from_map(map_fly)
    Pathfinder(network, Spfa).ssp()
    print(network.decompose())
    GuiRenderer(map_fly, None).run()


if __name__ == "__main__":
    main()
