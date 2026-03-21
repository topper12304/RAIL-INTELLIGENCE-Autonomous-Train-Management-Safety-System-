from typing import List
from pydantic import BaseModel
from .core import TrainState


class UnsafeZone(BaseModel):
    start: int
    end: int


class SafetyRequest(BaseModel):
    position: int
    unsafe_zones: List[UnsafeZone]


class SafetyResponse(BaseModel):
    final_state: TrainState
    final_position: int
