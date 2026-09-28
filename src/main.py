import sys

from src.ui.session import Session
from src.models import MapError
from src.ui.gui.gui_renderer import GuiRenderer
from src.ui.tui.tui_renderer import TuiRenderer
from pathlib import Path
from src.algo.shortest_path_algo import Spfa
from src.algo.pathfinder import Pathfinder


def main() -> int:
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
        return 1
    gui.run()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Execpected error occured: {e}")
    except KeyboardInterrupt:
        print("Bye ;3")
