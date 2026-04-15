from fastapi import APIRouter, HTTPException
from database import db
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])


class AddItemRequest(BaseModel):
    user_id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    color: str = "unknown"
    secondary_color: Optional[str] = None
    pattern: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

CATEGORY_MAP = {
    "tops": "top", "top": "top",
    "bottoms": "bottom", "bottom": "bottom",
    "dresses": "dress", "dress": "dress",
    "shoes": "shoes", "shoe": "shoes",
    "accessories": "accessories", "accessory": "accessories",
    "outerwear": "outerwear",
    "bag": "accessories", "bags": "accessories", "jewelry": "accessories", "jewellery": "accessories"
}


class UpdateItemRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    color: Optional[str] = None
    secondary_color: Optional[str] = None
    pattern: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("/add")
def add_item(request: AddItemRequest):
    # Normalize category
    raw_category = request.category.strip().lower()
    normalized_category = CATEGORY_MAP.get(raw_category, raw_category)
    
    item = {
        "id": str(uuid.uuid4()),
        "user_id": str(request.user_id),
        "name": request.name.strip(),
        "category": normalized_category,
        "subcategory": request.subcategory,
        "color": request.color,
        "secondary_color": request.secondary_color,
        "pattern": request.pattern,
        "season": request.season,
        "occasion": request.occasion,
        "brand": request.brand,
        "image_url": request.image_url or "",
        "tags": request.tags,
        "created_at": datetime.utcnow().isoformat()
    }

    added_item = db.add_item(item)
    if added_item:
        return {
            "success": True,
            "message": "Item added successfully",
            "data": added_item
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to add item")


@router.get("/all")
def get_all_items(user_id: str):
    items = db.get_user_items(str(user_id))
    for item in items:
        item["image_url"] = item.get("image_url", "")
    return {
        "success": True,
        "message": "Items retrieved successfully",
        "data": items
    }


@router.get("/{item_id}")
def get_item(item_id: str):
    item = db.get_item(item_id)
    if item:
        item["image_url"] = item.get("image_url", "")
        return {
            "success": True,
            "message": "Item retrieved successfully",
            "data": item
        }
    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}")
def update_item(item_id: str, request: UpdateItemRequest):
    updates = {}
    if request.name is not None:
        updates["name"] = request.name.strip()
    if request.category is not None:
        raw_category = request.category.strip().lower()
        normalized_category = CATEGORY_MAP.get(raw_category, raw_category)
        updates["category"] = normalized_category
    if request.subcategory is not None:
        updates["subcategory"] = request.subcategory
    if request.color is not None:
        updates["color"] = request.color
    if request.secondary_color is not None:
        updates["secondary_color"] = request.secondary_color
    if request.pattern is not None:
        updates["pattern"] = request.pattern
    if request.season is not None:
        updates["season"] = request.season
    if request.occasion is not None:
        updates["occasion"] = request.occasion
    if request.brand is not None:
        updates["brand"] = request.brand
    if request.image_url is not None:
        updates["image_url"] = request.image_url or ""
    if request.tags is not None:
        updates["tags"] = request.tags

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if db.update_item(item_id, updates):
        updated_item = db.get_item(item_id)
        if updated_item:
            updated_item["image_url"] = updated_item.get("image_url", "")
            return {
                "success": True,
                "message": "Item updated successfully",
                "data": updated_item
            }
    raise HTTPException(status_code=404, detail="Item not found or update failed")


@router.delete("/{item_id}")
def delete_item(item_id: str):
    if db.delete_item(item_id):
        return {
            "success": True,
            "message": "Item deleted successfully",
            "data": {"id": item_id}
        }
    raise HTTPException(status_code=404, detail="Item not found")
