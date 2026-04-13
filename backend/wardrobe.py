from fastapi import APIRouter, HTTPException
from database import wardrobe_items
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
        "image_url": request.image_url,
        "tags": request.tags,
        "created_at": datetime.utcnow().isoformat()
    }

    wardrobe_items.append(item)

    return {
        "success": True,
        "message": "Item added successfully",
        "data": item
    }


@router.get("/all")
def get_all_items(user_id: str):
    items = [item for item in wardrobe_items if str(item["user_id"]) == str(user_id)]
    return {
        "success": True,
        "message": "Items retrieved successfully",
        "data": items
    }


@router.get("/{item_id}")
def get_item(item_id: str):
    for item in wardrobe_items:
        if item["id"] == item_id:
            return {
                "success": True,
                "message": "Item retrieved successfully",
                "data": item
            }

    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}")
def update_item(item_id: str, request: UpdateItemRequest):
    for item in wardrobe_items:
        if item["id"] == item_id:
            if request.name is not None:
                item["name"] = request.name
            if request.category is not None:
                raw_category = request.category.strip().lower()
                normalized_category = CATEGORY_MAP.get(raw_category, raw_category)
                item["category"] = normalized_category
            if request.subcategory is not None:
                item["subcategory"] = request.subcategory
            if request.color is not None:
                item["color"] = request.color
            if request.secondary_color is not None:
                item["secondary_color"] = request.secondary_color
            if request.pattern is not None:
                item["pattern"] = request.pattern
            if request.season is not None:
                item["season"] = request.season
            if request.occasion is not None:
                item["occasion"] = request.occasion
            if request.brand is not None:
                item["brand"] = request.brand
            if request.image_url is not None:
                item["image_url"] = request.image_url
            if request.tags is not None:
                item["tags"] = request.tags

            return {
                "success": True,
                "message": "Item updated successfully",
                "data": item
            }

    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}")
def delete_item(item_id: str):
    for index, item in enumerate(wardrobe_items):
        if item["id"] == item_id:
            deleted_item = wardrobe_items.pop(index)
            return {
                "success": True,
                "message": "Item deleted successfully",
                "data": deleted_item
            }

    raise HTTPException(status_code=404, detail="Item not found")