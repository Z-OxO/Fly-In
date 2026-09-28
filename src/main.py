import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from src.algo.pathfinder import NoSolutionFind, Pathfinder  # noqa: E402
from src.algo.shortest_path_algo import Spfa  # noqa: E402
from src.models import MapError  # noqa: E402
from src.ui.session import Session  # noqa: E402
from src.ui.tui.tui_renderer import TuiRenderer  # noqa: E402


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
