from .shortest_path_algo import ShortestPathAlgo
from ..models.algo_types import Network
from typing import Type


class Pathfinder:
    def __init__(
        self, network: Network, pathfinding_algo: Type[ShortestPathAlgo]
    ) -> None:
        self.network = network
        self.algo = pathfinding_algo
        self.nb_drones = network.nb_drones

    def ssp(self) -> int | None:
        path_num: int = 0
        sum_of_path_cost: int = 0
        t_max: int | None = None

        while path_num < self.nb_drones:
            path = self.algo.find_path(self.network)
            if path is None:
                break
            path_num += 1
            self.network.push_network(path[0], 1)

            path, cost_path = path
            sum_of_path_cost += cost_path
            t_new = (self.network.nb_drones + sum_of_path_cost) // path_num - 1

            if t_max is not None and t_new > t_max:
                self.network.push_network(path, -1)
                print(self.network.decompose())
                return t_max
            t_max = t_new
        if t_max is None:
            return None
        """for name, edge in self.network.edges.items():
            if not edge.is_real:
                print(f"edge : {name[0]} -> {name[1]} , cap={edge.cap}")"""
        return t_max
