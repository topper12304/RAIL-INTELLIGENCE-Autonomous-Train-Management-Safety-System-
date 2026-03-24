"""
Tests for Module 2: Smart ACP & Fault Localization
- Unit tests (basic correctness, edge cases)
- Property tests using hypothesis
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.modules.coach.core import TrainComposition, CoachDLL, FaultLocation


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_faulty_coach():
    """Original test — kept working via find_faulty_index alias."""
    dll = CoachDLL()
    dll.append("C1")
    dll.append("C2", faulty=True)
    dll.append("C3")
    assert dll.find_faulty_index() == 1


def test_locate_fault_dfs_returns_correct_position():
    t = TrainComposition()
    t.add_coach("C1")
    t.add_coach("C2")
    t.add_coach("C3", faulty=True)
    result = t.locate_fault_dfs()
    assert result is not None
    assert result["coach_id"] == "C3"
    assert result["position"] == 3


def test_no_fault_returns_none():
    t = TrainComposition()
    t.add_coach("C1")
    t.add_coach("C2")
    assert t.locate_fault_dfs() is None


def test_empty_train_returns_none():
    """Task 4.7: empty composition."""
    t = TrainComposition()
    assert t.locate_fault_dfs() is None


def test_single_coach_faulty():
    """Task 4.7: single faulty coach."""
    t = TrainComposition()
    t.add_coach("C1", faulty=True)
    result = t.locate_fault_dfs()
    assert result["position"] == 1


def test_remove_coach():
    t = TrainComposition()
    t.add_coach("C1")
    t.add_coach("C2")
    t.add_coach("C3")
    removed = t.remove_coach("C2")
    assert removed is True
    assert t.get_train_composition() == ["C1", "C3"]


def test_remove_nonexistent_coach():
    t = TrainComposition()
    t.add_coach("C1")
    assert t.remove_coach("X99") is False


def test_get_train_composition_order():
    t = TrainComposition()
    for cid in ["C1", "C2", "C3", "C4"]:
        t.add_coach(cid)
    assert t.get_train_composition() == ["C1", "C2", "C3", "C4"]


def test_add_coach_at_position():
    t = TrainComposition()
    t.add_coach("C1")
    t.add_coach("C3")
    t.add_coach("C2", position=1)   # insert between C1 and C3
    assert t.get_train_composition() == ["C1", "C2", "C3"]


def test_add_coach_prepend():
    t = TrainComposition()
    t.add_coach("C2")
    t.add_coach("C1", position=0)
    assert t.get_train_composition() == ["C1", "C2"]


# ---------------------------------------------------------------------------
# Task 4.4 — Property 5: Bidirectional Traversal Completeness
# Validates Requirement 3.4
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(st.lists(st.text(min_size=1, max_size=5), min_size=1, max_size=20, unique=True))
def test_property_bidirectional_traversal(coach_ids):
    """
    Property 5: Forward traversal and reverse traversal must contain
    the same elements in opposite order.
    """
    t = TrainComposition()
    for cid in coach_ids:
        t.add_coach(cid)
    forward = t.get_train_composition()
    backward = t.get_train_composition_reverse()
    assert forward == list(reversed(backward))
    assert set(forward) == set(coach_ids)


# ---------------------------------------------------------------------------
# Task 4.2 — Property 6: Coach Insertion Correctness
# Validates Requirement 4.2
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    coach_ids=st.lists(st.text(min_size=1, max_size=4), min_size=2, max_size=15, unique=True),
    insert_pos=st.integers(min_value=0, max_value=14),
)
def test_property_coach_insertion_correctness(coach_ids, insert_pos):
    """
    Property 6: After inserting a coach at position p, the composition
    length increases by 1 and the new coach appears at the correct position.
    """
    t = TrainComposition()
    for cid in coach_ids:
        t.add_coach(cid)
    before_len = len(t)
    new_id = "NEW_COACH"
    clamped_pos = min(insert_pos, before_len)
    t.add_coach(new_id, position=clamped_pos)
    composition = t.get_train_composition()
    assert len(t) == before_len + 1
    assert composition[clamped_pos] == new_id


# ---------------------------------------------------------------------------
# Task 4.3 — Property 7: Coach Deletion Integrity
# Validates Requirement 4.3
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(st.lists(st.text(min_size=1, max_size=5), min_size=2, max_size=20, unique=True))
def test_property_coach_deletion_integrity(coach_ids):
    """
    Property 7: After removing a coach, it no longer appears in the
    composition and the list length decreases by 1.
    """
    t = TrainComposition()
    for cid in coach_ids:
        t.add_coach(cid)
    target = coach_ids[len(coach_ids) // 2]
    before_len = len(t)
    result = t.remove_coach(target)
    assert result is True
    composition = t.get_train_composition()
    assert target not in composition
    assert len(t) == before_len - 1


# ---------------------------------------------------------------------------
# Task 4.6 — Property 4: Fault Localization Accuracy
# Validates Requirement 3.2
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    n=st.integers(min_value=1, max_value=20),
    fault_idx=st.integers(min_value=0, max_value=19),
)
def test_property_fault_localization_accuracy(n, fault_idx):
    """
    Property 4: DFS must find the fault at exactly the position it was inserted.
    """
    if fault_idx >= n:
        fault_idx = n - 1
    t = TrainComposition()
    for i in range(n):
        t.add_coach(f"C{i}", faulty=(i == fault_idx))
    result = t.locate_fault_dfs()
    assert result is not None
    assert result["coach_id"] == f"C{fault_idx}"
    assert result["position"] == fault_idx + 1  # 1-indexed
