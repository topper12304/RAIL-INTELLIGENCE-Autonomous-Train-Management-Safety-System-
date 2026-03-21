from fastapi import APIRouter
from .core import Graph
from .models import NetworkRequest, PathResponse

router = APIRouter()


@router.post("/shortest-path", response_model=PathResponse)
def shortest_path(req: NetworkRequest):
    graph = Graph()
    for edge in req.edges:
        graph.add_edge(edge.u, edge.v, edge.w)

    for blocked in req.blocked_edges:
        graph.remove_edge(blocked.u, blocked.v)

    distance, path = graph.dijkstra(req.source, req.target)
    return PathResponse(distance=distance, path=path)
