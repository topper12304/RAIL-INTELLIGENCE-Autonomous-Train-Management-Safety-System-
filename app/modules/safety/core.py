from enum import Enum
from typing import Tuple, List


class TrainState(str, Enum):
    MOVING = "MOVING"
    STOPPED = "STOPPED"
    EMERGENCY_REQUESTED = "EMERGENCY_REQUESTED"


class SafetyController:
    def __init__(self, unsafe_zones: List[Tuple[int, int]]) -> None:
        """
        unsafe_zones: list of (start_km, end_km) representing bridges/tunnels.
        """
        self.state = TrainState.MOVING
        self.unsafe_zones = unsafe_zones

    def is_in_unsafe_zone(self, position: int) -> bool:
        return any(start <= position <= end for start, end in self.unsafe_zones)

    def nearest_safe_position(self, position: int) -> int:
        """
        Move to nearest boundary outside unsafe zone.
        """
        for start, end in self.unsafe_zones:
            if start <= position <= end:
                # choose nearest edge
                if position - start <= end - position:
                    return start - 1
                else:
                    return end + 1
        return position

    def handle_emergency(self, position: int) -> Tuple[TrainState, int]:
        """
        If emergency requested in unsafe zone, move to nearest safe position.
        Returns final state and final position.
        """
        self.state = TrainState.EMERGENCY_REQUESTED
        if self.is_in_unsafe_zone(position):
            safe_pos = self.nearest_safe_position(position)
            self.state = TrainState.STOPPED
            return self.state, safe_pos
        else:
            self.state = TrainState.STOPPED
            return self.state, position
