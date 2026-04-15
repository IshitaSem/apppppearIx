from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter(prefix="/ai", tags=["AI Stylist"])


def serialize_item(item: dict) -> dict:
    if not item:
        return {}

    image_url = item.get("image_url", "")
    if image_url and not image_url.startswith("http"):
        if not image_url.startswith("/"):
            image_url = f"/{image_url}"

    return {
        "id": str(item.get("id", "")),
        "user_id": str(item.get("user_id", "")),
        "name": item.get("name", ""),
        "category": item.get("category", ""),
        "subcategory": item.get("subcategory"),
        "color": item.get("color", "unknown"),
        "secondary_color": item.get("secondary_color"),
        "pattern": item.get("pattern"),
        "season": item.get("season"),
        "occasion": item.get("occasion"),
        "brand": item.get("brand"),
        "image_url": image_url,
        "tags": item.get("tags", []),
        "created_at": str(item.get("created_at", "")),
    }


@router.get("/generate-outfit")
def generate_outfit(user_id: str, occasion: str):
    items = db.get_user_items(user_id)

    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items found for this user")

    tops = [item for item in items if str(item.get("category", "")).lower() in ["top", "tops"]]
    bottoms = [item for item in items if str(item.get("category", "")).lower() in ["bottom", "bottoms"]]
    dresses = [item for item in items if str(item.get("category", "")).lower() in ["dress", "dresses"]]
    shoes = [item for item in items if str(item.get("category", "")).lower() in ["shoe", "shoes"]]
    accessories = [item for item in items if str(item.get("category", "")).lower() in ["accessory", "accessories"]]

    occasion_lower = occasion.strip().lower()

    outfit_items = []
    notes = []

    if occasion_lower in ["casual", "casual day", "college", "daily", "everyday"]:
        if tops and bottoms:
            outfit_items.append(serialize_item(tops[0]))
            outfit_items.append(serialize_item(bottoms[0]))
            notes.append("Picked a casual top and bottom combination.")
        elif dresses:
            outfit_items.append(serialize_item(dresses[0]))
            notes.append("Picked an easy casual dress option.")
        else:
            raise HTTPException(status_code=400, detail="Not enough wardrobe items to create a casual outfit")

    elif occasion_lower in ["formal", "office", "interview", "party"]:
        if dresses:
            outfit_items.append(serialize_item(dresses[0]))
            notes.append("Picked a dress suitable for a more dressed-up occasion.")
        elif tops and bottoms:
            outfit_items.append(serialize_item(tops[0]))
            outfit_items.append(serialize_item(bottoms[0]))
            notes.append("Picked a polished top and bottom combination.")
        else:
            raise HTTPException(status_code=400, detail="Not enough wardrobe items to create a formal outfit")

    else:
        if tops and bottoms:
            outfit_items.append(serialize_item(tops[0]))
            outfit_items.append(serialize_item(bottoms[0]))
            notes.append("Picked a balanced outfit from available wardrobe items.")
        elif dresses:
            outfit_items.append(serialize_item(dresses[0]))
            notes.append("Picked a dress from available wardrobe items.")
        else:
            raise HTTPException(status_code=400, detail="Not enough wardrobe items to create an outfit")

    if shoes:
        outfit_items.append(serialize_item(shoes[0]))
        notes.append("Added shoes to complete the look.")

    if accessories:
        outfit_items.append(serialize_item(accessories[0]))
        notes.append("Added an accessory for styling.")

    return {
        "success": True,
        "occasion": occasion,
        "user_id": user_id,
        "items": outfit_items,
        "notes": notes,
    }
