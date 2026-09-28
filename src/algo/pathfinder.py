from typing import Type

from .shortest_path_algo import ShortestPathAlgo
from src.models import Network, Plan, Move
from src.models import MapFlyIn


class NoSolutionFind(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Pathfinder:
    def __init__(self, pathfinding_algo: Type[ShortestPathAlgo]) -> None:
        self.algo = pathfinding_algo
        self.network: Network
        self.nb_drones: int = 0
        self.t_max: int | None = None

    def ssp(self) -> None:
        path_num: int = 0
        sum_of_paths_cost: int = 0
        t_max: int | None = None

        while path_num < self.nb_drones:
            path = self.algo.find_path(self.network)
            if path is None:
                break
            path_num += 1
            self.network.push_network(path[0], 1)

            path_hubs, cost_path = path
            sum_of_paths_cost += cost_path
            t_new = (
                -(-(self.network.nb_drones + sum_of_paths_cost) // path_num)
                - 1
            )
            if t_max is not None and t_new > t_max:
                self.network.push_network(path_hubs, -1)
                break
            t_max = t_new
        if t_max is None:
            return
        self.t_max = t_max

    def scheduler(self, map_fly: MapFlyIn) -> Plan:
        self.network = Network.from_map(map_fly)
        self.nb_drones = map_fly.nb_drones
        self.t_max = None
        self.ssp()
        routes = self.network.decompose()
        if routes is None or self.t_max is None:
            raise NoSolutionFind("The map is not solvable")
        routes_caps: list[int] = [
            max(0, self.t_max - route.length + 1) for route in routes
        ]
        slots = [
            (delay + route.length, route.length, delay, route)
            for i, route in enumerate(routes)
            for delay in range(routes_caps[i])
        ]
        slots.sort(key=lambda s: s[:3])

        turns: dict[int, list[Move]] = {}
        for drone_id, (_, _, delay, route) in enumerate(
            slots[: self.nb_drones], 1
        ):
            previous_hub_turn: int = 0
            for turn, step in route.steps:
                if turn - previous_hub_turn == 2:
                    turns.setdefault(delay + turn - 1, []).append(
                        (drone_id, step)
                    )
                turns.setdefault(delay + turn, []).append(
                    (drone_id, step.split("-")[1])
                )
                previous_hub_turn = turn
        # Don t skip blank turn and get turn in order with max(turns) + 1
        return tuple(tuple(turns.get(t, [])) for t in range(1, max(turns) + 1))
