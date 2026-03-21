from .core import Graph


def test_dijkstra_basic():
    g = Graph()
    g.add_edge("A", "B", 1)
    g.add_edge("B", "C", 2)
    g.add_edge("A", "C", 5)

    dist, path = g.dijkstra("A", "C")
    assert dist == 3
    assert path == ["A", "B", "C"]
