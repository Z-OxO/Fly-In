import sys
from srcs.parsing import MapBuilder, MapLoader
from srcs.models import MapError
from srcs.ui.gui.gui_renderer import GuiRenderer
from pathlib import Path
from srcs.algo.shortest_path_algo import Spfa
from srcs.algo.pathfinder import Pathfinder


def main() -> None:
    try:
        lines = MapLoader.load(
            Path("data") / "maps" / "challenger"
            / "01_the_impossible_dream.txt"
        )
        map_fly = MapBuilder(lines).build()
    except MapError as e:
        print(f"{e}")
        sys.exit(1)
    pathfinder = Pathfinder(Spfa)
    GuiRenderer(map_fly, pathfinder).run()


if __name__ == "__main__":
    main()
