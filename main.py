import sys

from srcs.ui.session import Session
from srcs.models import MapError
from srcs.ui.gui.gui_renderer import GuiRenderer
from srcs.ui.tui.tui_renderer import TuiRenderer
from pathlib import Path
from srcs.algo.shortest_path_algo import Spfa
from srcs.algo.pathfinder import Pathfinder


def main() -> None:
    session = Session(Pathfinder(Spfa))
    gui = GuiRenderer(session)
    session.subscribe(gui)
    session.subscribe(TuiRenderer())
    try:
        session.load(
            Path("data")
            / "maps"
            / "challenger"
            / "01_the_impossible_dream.txt"
        )
    except (MapError, ValueError) as e:
        print(e)
        sys.exit(1)
    gui.run()


if __name__ == "__main__":
    main()
