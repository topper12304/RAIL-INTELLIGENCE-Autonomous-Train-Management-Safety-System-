from typing import List
from pydantic import BaseModel


class TrainInterval(BaseModel):
    arrival: int   # e.g., minutes since start of day
    departure: int


class PlatformRequest(BaseModel):
    intervals: List[TrainInterval]


class PlatformResponse(BaseModel):
    min_platforms: int
