from ..models.map_types import Hub, Link, MapError, HubType, MapFlyIn
from .line_parser import LineParser


class MapBuilder:
    def __init__(self, lines: list[tuple[int, str]]) -> None:
        self._lines: list[tuple[int, str]] = lines
        self._hubs: dict[str, Hub] = {}
        """
        frozenset to allow bidirectional check hihi
        a -> b = b -> a, set is not hashable
        """
        self._links: dict[frozenset[str], Link] = {}
        self._adjacency: dict[str, list[tuple[str, Link]]] = {}
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
        self._adjacency[hub.name] = []

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
        self._adjacency[link.from_hub].append((link.to_hub, link))
        self._adjacency[link.to_hub].append((link.from_hub, link))

    def _assemble_map(self) -> MapFlyIn:
        if self._start_hub is None:
            raise MapError(0, "no start_hub defined")
        if self._end_hub is None:
            raise MapError(0, "no end_hub defined")
        if self._nb_drones is None:
            raise MapError(0, "no nb_drones defined")
        return MapFlyIn(
            nb_drones=self._nb_drones,
            start_hub=self._start_hub,
            end_hub=self._end_hub,
            hubs=self._hubs,
            links=self._links,
            adjacency={k: tuple(v) for k, v in self._adjacency.items()},
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
