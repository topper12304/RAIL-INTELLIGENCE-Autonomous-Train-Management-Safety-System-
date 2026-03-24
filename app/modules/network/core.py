from typing import Dict, List, Tuple, Optional
import heapq


class TrackSegment:
    """Represents a single track segment between two stations."""
    def __init__(self, u: str, v: str, weight: float) -> None:
        self.u = u
        self.v = v
        self.weight = weight
        self.available: bool = True


class RoutingRequest:
    """A train routing request with priority (1=premium, 2=standard)."""
    def __init__(self, train_id: str, source: str, target: str, priority: int = 2) -> None:
        self.train_id = train_id
        self.source = source
        self.target = target
        self.priority = priority  # 1 = premium, 2 = standard

    def __lt__(self, other: "RoutingRequest") -> bool:
        return self.priority < other.priority


class NetworkGraph:
    """Railway network graph with adjacency list storage."""

    def __init__(self) -> None:
        self.adj: Dict[str, List[Tuple[str, float]]] = {}
        self._segments: List[TrackSegment] = []
        self._unavailable: set = set()          # frozenset({u,v}) of blocked edges
        self._request_queue: List[RoutingRequest] = []

    # ------------------------------------------------------------------ #
    #  Graph construction                                                  #
    # ------------------------------------------------------------------ #

    def add_track_segment(self, u: str, v: str, weight: float) -> None:
        """Add a bidirectional track segment."""
        seg = TrackSegment(u, v, weight)
        self._segments.append(seg)
        self.adj.setdefault(u, []).append((v, weight))
        self.adj.setdefault(v, []).append((u, weight))

    # Keep old name for backward-compat with existing router
    def add_edge(self, u: str, v: str, w: float) -> None:
        self.add_track_segment(u, v, w)

    # ------------------------------------------------------------------ #
    #  Segment availability                                                #
    # ------------------------------------------------------------------ #

    def mark_segment_unavailable(self, u: str, v: str) -> None:
        self._unavailable.add(frozenset({u, v}))

    def mark_segment_available(self, u: str, v: str) -> None:
        self._unavailable.discard(frozenset({u, v}))

    def remove_edge(self, u: str, v: str) -> None:
        """Hard-remove an edge (used by router for blocked_edges)."""
        if u in self.adj:
            self.adj[u] = [(node, w) for node, w in self.adj[u] if node != v]
        if v in self.adj:
            self.adj[v] = [(node, w) for node, w in self.adj[v] if node != u]

    def get_network_status(self) -> Dict[str, object]:
        """Return current network status summary."""
        total = len(self._segments)
        blocked = len(self._unavailable)
        return {
            "total_segments": total,
            "available_segments": total - blocked,
            "blocked_segments": blocked,
            "nodes": list(self.adj.keys()),
        }

    # ------------------------------------------------------------------ #
    #  Routing                                                             #
    # ------------------------------------------------------------------ #

    def compute_route(self, source: str, target: str) -> Tuple[float, List[str]]:
        """Dijkstra ignoring unavailable segments. Returns (distance, path)."""
        if source not in self.adj or target not in self.adj:
            return float("inf"), []

        dist: Dict[str, float] = {node: float("inf") for node in self.adj}
        prev: Dict[str, Optional[str]] = {node: None for node in self.adj}
        dist[source] = 0.0
        heap: List[Tuple[float, str]] = [(0.0, source)]

        while heap:
            d, u = heapq.heappop(heap)
            if u == target:
                break
            if d > dist[u]:
                continue
            for v, w in self.adj.get(u, []):
                if frozenset({u, v}) in self._unavailable:
                    continue
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        if dist[target] == float("inf"):
            return float("inf"), []

        path: List[str] = []
        cur: Optional[str] = target
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return dist[target], path

    # Keep old name for backward-compat
    def dijkstra(self, source: str, target: str) -> Tuple[float, List[str]]:
        return self.compute_route(source, target)

    # ------------------------------------------------------------------ #
    #  Priority queue for routing requests                                 #
    # ------------------------------------------------------------------ #

    def enqueue_request(self, request: RoutingRequest) -> None:
        """Add a routing request to the priority queue."""
        heapq.heappush(self._request_queue, request)

    def dequeue_request(self) -> Optional[RoutingRequest]:
        """Pop the highest-priority routing request (lowest priority number)."""
        if not self._request_queue:
            return None
        return heapq.heappop(self._request_queue)


# ---------------------------------------------------------------------------
# Backward-compat alias so existing router (which imports Graph) still works
# ---------------------------------------------------------------------------
Graph = NetworkGraph
