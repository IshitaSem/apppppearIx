from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter(prefix="/ai", tags=["AI Stylist"])


@router.get("/generate-outfit")
def generate_outfit(user_id: str, occasion: str):
    try:
        # get items from MongoDB
        items = db.get_items_by_user(user_id)

        if not items:
            raise HTTPException(status_code=400, detail="No wardrobe items found")

        tops = [i for i in items if i.get("category") == "top"]
        bottoms = [i for i in items if i.get("category") == "bottom"]
        dresses = [i for i in items if i.get("category") == "dress"]
        shoes = [i for i in items if i.get("category") == "shoes"]
        accessories = [i for i in items if i.get("category") == "accessories"]

        outfit = {}

        if dresses:
            outfit["dress"] = dresses[0]
        else:
            if tops and bottoms:
                outfit["top"] = tops[0]
                outfit["bottom"] = bottoms[0]

        if shoes:
            outfit["shoes"] = shoes[0]

        if accessories:
            outfit["accessories"] = accessories[:2]

        return {
            "success": True,
            "message": "Outfit generated",
            "data": outfit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
