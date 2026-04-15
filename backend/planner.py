from fastapi import APIRouter
from database import db
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/planner", tags=["Planner"])

class SavePlanRequest(BaseModel):
    user_id: str
    outfit_id: str
    date: str

@router.post("/save")
def save_plan(request: SavePlanRequest):
    plan = {
        "id": str(uuid.uuid4()),
        "user_id": request.user_id,
        "outfit_id": request.outfit_id,
        "date": request.date
    }

    added_plan = db.save_plan(plan)
    if added_plan:
        return {
            "success": True,
            "message": "Outfit planned successfully",
            "plan": added_plan
        }
    raise HTTPException(status_code=500, detail="Failed to save plan")


@router.get("/{user_id}")
def get_plans(user_id: str):
    user_plans = db.get_user_plans(user_id)
    return {
        "success": True,
        "plans": user_plans
    }
