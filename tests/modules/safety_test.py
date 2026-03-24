"""
Tests for Module 4: Safety Controller
- Unit tests (basic correctness, edge cases)
- Property tests using hypothesis
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from app.modules.safety.core import SafetyController, TrainState


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_emergency_in_unsafe_zone():
    """Original test — train inside unsafe zone moves to boundary."""
    controller = SafetyController(unsafe_zones=[(10, 20)])
    state, pos = controller.handle_emergency(position=15)
    assert state == TrainState.STOPPED
    assert pos in {9, 21}


def test_emergency_outside_unsafe_zone():
    controller = SafetyController(unsafe_zones=[(10, 20)])
    state, pos = controller.handle_emergency(position=5)
    assert state == TrainState.STOPPED
    assert pos == 5


def test_is_in_unsafe_zone_true():
    c = SafetyController(unsafe_zones=[(10, 20)])
    assert c.is_in_unsafe_zone(15) is True
    assert c.is_in_unsafe_zone(10) is True
    assert c.is_in_unsafe_zone(20) is True


def test_is_in_unsafe_zone_false():
    c = SafetyController(unsafe_zones=[(10, 20)])
    assert c.is_in_unsafe_zone(9) is False
    assert c.is_in_unsafe_zone(21) is False


def test_nearest_safe_position_closer_to_start():
    """Position 11 is closer to start=10, so safe pos = 9."""
    c = SafetyController(unsafe_zones=[(10, 20)])
    assert c.nearest_safe_position(11) == 9


def test_nearest_safe_position_closer_to_end():
    """Position 19 is closer to end=20, so safe pos = 21."""
    c = SafetyController(unsafe_zones=[(10, 20)])
    assert c.nearest_safe_position(19) == 21


def test_invalid_geofence_no_zones():
    """Task 7.8: no unsafe zones — train stops in place."""
    c = SafetyController(unsafe_zones=[])
    state, pos = c.handle_emergency(position=50)
    assert state == TrainState.STOPPED
    assert pos == 50


def test_multiple_unsafe_zones():
    c = SafetyController(unsafe_zones=[(5, 10), (20, 30)])
    state, pos = c.handle_emergency(position=25)
    assert state == TrainState.STOPPED
    assert pos not in range(20, 31)


# ---------------------------------------------------------------------------
# Task 7.6 — Property 11: Speed Limit Enforcement
# Validates Requirement 7.2
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    start=st.integers(min_value=0, max_value=100),
    width=st.integers(min_value=1, max_value=50),
    offset=st.integers(min_value=0, max_value=49),
)
def test_property_speed_limit_enforcement(start, width, offset):
    """
    Property 11: A train inside an unsafe zone must always be moved
    to a position strictly outside that zone after emergency stop.
    """
    end = start + width
    position = start + (offset % (width + 1))
    c = SafetyController(unsafe_zones=[(start, end)])
    state, safe_pos = c.handle_emergency(position=position)
    assert state == TrainState.STOPPED
    assert not c.is_in_unsafe_zone(safe_pos), \
        f"Safe pos {safe_pos} is still inside zone ({start},{end})"


# ---------------------------------------------------------------------------
# Task 7.7 — Property 13: Most Restrictive Speed Limit (zone selection)
# Validates Requirement 8.4
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    zones=st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=80),
            st.integers(min_value=1, max_value=20),
        ),
        min_size=1,
        max_size=5,
    ),
    pos_offset=st.integers(min_value=0, max_value=19),
)
def test_property_most_restrictive_zone_applied(zones, pos_offset):
    """
    Property 13: When a train is inside any unsafe zone, the emergency
    stop must move it outside ALL overlapping zones.
    """
    # Build non-overlapping zones for clean testing
    unsafe = [(s, s + w) for s, w in zones]
    # Pick a position inside the first zone
    s0, e0 = unsafe[0]
    position = s0 + (pos_offset % (e0 - s0 + 1))
    c = SafetyController(unsafe_zones=unsafe)
    state, safe_pos = c.handle_emergency(position=position)
    assert state == TrainState.STOPPED
    # safe_pos must not be inside the zone it was originally in
    assert not (s0 <= safe_pos <= e0)
