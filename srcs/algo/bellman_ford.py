from ..models.algo_types import Network
from ..models.map_types import Cost


def bellman_ford(network: Network) -> dict[str, Cost]:
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
    return dist
