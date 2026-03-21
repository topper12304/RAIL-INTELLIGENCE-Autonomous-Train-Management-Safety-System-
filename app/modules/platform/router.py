from fastapi import APIRouter
from .core import min_platforms
from .models import PlatformRequest, PlatformResponse

router = APIRouter()


@router.post("/min-platforms", response_model=PlatformResponse)
def compute_min_platforms(req: PlatformRequest):
    intervals = [(t.arrival, t.departure) for t in req.intervals]
    result = min_platforms(intervals)
    return PlatformResponse(min_platforms=result)
