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
    image_path: Optional[str] = None
    original_image_url: Optional[str] = None
    background_removed: bool = False
    tags: List[str] = Field(default_factory=list)


CATEGORY_MAP = {
    "tops": "top",
    "top": "top",
    "bottoms": "bottom",
    "bottom": "bottom",
    "dresses": "dress",
    "dress": "dress",
    "shoes": "shoes",
    "shoe": "shoes",
    "accessories": "accessories",
    "accessory": "accessories",
    "outerwear": "outerwear",
    "bag": "accessories",
    "bags": "accessories",
    "jewelry": "accessories",
    "jewellery": "accessories",
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
    image_path: Optional[str] = None
    original_image_url: Optional[str] = None
    background_removed: Optional[bool] = None
    tags: Optional[List[str]] = None


def normalize_category(category: str) -> str:
    raw_category = category.strip().lower()
    return CATEGORY_MAP.get(raw_category, raw_category)


def normalize_item(item: dict) -> dict:
    if not item:
        return item

    item.pop("_id", None)

    item["id"] = str(item.get("id", ""))
    item["user_id"] = str(item.get("user_id", ""))
    item["name"] = item.get("name", "")
    item["category"] = item.get("category", "unknown")
    item["subcategory"] = item.get("subcategory")
    item["color"] = item.get("color", "unknown")
    item["secondary_color"] = item.get("secondary_color")
    item["pattern"] = item.get("pattern")
    item["season"] = item.get("season")
    item["occasion"] = item.get("occasion")
    item["brand"] = item.get("brand")
    item["image_url"] = item.get("image_url", "") or ""
    item["image_path"] = item.get("image_path", "") or ""
    item["original_image_url"] = item.get("original_image_url", "") or ""
    item["background_removed"] = bool(item.get("background_removed", False))
    item["tags"] = item.get("tags", []) or []

    if item.get("created_at") is not None:
        item["created_at"] = str(item["created_at"])
    if item.get("updated_at") is not None:
        item["updated_at"] = str(item["updated_at"])

    return item


@router.post("/add")
def add_item(request: AddItemRequest):
    try:
        item = {
            "id": str(uuid.uuid4()),
            "user_id": str(request.user_id),
            "name": request.name.strip(),
            "category": normalize_category(request.category),
            "subcategory": request.subcategory,
            "color": request.color or "unknown",
            "secondary_color": request.secondary_color,
            "pattern": request.pattern,
            "season": request.season,
            "occasion": request.occasion,
            "brand": request.brand,
            "image_url": request.image_url or "",
            "image_path": request.image_path or "",
            "original_image_url": request.original_image_url or "",
            "background_removed": request.background_removed,
            "tags": request.tags,
            "created_at": datetime.utcnow().isoformat(),
        }

        added_item = db.add_item(item)

        if not added_item:
            raise HTTPException(status_code=500, detail="Failed to add item")

        return {
            "success": True,
            "message": "Item added successfully",
            "data": normalize_item(added_item),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding item: {str(e)}")


@router.get("/all")
def get_all_items(user_id: str):
    try:
        items = db.get_user_items(str(user_id))
        normalized_items = [normalize_item(item) for item in items]

        return {
            "success": True,
            "message": "Items retrieved successfully",
            "data": normalized_items,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching items: {str(e)}")


@router.get("/{item_id}")
def get_item(item_id: str):
    try:
        item = db.get_item(item_id)

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        return {
            "success": True,
            "message": "Item retrieved successfully",
            "data": normalize_item(item),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching item: {str(e)}")


@router.put("/{item_id}")
def update_item(item_id: str, request: UpdateItemRequest):
    try:
        updates = {}

        if request.name is not None:
            updates["name"] = request.name.strip()
        if request.category is not None:
            updates["category"] = normalize_category(request.category)
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
        if request.image_path is not None:
            updates["image_path"] = request.image_path or ""
        if request.original_image_url is not None:
            updates["original_image_url"] = request.original_image_url or ""
        if request.background_removed is not None:
            updates["background_removed"] = request.background_removed
        if request.tags is not None:
            updates["tags"] = request.tags

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        updated = db.update_item(item_id, updates)

        if not updated:
            raise HTTPException(status_code=404, detail="Item not found or update failed")

        updated_item = db.get_item(item_id)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Updated item not found")

        return {
            "success": True,
            "message": "Item updated successfully",
            "data": normalize_item(updated_item),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")


@router.delete("/{item_id}")
def delete_item(item_id: str):
    try:
        deleted = db.delete_item(item_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Item not found")

        return {
            "success": True,
            "message": "Item deleted successfully",
            "data": {"id": item_id},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")
