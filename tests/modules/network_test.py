"""
Tests for Module 1: Dynamic Network Rescheduler
- Unit tests (basic correctness, edge cases)
- Property tests using hypothesis
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.modules.network.core import NetworkGraph, RoutingRequest


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_dijkstra_basic():
    """Basic shortest path: A->B->C should beat A->C direct."""
    g = NetworkGraph()
    g.add_track_segment("A", "B", 1)
    g.add_track_segment("B", "C", 2)
    g.add_track_segment("A", "C", 5)
    dist, path = g.compute_route("A", "C")
    assert dist == 3
    assert path == ["A", "B", "C"]


def test_disconnected_graph_returns_no_path():
    """Task 3.5: disconnected graph should return empty path."""
    g = NetworkGraph()
    g.add_track_segment("A", "B", 1)
    g.add_track_segment("C", "D", 1)
    dist, path = g.compute_route("A", "D")
    assert dist == float("inf")
    assert path == []


def test_single_node_graph():
    """Task 3.5: source == target should return distance 0."""
    g = NetworkGraph()
    g.add_track_segment("A", "B", 1)
    dist, path = g.compute_route("A", "A")
    assert dist == 0
    assert path == ["A"]


def test_invalid_station_ids():
    """Task 3.5: unknown station returns no path."""
    g = NetworkGraph()
    g.add_track_segment("A", "B", 1)
    dist, path = g.compute_route("A", "Z")
    assert dist == float("inf")
    assert path == []


def test_mark_segment_unavailable():
    """Task 3.1: unavailable segment must be excluded from routing."""
    g = NetworkGraph()
    g.add_track_segment("A", "B", 1)
    g.add_track_segment("B", "C", 1)
    g.add_track_segment("A", "C", 10)
    g.mark_segment_unavailable("A", "B")
    dist, path = g.compute_route("A", "C")
    # Must use A->C direct (10) since A->B is blocked
    assert dist == 10
    assert "B" not in path


def test_mark_segment_available_restores_route():
    g = NetworkGraph()
    g.add_track_segment("A", "B", 1)
    g.add_track_segment("B", "C", 1)
    g.add_track_segment("A", "C", 10)
    g.mark_segment_unavailable("A", "B")
    g.mark_segment_available("A", "B")
    dist, path = g.compute_route("A", "C")
    assert dist == 2


def test_get_network_status():
    g = NetworkGraph()
    g.add_track_segment("A", "B", 1)
    g.add_track_segment("B", "C", 2)
    g.mark_segment_unavailable("A", "B")
    status = g.get_network_status()
    assert status["total_segments"] == 2
    assert status["blocked_segments"] == 1
    assert status["available_segments"] == 1


# ---------------------------------------------------------------------------
# Task 3.6 — Priority queue tests
# ---------------------------------------------------------------------------

def test_priority_queue_premium_before_standard():
    """Task 3.8: premium (priority=1) dequeued before standard (priority=2)."""
    g = NetworkGraph()
    g.enqueue_request(RoutingRequest("T2", "A", "C", priority=2))
    g.enqueue_request(RoutingRequest("T1", "A", "C", priority=1))
    first = g.dequeue_request()
    assert first is not None
    assert first.priority == 1
    assert first.train_id == "T1"


def test_priority_queue_empty_returns_none():
    g = NetworkGraph()
    assert g.dequeue_request() is None


# ---------------------------------------------------------------------------
# Task 3.3 — Property 1: Optimal Route Selection
# Validates Requirement 1.2
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    w_ab=st.floats(min_value=0.1, max_value=100.0),
    w_bc=st.floats(min_value=0.1, max_value=100.0),
    w_ac=st.floats(min_value=0.1, max_value=100.0),
)
def test_property_optimal_route_selection(w_ab, w_bc, w_ac):
    """
    Property 1: Dijkstra always returns the minimum-cost path.
    For a 3-node graph, the returned distance must equal
    min(direct, via-B).
    """
    g = NetworkGraph()
    g.add_track_segment("A", "B", w_ab)
    g.add_track_segment("B", "C", w_bc)
    g.add_track_segment("A", "C", w_ac)
    dist, path = g.compute_route("A", "C")
    expected = min(w_ac, w_ab + w_bc)
    assert abs(dist - expected) < 1e-9
    assert path[0] == "A" and path[-1] == "C"


# ---------------------------------------------------------------------------
# Task 3.4 — Property 2: Unavailable Segment Exclusion
# Validates Requirement 1.3
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    w_ab=st.floats(min_value=0.1, max_value=50.0),
    w_bc=st.floats(min_value=0.1, max_value=50.0),
    w_ac=st.floats(min_value=0.1, max_value=50.0),
)
def test_property_unavailable_segment_excluded(w_ab, w_bc, w_ac):
    """
    Property 2: When A-B is marked unavailable, the returned path
    must never contain edge A->B.
    """
    g = NetworkGraph()
    g.add_track_segment("A", "B", w_ab)
    g.add_track_segment("B", "C", w_bc)
    g.add_track_segment("A", "C", w_ac)
    g.mark_segment_unavailable("A", "B")
    dist, path = g.compute_route("A", "C")
    # B must not appear consecutively after A in path
    for i in range(len(path) - 1):
        assert not (path[i] == "A" and path[i + 1] == "B"), \
            "Blocked segment A->B appeared in path"
    assert dist == w_ac


# ---------------------------------------------------------------------------
# Task 3.7 — Property 3: Priority Queue Ordering
# Validates Requirement 2.1
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(st.lists(st.integers(min_value=1, max_value=2), min_size=1, max_size=20))
def test_property_priority_queue_ordering(priorities):
    """
    Property 3: Dequeuing always yields requests in non-decreasing priority order.
    """
    g = NetworkGraph()
    for i, p in enumerate(priorities):
        g.enqueue_request(RoutingRequest(f"T{i}", "A", "B", priority=p))
    dequeued = []
    while True:
        req = g.dequeue_request()
        if req is None:
            break
        dequeued.append(req.priority)
    assert dequeued == sorted(dequeued)
