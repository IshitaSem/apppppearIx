from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime
from database import db

router = APIRouter(prefix="/outfit", tags=["Outfit"])


class SaveOutfitRequest(BaseModel):
    user_id: str
    top_id: Optional[str] = None
    bottom_id: Optional[str] = None
    occasion: str
    shoes_id: Optional[str] = None
    accessories_ids: List[str] = Field(default_factory=list)


@router.post("/save")
def save_outfit(request: SaveOutfitRequest):
    try:
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

        saved_outfit = db.add_outfit(outfit)

        if not saved_outfit:
            raise HTTPException(status_code=500, detail="Failed to save outfit")

        return {
            "success": True,
            "message": "Outfit saved successfully",
            "data": saved_outfit
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving outfit: {str(e)}")


@router.get("/{user_id}")
def get_outfits(user_id: str):
    try:
        user_outfits = db.get_outfits_by_user(user_id)

        return {
            "success": True,
            "message": "Outfits retrieved successfully",
            "data": user_outfits
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving outfits: {str(e)}")
