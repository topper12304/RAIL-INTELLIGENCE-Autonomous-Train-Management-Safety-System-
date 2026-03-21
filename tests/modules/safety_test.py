from .core import SafetyController, TrainState


def test_emergency_in_unsafe_zone():
    controller = SafetyController(unsafe_zones=[(10, 20)])
    state, pos = controller.handle_emergency(position=15)
    assert state == TrainState.STOPPED
    assert pos in {9, 21}
