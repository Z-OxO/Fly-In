from collections import deque
from abc import abstractmethod, ABC

from src.models import Network
from src.models import Cost


class ShortestPathAlgo(ABC):
    @staticmethod
    @abstractmethod
    def find_path(network: Network) -> tuple[list[str], int] | None: ...


class Spfa(ShortestPathAlgo):
    @staticmethod
    def find_path(network: Network) -> tuple[list[str], int] | None:
        dist: dict[str, Cost] = {network.source: (0, 0)}
        queue: deque[str] = deque()
        queue.append(network.source)
        in_queue: set[str] = {network.source}
        previous: dict[str, str] = {}

        while queue:
            u = queue.popleft()
            in_queue.remove(u)
            for v in network.neighbors[u]:
                edge = network.edges[(u, v)]
                if edge.cap == 0:
                    continue
                new_cost = (
                    dist[u][0] + edge.cost[0],
                    dist[u][1] + edge.cost[1],
                )
                if v not in dist or new_cost < dist[v]:
                    if v not in in_queue:
                        queue.append(v)
                        in_queue.add(v)
                    dist[v] = new_cost
                    previous[v] = u
        if network.sink not in dist:
            return None
        path: list[str] = [network.sink]
        while path[-1] != network.source:
            path.append(previous[path[-1]])
        path.reverse()
        return path, dist[network.sink][0]


class BellmanFord(ShortestPathAlgo):
    @staticmethod
    def find_path(network: Network) -> tuple[list[str], int] | None:
        dist: dict[str, Cost] = {network.source: (0, 0)}
        previous: dict[str, str] = {}
        changed = True

        for _ in range(len(network.neighbors) - 1):
            if not changed:
                break
            changed = False
            for u, neighboor in network.neighbors.items():
                if u not in dist:
                    continue
                for v in neighboor:
                    edge = network.edges[(u, v)]
                    if edge.cap == 0:
                        continue
                    new_cost = (
                        dist[u][0] + edge.cost[0],
                        dist[u][1] + edge.cost[1],
                    )
                    if v not in dist or new_cost < dist[v]:
                        dist[v] = new_cost
                        previous[v] = u
                        changed = True
        if network.sink not in dist:
            return None

        path: list[str] = [network.sink]
        while path[-1] != network.source:
            path.append(previous[path[-1]])
        path.reverse()
        return path, dist[network.sink][0]
