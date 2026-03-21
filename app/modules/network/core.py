from typing import Dict, List, Tuple
import heapq


class Graph:
    def __init__(self) -> None:
        self.adj: Dict[str, List[Tuple[str, float]]] = {}

    def add_edge(self, u: str, v: str, w: float) -> None:
        self.adj.setdefault(u, []).append((v, w))
        self.adj.setdefault(v, []).append((u, w))

    def remove_edge(self, u: str, v: str) -> None:
        if u in self.adj:
            self.adj[u] = [(node, w) for node, w in self.adj[u] if node != v]
        if v in self.adj:
            self.adj[v] = [(node, w) for node, w in self.adj[v] if node != u]

    def dijkstra(self, source: str, target: str) -> Tuple[float, List[str]]:
        dist: Dict[str, float] = {node: float("inf") for node in self.adj}
        prev: Dict[str, str | None] = {node: None for node in self.adj}
        dist[source] = 0.0

        heap: List[Tuple[float, str]] = [(0.0, source)]

        while heap:
            d, u = heapq.heappop(heap)
            if u == target:
                break
            if d > dist[u]:
                continue
            for v, w in self.adj.get(u, []):
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        if dist[target] == float("inf"):
            return float("inf"), []

        path: List[str] = []
        cur: str | None = target
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return dist[target], path
