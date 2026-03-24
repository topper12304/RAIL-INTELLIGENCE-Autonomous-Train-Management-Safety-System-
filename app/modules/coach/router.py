from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import sys
import os

# Core logic import
from app.modules.coach.core import CoachDLL

# Task 9: Database import fix
try:
    from app.database import log_fault
except ImportError:
    # Agar direct import na ho, toh path add karein
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from database import log_fault

router = APIRouter()

class CoachInput(BaseModel):
    id: str
    is_faulty: bool = False

class CoachRequest(BaseModel):
    coaches: List[CoachInput]

@router.post("/fault-location")
def get_fault(req: CoachRequest):
    train = CoachDLL()
    for c in req.coaches:
        train.append(c.id, c.is_faulty)
    
    result = train.locate_fault_dfs()
    
    if result:
        try:
            log_fault(result["coach_id"], result["position"])
        except Exception as e:
            print(f"DB Error: {e}")
            
        return {"status": "Fault Detected", "result": result}
    return {"status": "Healthy", "message": "All coaches fine"}