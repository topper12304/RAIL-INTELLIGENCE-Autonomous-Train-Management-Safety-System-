from typing import List
from pydantic import BaseModel


class Edge(BaseModel):
    u: str
    v: str
    w: float


class NetworkRequest(BaseModel):
    nodes: List[str]
    edges: List[Edge]
    blocked_edges: List[Edge] = []
    source: str
    target: str


class PathResponse(BaseModel):
    distance: float
    path: List[str]
