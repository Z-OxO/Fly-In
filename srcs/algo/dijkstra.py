from srcs.models import MapFlyIn, Cost
import heapq


def dijkstra(map_fly: MapFlyIn) -> dict[str, Cost]:
    dist: dict[str, Cost] = {map_fly.end_hub.name: (0, 0)}
    heap: list[tuple[Cost, str]] = [((0, 0), map_fly.end_hub.name)]

    while heap:
        cost, name = heapq.heappop(heap)
        if cost > dist[name]:
            continue
        cost_zone = map_fly.hubs[name].zone.cost
        if cost_zone is None:
            continue
        for n_name, _ in map_fly.adjacency[name]:
            n_cost = (cost[0] + cost_zone[0], cost[1] + cost_zone[1])
            if n_name not in dist or n_cost < dist[n_name]:
                dist[n_name] = n_cost
                heapq.heappush(heap, (n_cost, n_name))
    return dist
