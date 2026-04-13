from fastapi import APIRouter, HTTPException
from database import outfits
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

router = APIRouter(prefix="/outfit", tags=["Outfit"])

class SaveOutfitRequest(BaseModel):
    user_id: str
    top_id: Optional[str] = None
    bottom_id: Optional[str] = None
    occasion: str
    shoes_id: Optional[str] = None
    accessories_ids: List[str] = []

@router.post("/save")
def save_outfit(request: SaveOutfitRequest):
    outfit = {
        "id": str(uuid.uuid4()),
        "user_id": request.user_id,
        "top_id": request.top_id,
        "bottom_id": request.bottom_id,
        "occasion": request.occasion,
        "shoes_id": request.shoes_id,
        "accessories_ids": request.accessories_ids,
        "created_at": datetime.utcnow().isoformat()
    }

    outfits.append(outfit)

    return {
        "success": True,
        "message": "Outfit saved successfully",
        "data": outfit
    }

@router.get("/{user_id}")
def get_outfits(user_id: str):
    user_outfits = [o for o in outfits if o["user_id"] == user_id]
    return {
        "success": True,
        "message": "Outfits retrieved successfully",
        "data": user_outfits
    }