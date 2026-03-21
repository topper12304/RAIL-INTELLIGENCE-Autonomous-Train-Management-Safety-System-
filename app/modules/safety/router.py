from fastapi import APIRouter
from .core import SafetyController
from .models import SafetyRequest, SafetyResponse

router = APIRouter()


@router.post("/emergency-stop", response_model=SafetyResponse)
def emergency_stop(req: SafetyRequest):
    unsafe_zones = [(z.start, z.end) for z in req.unsafe_zones]
    controller = SafetyController(unsafe_zones=unsafe_zones)
    final_state, final_position = controller.handle_emergency(req.position)
    return SafetyResponse(final_state=final_state, final_position=final_position)
