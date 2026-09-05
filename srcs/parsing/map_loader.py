from pathlib import Path
from typing import Generator
from dataclasses import dataclass
from enum import Enum
import sys

ROOT = Path(__file__).resolve().parents[2]

ALLOWED: dict[str, frozenset[str]] = {
    "nb_drones": frozenset(),
    "hub": frozenset({"zone", "color", "max_drones"}),
    "start_hub": frozenset({"zone", "color", "max_drones"}),
    "end_hub": frozenset({"zone", "color", "max_drones"}),
    "connection": frozenset({"max_link_capacity"}),
}


class MapError(Exception):
    def __init__(self, linenum: int, msg: str) -> None:
        super().__init__(f"{f'line {linenum}: ' if linenum else ''}{msg}")


class Zone(Enum):
    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


class HubType(Enum):
    NORMAL = "hub"
    START = "start_hub"
    END = "end_hub"

@dataclass(frozen=True)
class Hub:
    name: str
    x: int
    y: int
    zone: Zone
    metadata: dict[str, str]


@dataclass(frozen=True)
class Link:
    name: str
    from_hub: str
    to_hub: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class MapFlyIn:
    nb_drone: int
    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]
    links: list[Link]


class LineParser:
    def __init__(self, linenum: int, text: str):
        self._linenum = linenum
        self._text = text

    def _error(self, msg: str) -> MapError:
        return MapError(self._linenum, msg)

    def _hub(
        self, hub_type: HubType, line_data: str, metatada: dict[str, str]
    ) -> Hub:
        if not line_data:
            raise self._error(f"{hub_type} with missing datas")

        line_split = line_data.split()
        if len(line_split) != 3:
            raise self._error(
                f"{hub_type} has invalid data has to be: "
                f"'name x y' got {line_data}"
            )

        name, sx, sy = line_data.split()
        if "-" in name:
            raise self._error(f"{hub_type} name cannot contain '-'")

        try:
            x, y = int(sx), int(sy)
        except ValueError:
            raise self._error(
                f"{hub_type} invalid coordinate has to be integers got: "
                f"{sx}, {sy}"
            )

        return Hub(name, x, y, Zone(metatada.get("zone", "normal")), metatada)

    def _meta(
        self,
        bracket: str,
        metadata: str,
        keyword: str,
        allowed: frozenset[str],
    ) -> dict[str, str]:
        if not bracket:
            if "]" in metadata:
                raise self._error("unmatched ']' with no opening '['")
            return {}
        if not allowed:
            raise self._error(f"directive {keyword!r} takes no metadata")

        metadata = metadata.strip()
        if not metadata.endswith("]"):
            raise self._error("unclosed metadata block: missing ']'")
        if "[" in metadata:
            raise self._error("nested or repeated '[' in metadata block")

        listing = ", ".join(sorted(allowed))
        metadata_dict: dict[str, str] = {}
        for token in metadata.removesuffix("]").split():
            name, eq, value = token.partition("=")
            if not eq:
                raise self._error(
                    f"malformed metadata {token!r}: expected key=value"
                )
            if not name:
                raise self._error(f"malformed metadata {token!r}: empty key")
            if not value:
                raise self._error(f"metadata {name!r} has an empty value")
            if name in metadata_dict:
                raise self._error(f"duplicate metadata key {name!r}")
            if name not in allowed:
                raise self._error(
                    f"unknown metadata key {name!r}"
                    f"for {keyword!r} (allowed: {listing})"
                )
            metadata_dict[name] = value
        return metadata_dict

    def parse(self) -> Hub | Link:
        name, _, data = self._text.partition(":")
        data, bracket, metadata = data.partition("[")

        if name not in ALLOWED.keys():
            raise self._error(
                f"prefix name is invalid expected: {','.join(ALLOWED.keys())} "
                f"got: {name}"
            )

        metadata_dict = self._meta(bracket, metadata, name, ALLOWED[name])
        match name:
            case "connection":
                return self._link()
            case "hub":
                return self._hub(HubType(name), data, metadata_dict)


class MapBuilder:
    def __init__(self, lines: list[tuple[int, str]]) -> None:
        self._lines: list[tuple[int, str]] = lines
        self._hubs: list[Hub] = []
        self._links: list[Link] = []

    def build(self) -> MapFlyIn:
        for linenum, text in self._lines:
            print(LineParser(linenum, text).parse())


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
        print(list(MapLoader._get_lines(path)))
        return list(MapLoader._get_lines(path))


try:
    lines = MapLoader.load(
        ROOT / "data" / "maps" / "easy" / "03_basic_capacity.txt"
    )
    MapBuilder(lines).build()
except MapError as e:
    print(f"{e}")
    sys.exit(1)
