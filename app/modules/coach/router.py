from fastapi import APIRouter
from .core import CoachDLL
from .models import CoachInput, CoachFaultResponse

router = APIRouter()


@router.post("/fault-location", response_model=CoachFaultResponse)
def locate_fault(req: CoachInput):
    dll = CoachDLL()
    for idx, cid in enumerate(req.coach_ids):
        dll.append(cid, faulty=(idx == req.faulty_index))

    faulty_index = dll.find_faulty_index()
    return CoachFaultResponse(coach_ids=dll.to_list(), faulty_index=faulty_index)
