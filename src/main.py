import argparse
import sys

from pathlib import Path
from src.algo.pathfinder import Pathfinder
from src.algo.shortest_path_algo import Spfa
from src.models import MapError, NoSolutionFind
from src.ui.session import Session
from src.ui.tui.tui_renderer import TuiRenderer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fly-in")
    parser.add_argument("map", type=Path, help="path to the map file")
    parser.add_argument("--no-gui", action="store_true", help="terminal only")
    args = parser.parse_args(argv)

    session = Session(Pathfinder(Spfa))
    session.subscribe(TuiRenderer())
    gui = None
    if not args.no_gui:
        import pygame
        from src.ui.gui.gui_renderer import GuiRenderer

        try:
            gui = GuiRenderer(session)
            session.subscribe(gui)
        except pygame.error as e:
            print(f"GUI unavailable ({e}), terminal only", file=sys.stderr)
    try:
        session.load(args.map)
    except (MapError, NoSolutionFind) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    if gui is not None:
        gui.run()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Execpected error occured: {e}")
    except KeyboardInterrupt:
        print("Bye ;3")
