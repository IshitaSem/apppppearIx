from fastapi import APIRouter, HTTPException
from database import wardrobe_collection      , serialize_doc, serialize_list
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

    wardrobe_collection.insert_one(item)

    return {
        "success": True,
        "message": "Item added successfully",
        "data": item
    }


@router.get("/all")
def get_all_items(user_id: str):
    items = serialize_list(list(wardrobe_collection.find({"user_id": user_id})))
    return {
        "success": True,
        "message": "Items retrieved successfully",
        "data": items
    }


@router.get("/{item_id}")
def get_item(item_id: str):
    item = wardrobe_collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "success": True,
        "message": "Item retrieved successfully",
        "data": serialize_doc(item)
    }


@router.put("/{item_id}")
def update_item(item_id: str, request: UpdateItemRequest):
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
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
        updates["image_url"] = request.image_url
    if request.tags is not None:
        updates["tags"] = request.tags

    result = wardrobe_collection.update_one(
        {"id": item_id},
        {"$set": updates}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    updated_item = serialize_doc(wardrobe_collection.find_one({"id": item_id}))
    return {
        "success": True,
        "message": "Item updated successfully",
        "data": updated_item
    }


@router.delete("/{item_id}")
def delete_item(item_id: str):
    result = wardrobe_collection.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Fetch deleted item if needed (optional, but to match original)
    deleted_item = None  # Can't fetch after delete easily, but original had data
    return {
        "success": True,
        "message": "Item deleted successfully",
        "data": deleted_item
    }
