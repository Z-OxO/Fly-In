from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

Cost: TypeAlias = tuple[int, int]


class MapError(Exception):
    """Raised when a map file is invalid."""

    def __init__(self, linenum: int, msg: str) -> None:
        """Build the message with the line number.

        Args:
            linenum: Line of the error, 0 if not tied to a line.
            msg: Error message.
        """
        super().__init__(f"{f'line {linenum}: ' if linenum else ''}{msg}")


class Zone(Enum):
    """Zone type of a hub."""

    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"

    @property
    def cost(self) -> Cost | None:
        """Cost to enter a hub of this zone.

        Returns:
            (turns, penalty), or None if the zone is blocked.
        """
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
    """Kind of hub, matches the map keywords."""

    NORMAL = "hub"
    START = "start_hub"
    END = "end_hub"


@dataclass(frozen=True)
class Hub:
    """Hub of the map.

    Attributes:
        name: Unique name.
        x: X coordinate.
        y: Y coordinate.
        zone: Zone type.
        hub_type: Normal, start or end hub.
        max_drones: Max drones at the same time, 0 means no limit.
        color: Optional color name.
    """

    name: str
    x: int
    y: int
    zone: Zone
    hub_type: HubType
    max_drones: int
    color: str | None


@dataclass(frozen=True)
class Link:
    """Connection between two hubs.

    Attributes:
        from_hub: First hub name.
        to_hub: Second hub name.
        max_link_capacity: Max drones on the link at the same time.
    """

    from_hub: str
    to_hub: str
    max_link_capacity: int


Neighbor: TypeAlias = tuple[tuple[str, Link], ...]


@dataclass(frozen=True)
class MapFlyIn:
    """Parsed map.

    Attributes:
        nb_drones: Number of drones.
        start_hub: Start hub.
        end_hub: End hub.
        hubs: Hubs by name.
        links: Links by pair of hub names.
        adjacency: Neighbors and links of each hub.
    """

    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    hubs: dict[str, Hub]
    links: dict[frozenset[str], Link]
    adjacency: dict[str, Neighbor]
