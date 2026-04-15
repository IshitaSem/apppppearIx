from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter(prefix="/tools", tags=["Fashion Tools"])


@router.get("/outfit-generator")
def outfit_generator(user_id: str):
    try:
        items = db.get_user_items(user_id)

        if not items:
            raise HTTPException(status_code=400, detail="No wardrobe items found")

        tops = [i for i in items if i.get("category") == "top"]
        bottoms = [i for i in items if i.get("category") == "bottom"]
        dresses = [i for i in items if i.get("category") == "dress"]

        outfit = {}

        if dresses:
            outfit["dress"] = dresses[0]
        elif tops and bottoms:
            outfit["top"] = tops[0]
            outfit["bottom"] = bottoms[0]

        return {
            "success": True,
            "message": "Outfit generated",
            "data": outfit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cat-judge")
def cat_judge():
    return {
        "success": True,
        "message": "😼 Meow! Your outfit is approved by the fashion cat!"
    }
