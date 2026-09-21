from dataclasses import dataclass
from typing import TypeAlias
from .map_types import MapFlyIn, Hub, Cost, Link, Zone, HubType

Move: TypeAlias = tuple[int, str]
Turn: TypeAlias = tuple[Move, ...]
Plan: TypeAlias = tuple[Turn, ...]


@dataclass
class Edge:
    cap: int
    cost: Cost
    is_real: bool


@dataclass
class Network:
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

    def add_hub(self, hub: Hub, nb_drones: int) -> None:

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

    def add_link(
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
            print(link.max_link_capacity)
            self.add_pair(
                cost, link.max_link_capacity, self._exit(src), self._entry(dst)
            )

    @classmethod
    def from_map(cls, map_fly: MapFlyIn) -> "Network":
        source = cls._entry(map_fly.start_hub.name)
        sink = cls._exit(map_fly.end_hub.name)
        network = cls({}, {source: [], sink: []}, source, sink)

        for hub in map_fly.hubs.values():
            network.add_hub(hub, map_fly.nb_drones)
        for link in map_fly.links.values():
            network.add_link(map_fly, link)

        return network
