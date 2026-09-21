from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

Cost: TypeAlias = tuple[int, int]


class MapError(Exception):
    def __init__(self, linenum: int, msg: str) -> None:
        super().__init__(f"{f'line {linenum}: ' if linenum else ''}{msg}")


class Zone(Enum):
    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"

    @property
    def cost(self) -> Cost | None:
        match self:
            case Zone.NORMAL:
                return (1, 1)
            case Zone.PRIORITY:
                return (1, 0)
            case Zone.RESTRICTED:
                return (2, 1)
            case Zone.BLOCKED:
                return None


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
    max_drones: int
    color: str | None


@dataclass(frozen=True)
class Link:
    from_hub: str
    to_hub: str
    max_link_capacity: int


Neighbor: TypeAlias = tuple[tuple[str, Link], ...]


@dataclass(frozen=True)
class MapFlyIn:
    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    hubs: dict[str, Hub]
    links: dict[frozenset[str], Link]
    adjacency: dict[str, Neighbor]
