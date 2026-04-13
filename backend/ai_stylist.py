from fastapi import APIRouter
from database import wardrobe_items
from wardrobe import CATEGORY_MAP
from pydantic import BaseModel
from typing import List, Dict
import random

router = APIRouter(prefix="/ai", tags=["AI Stylist"])

class GenerateOutfitRequest(BaseModel):
    user_id: str
    occasion: str

def normalize_category(cat: str) -> str:
    return CATEGORY_MAP.get(cat.lower().strip(), cat.lower().strip())

def get_user_items(user_id: str) -> List[Dict]:
    items = [i for i in wardrobe_items if i.get("user_id") == user_id]
    for item in items:
        cat = item.get("category", "")
        if cat:
            item["category"] = normalize_category(cat)
    return items

def fix_item_image(item: Dict):
    image_url = item.get("image_url") or item.get("image_path", "")
    if not image_url:
        image_url = ""
    item["image_url"] = image_url
    return item

@router.get("/generate-outfit")
def generate_outfit(user_id: str, occasion: str):
    items = get_user_items(user_id)
    if not items:
        return {
            "success": True,
            "data": {
                "outfit": {},
                "styling_notes": ["Add items to wardrobe for outfits."]
            }
        }
    
    # Groups
    tops = [fix_item_image(i.copy()) for i in items if normalize_category(i.get("category", "")) == "top"]
    bottoms = [fix_item_image(i.copy()) for i in items if normalize_category(i.get("category", "")) == "bottom"]
    dresses = [fix_item_image(i.copy()) for i in items if normalize_category(i.get("category", "")) == "dress"]
    shoes = [fix_item_image(i.copy()) for i in items if normalize_category(i.get("category", "")) == "shoes"]
    accessories = [fix_item_image(i.copy()) for i in items if normalize_category(i.get("category", "")) == "accessories"]
    
    outfit = {}
    notes = []
    
    occ_lower = occasion.lower()
    
    # Simple rules - 2-5 items
    if "college" in occ_lower or "casual" in occ_lower or "work" in occ_lower:
        if tops and bottoms:
            outfit["top"] = random.choice(tops)
            outfit["bottom"] = random.choice(bottoms)
            notes.append("Casual top + bottom combo.")
        elif dresses:
            outfit["dress"] = random.choice(dresses)
            notes.append("Casual dress look.")
    elif "party" in occ_lower or "date" in occ_lower:
        if dresses:
            outfit["dress"] = random.choice(dresses)
            notes.append("Party dress.")
        elif tops and bottoms:
            outfit["top"] = random.choice(tops)
            outfit["bottom"] = random.choice(bottoms)
            notes.append("Party ready outfit.")
    elif "travel" in occ_lower or "comfy" in occ_lower:
        if tops:
            outfit["top"] = random.choice(tops)
        if bottoms:
            outfit["bottom"] = random.choice(bottoms)
            notes.append("Comfy travel fit.")
    else:
        # Default
        if tops:
            outfit["top"] = random.choice(tops)
        if bottoms:
            outfit["bottom"] = random.choice(bottoms)
        notes.append("Everyday outfit.")
    
    # Add shoe if available (limit 5)
    if shoes and len(outfit) < 5:
        outfit["shoes"] = random.choice(shoes)
        notes.append("Shoes complete the look.")
    
    # Add 1 accessory if available
    if accessories and len(outfit) < 5:
        outfit["accessories"] = [random.choice(accessories)]
        notes.append("Accessory adds style.")
    
    # Final notes
    if len(outfit) > 0:
        notes.insert(0, f"Curated {len(outfit)}-piece outfit for {occasion}.")
    
    return {
        "success": True,
        "data": {
            "outfit": outfit,
            "styling_notes": notes
        }
    }

@router.post("/generate-outfit")
def generate_outfit_post(request: GenerateOutfitRequest):
    return generate_outfit(request.user_id, request.occasion)

