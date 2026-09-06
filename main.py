import sys
from srcs.parsing import MapBuilder, MapLoader
from srcs.models import MapError
from pathlib import Path


def main() -> None:
    try:
        lines = MapLoader.load(
            Path("data") / "maps" / "easy" / "03_basic_capacity.txt"
        )
        print(MapBuilder(lines).build())
    except MapError as e:
        print(f"{e}")
    sys.exit(1)


if __name__ == "__main__":
    main()
