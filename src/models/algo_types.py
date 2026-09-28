from dataclasses import dataclass
from typing import TypeAlias
from .map_types import MapFlyIn, Hub, Cost, Link, Zone, HubType

Move: TypeAlias = tuple[int, str]
Turn: TypeAlias = tuple[Move, ...]
Plan: TypeAlias = tuple[Turn, ...]


class NoSolutionFind(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


@dataclass
class Edge:
    cap: int
    cost: Cost
    is_real: bool


@dataclass(frozen=True)
class Route:
    steps: tuple[tuple[int, str], ...]

    @property
    def length(self) -> int:
        return self.steps[-1][0]


@dataclass
class Network:
    nb_drones: int
    edges: dict[tuple[str, str], Edge]
    neighbors: dict[str, list[str]]
    source: str
    sink: str

    @staticmethod
    def _entry(hub: str) -> str:
        return f"{hub}-in"

    @staticmethod
    def _exit(hub: str) -> str:
        return f"{hub}-out"

    def push_network(self, path: list[str], unit: int) -> None:
        for u, v in zip(path, path[1:]):
            self.edges[(u, v)].cap -= unit
            self.edges[(v, u)].cap += unit

    def add_pair(
        self,
        cost: Cost,
        cap: int,
        from_hub: str,
        to_hub: str,
    ) -> None:
        self.edges[(from_hub, to_hub)] = Edge(cap, cost, True)
        self.edges[(to_hub, from_hub)] = Edge(0, (-cost[0], -cost[1]), False)
        self.neighbors.setdefault(from_hub, []).append(to_hub)
        self.neighbors.setdefault(to_hub, []).append(from_hub)

    def _add_hub(self, hub: Hub, nb_drones: int) -> None:

        if hub.zone is Zone.BLOCKED or hub.zone.cost is None:
            return
        if hub.hub_type is HubType.NORMAL:
            cap = hub.max_drones
        else:
            cap = nb_drones

        self.add_pair(
            (0, 0),
            cap,
            Network._entry(hub.name),
            Network._exit(hub.name),
        )

    def _add_link(
        self,
        map_fly: MapFlyIn,
        link: Link,
    ) -> None:

        for src, dst in (
            (link.from_hub, link.to_hub),
            (link.to_hub, link.from_hub),
        ):
            cost = map_fly.hubs[dst].zone.cost
            if cost is None:
                continue
            self.add_pair(
                cost, link.max_link_capacity, self._exit(src), self._entry(dst)
            )

    @classmethod
    def from_map(cls, map_fly: MapFlyIn) -> "Network":
        source = cls._entry(map_fly.start_hub.name)
        sink = cls._exit(map_fly.end_hub.name)
        network = cls(
            map_fly.nb_drones, {}, {source: [], sink: []}, source, sink
        )

        for hub in map_fly.hubs.values():
            network._add_hub(hub, map_fly.nb_drones)
        for link in map_fly.links.values():
            network._add_link(map_fly, link)

        return network

    def _flot_neighboor(self, u: str) -> str | None:
        for v in self.neighbors[u]:
            if self.edges[u, v].is_real and self.edges[v, u].cap > 0:
                return v
        return None

    def _find_route(self) -> Route | None:
        steps: list[tuple[int, str]] = []
        u, turns = self.source, 0
        if self._flot_neighboor(u) is None:
            return None
        while u != self.sink:
            n = self._flot_neighboor(u)
            if n is None:
                return None
            self.push_network([u, n], -1)
            if self.edges[u, n].cost[0] > 0:
                if self.edges[u, n].cost == Zone.RESTRICTED.cost:
                    turns += 2
                else:
                    turns += 1
                steps.append((turns, f"{u.split('-')[0]}-{n.split('-')[0]}"))
            u = n
        return Route(tuple(steps))

    def decompose(self) -> list[Route]:
        routes: list[Route] = []
        while route := self._find_route():
            routes.append(route)
        return routes
