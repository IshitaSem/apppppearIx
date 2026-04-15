from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter(prefix="/ai", tags=["AI Stylist"])


@router.get("/generate-outfit")
def generate_outfit(user_id: str, occasion: str):
    try:
        items = db.get_user_items(str(user_id))

        if not items:
            raise HTTPException(status_code=400, detail="No wardrobe items found")

        occasion = occasion.strip().lower()

        tops = [i for i in items if i.get("category") == "top"]
        bottoms = [i for i in items if i.get("category") == "bottom"]
        dresses = [i for i in items if i.get("category") == "dress"]
        shoes = [i for i in items if i.get("category") == "shoes"]
        accessories = [i for i in items if i.get("category") == "accessories"]

        outfit = {}
        notes = []

        if occasion in ["casual", "college"]:
            if tops and bottoms:
                outfit["top"] = tops[0]
                outfit["bottom"] = bottoms[0]
                notes.append("Picked a simple top and bottom for a casual look.")
            elif dresses:
                outfit["dress"] = dresses[0]
                notes.append("Picked a dress for an easy casual outfit.")
        elif occasion in ["formal", "office", "party"]:
            if dresses:
                outfit["dress"] = dresses[0]
                notes.append("Picked a dress for a polished look.")
            elif tops and bottoms:
                outfit["top"] = tops[0]
                outfit["bottom"] = bottoms[0]
                notes.append("Picked a top and bottom for a neat formal outfit.")
        else:
            if tops and bottoms:
                outfit["top"] = tops[0]
                outfit["bottom"] = bottoms[0]
                notes.append("Picked a balanced outfit from your wardrobe.")
            elif dresses:
                outfit["dress"] = dresses[0]
                notes.append("Picked a dress from your wardrobe.")

        if shoes:
            outfit["shoes"] = shoes[0]

        if accessories:
            outfit["accessories"] = accessories[:2]

        if not outfit:
            raise HTTPException(
                status_code=400,
                detail="Not enough wardrobe items to generate an outfit"
            )

        return {
            "success": True,
            "message": "Outfit generated successfully",
            "data": outfit,
            "notes": notes
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating outfit: {str(e)}")
