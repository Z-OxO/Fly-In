from pathlib import Path
from typing import Generator

from src.models.map_types import MapError


class MapLoader:
    """Read a map file."""

    @staticmethod
    def _get_lines(path: Path) -> Generator[tuple[int, str], None, None]:
        """Yield the non empty lines of a file, without comments.

        Args:
            path: Path of the map file.

        Yields:
            (line number, text) pairs.

        Raises:
            MapError: If the file can't be read.
        """
        def sanitize(line: str) -> str:
            """Remove the comment and spaces."""
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
        """Load the useful lines of a map file.

        Args:
            path: Path of the map file.

        Returns:
            (line number, text) pairs.
        """
        return list(MapLoader._get_lines(path))
