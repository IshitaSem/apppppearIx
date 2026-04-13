from fastapi import APIRouter
from database import planner
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

    planner.append(plan)

    return {
        "message": "Outfit planned successfully",
        "plan": plan
    }

@router.get("/{user_id}")
def get_plans(user_id: str):
    user_plans = [p for p in planner if p["user_id"] == user_id]
    return {"plans": user_plans}