import sys
from srcs.parsing import MapBuilder, MapLoader
from srcs.models import MapError
from srcs.gui.gui_renderer import GuiRenderer
from pathlib import Path


def main() -> None:
    try:
        lines = MapLoader.load(
            Path("data") / "maps" / "medium" / "03_priority_puzzle.txt"
        )
        map_fly = MapBuilder(lines).build()
    except MapError as e:
        print(f"{e}")
        sys.exit(1)
    GuiRenderer(map_fly, None).run()


if __name__ == "__main__":
    main()
