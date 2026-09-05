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
    hub_type: HubType
    metadata: dict[str, str]


@dataclass(frozen=True)
class Link:
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

    def _hub(
        self,
        prefix_name: str,
        hub_type: HubType,
        line_data: str,
        metatada: dict[str, str],
    ) -> Hub:
        if not line_data:
            raise self._error(f"{hub_type} with missing datas")

        line_split = line_data.split()
        if len(line_split) != 3:
            raise self._error(
                f"{prefix_name} has invalid data has to be: "
                f"'name x y' got: {line_data}"
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
        return Hub(
            name,
            x,
            y,
            Zone(metatada.get("zone", "normal")),
            hub_type,
            metatada,
        )

    def _link(self, line_data: str, metadata: dict[str, str]) -> Link:
        from_hub, dash, to_hub = line_data.partition("-")

        if not dash or "-" in from_hub or " " in from_hub or " " in to_hub:
            raise self._error(
                "link data malformated "
                f"has to be from_hub-to_hub got: {line_data}"
            )

        if not from_hub or not to_hub:
            raise self._error(f"link missing hub got: {line_data}")

        return Link(from_hub, to_hub, metadata)

    def _nb_drones(self, line_data: str) -> int:
        try:
            nb_drones = int(line_data)
        except ValueError:
            raise self._error(
                f"nb_drones invalid value got: {line_data!r} "
                "expected a positive integer"
            ) from None
        if nb_drones <= 0:
            raise self._error(f"nb_drones must be positive got: {nb_drones}")
        return nb_drones

    def parse(self) -> Hub | Link | int:
        name, _, data = self._text.partition(":")
        data, bracket, metadata = data.partition("[")

        if name not in ALLOWED.keys():
            raise self._error(
                f"prefix name is invalid expected: {','.join(ALLOWED.keys())} "
                f"got: {name}"
            )

        data = data.strip()
        metadata_dict = self._meta(bracket, metadata, name, ALLOWED[name])
        match name:
            case "nb_drones":
                return self._nb_drones(data)
            case "connection":
                return self._link(data, metadata_dict)
            case _:
                return self._hub(name, HubType(name), data, metadata_dict)


class MapBuilder:
    def __init__(self, lines: list[tuple[int, str]]) -> None:
        self._lines: list[tuple[int, str]] = lines
        self._hubs: dict[str, Hub] = {}
        # frozenset to allow bidirectional check hihi a -> b = b -> a, set is not hashable
        self._links: dict[frozenset[str], Link] = {}
        self._nb_drones: int | None = None
        self._start_hub: Hub | None = None
        self._end_hub: Hub | None = None

    def _set_nb_drones(self, linenum: int, nb: int) -> None:
        if self._nb_drones is not None:
            raise MapError(linenum, "nb_drones defined more than once")
        if self._hubs or self._links:
            raise MapError(linenum, "nb_drones must be the first directive")
        self._nb_drones = nb

    def _add_hub(self, linenum: int, hub: Hub) -> None:
        if hub.name in self._hubs:
            raise MapError(linenum, f"duplicate hub: {hub.name}")
        if hub.hub_type is HubType.START:
            if self._start_hub is not None:
                raise MapError(linenum, "multiple start_hub definitions")
            self._start_hub = hub
        elif hub.hub_type is HubType.END:
            if self._end_hub is not None:
                raise MapError(linenum, "multiple end_hub definitions")
            self._end_hub = hub
        self._hubs[hub.name] = hub

    def _set_link(self, linenum: int, link: Link) -> None:
        key = frozenset((link.from_hub, link.to_hub))
        if len(key) == 1:
            raise MapError(linenum, f"self-link on {link.from_hub}")
        if key in self._links:
            raise MapError(
                linenum, f"duplicate link {link.from_hub}-{link.to_hub}"
            )

        for name in key:
            if name not in self._hubs:
                raise MapError(
                    linenum, f"connection to undefined hub {name!r}"
                )
        self._links[key] = link

    def _assemble_map(self) -> MapFlyIn:
        if self._start_hub is None:
            raise MapError(0, "no start_hub defined")
        if self._end_hub is None:
            raise MapError(0, "no end_hub defined")
        if self._nb_drones is None:
            raise MapError(0, "no nb_drones defined")
        return MapFlyIn(
            nb_drone=self._nb_drones,
            start_hub=self._start_hub,
            end_hub=self._end_hub,
            hubs=list(self._hubs.values()),
            links=list(self._links.values()),
        )

    def build(self) -> MapFlyIn:
        for linenum, text in self._lines:
            match LineParser(linenum, text).parse():
                case int() as nb:
                    self._set_nb_drones(linenum, nb)
                case Hub() as hub:
                    self._add_hub(linenum, hub)
                case Link() as link:
                    self._set_link(linenum, link)
        return self._assemble_map()


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


try:
    lines = MapLoader.load(
        ROOT / "data" / "maps" / "easy" / "03_basic_capacity.txt"
    )
    print(MapBuilder(lines).build())
except MapError as e:
    print(f"{e}")
    sys.exit(1)
