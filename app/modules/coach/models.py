from typing import List
from pydantic import BaseModel


class CoachInput(BaseModel):
    coach_ids: List[str]
    faulty_index: int  # index in coach_ids that is faulty, -1 if none


class CoachFaultResponse(BaseModel):
    coach_ids: List[str]
    faulty_index: int
