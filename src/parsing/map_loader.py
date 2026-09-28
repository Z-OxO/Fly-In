from pathlib import Path
from typing import Generator

from src.models.map_types import MapError


class MapLoader:
    @staticmethod
    def _get_lines(path: Path) -> Generator[tuple[int, str], None, None]:
        def sanitize(line: str) -> str:
            return line.split("#", 1)[0].strip()

        try:
            with open(path, "r", encoding="utf-8") as f:
                for linenum, raw in enumerate(f, 1):
                    if line := sanitize(raw):
                        yield linenum, line
        except (OSError, UnicodeDecodeError) as e:
            raise MapError(0, f"Failed to read map: {e}") from e

    @staticmethod
    def load(path: Path) -> list[tuple[int, str]]:
        return list(MapLoader._get_lines(path))
