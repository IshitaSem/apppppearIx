from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from database import db

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])


CATEGORY_MAP = {
    # TOP
    "top": "top",
    "tops": "top",
    "shirt": "top",
    "shirts": "top",
    "tshirt": "top",
    "t-shirts": "top",
    "t-shirt": "top",
    "tee": "top",
    "blouse": "top",
    "crop top": "top",

    # BOTTOM
    "bottom": "bottom",
    "bottoms": "bottom",
    "jean": "bottom",
    "jeans": "bottom",
    "pant": "bottom",
    "pants": "bottom",
    "trouser": "bottom",
    "trousers": "bottom",
    "skirt": "bottom",
    "skirts": "bottom",
    "shorts": "bottom",
    "legging": "bottom",
    "leggings": "bottom",

    # DRESS
    "dress": "dress",
    "dresses": "dress",
    "gown": "dress",

    # SHOES
    "shoe": "shoes",
    "shoes": "shoes",
    "sneaker": "shoes",
    "sneakers": "shoes",
    "heel": "shoes",
    "heels": "shoes",
    "boot": "shoes",
    "boots": "shoes",
    "sandal": "shoes",
    "sandals": "shoes",
    "loafer": "shoes",
    "loafers": "shoes",
    "flat": "shoes",
    "flats": "shoes",

    # ACCESSORIES
    "accessory": "accessories",
    "accessories": "accessories",
    "bag": "accessories",
    "bags": "accessories",
    "belt": "accessories",
    "belts": "accessories",
    "watch": "accessories",
    "watches": "accessories",
    "jewelry": "accessories",
    "jewellery": "accessories",
    "necklace": "accessories",
    "necklaces": "accessories",
    "bracelet": "accessories",
    "bracelets": "accessories",
    "ring": "accessories",
    "rings": "accessories",
    "earring": "accessories",
    "earrings": "accessories",
    "scarf": "accessories",
    "scarves": "accessories",
    "cap": "accessories",
    "caps": "accessories",
    "hat": "accessories",
    "hats": "accessories",

    # OUTERWEAR
    "outerwear": "outerwear",
    "jacket": "outerwear",
    "jackets": "outerwear",
    "coat": "outerwear",
    "coats": "outerwear",
    "hoodie": "outerwear",
    "hoodies": "outerwear",
    "sweater": "outerwear",
    "sweaters": "outerwear",
    "blazer": "outerwear",
    "blazers": "outerwear",
    "cardigan": "outerwear",
    "cardigans": "outerwear",
    "shrug": "outerwear",
    "shrugs": "outerwear",
}


def normalize_category(category: str) -> str:
    if not category:
        return "other"

    c = category.strip().lower()
    return CATEGORY_MAP.get(c, c)


def normalize_item(item: dict) -> dict:
    item["category"] = normalize_category(item.get("category", ""))
    return item


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
    tags: List[str] = []


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
    item = {
        "id": str(uuid.uuid4()),
        "user_id": request.user_id,
        "name": request.name,
        "category": normalize_category(request.category),
        "subcategory": request.subcategory,
        "color": request.color,
        "secondary_color": request.secondary_color,
        "pattern": request.pattern,
        "season": request.season,
        "occasion": request.occasion,
        "brand": request.brand,
        "image_url": request.image_url,
        "tags": request.tags,
        "created_at": datetime.utcnow(),
    }

    saved_item = db.add_item(item)
    if not saved_item:
        raise HTTPException(status_code=500, detail="Failed to add item")

    saved_item = normalize_item(saved_item)

    return {
        "message": "Item added successfully",
        "item": saved_item,
    }


# Supports frontend call: /wardrobe/all?user_id=...
@router.get("/all")
def get_all_items_query(user_id: str = Query(...)):
    items = db.get_user_items(user_id)
    items = [normalize_item(item) for item in items]

    return {
        "count": len(items),
        "items": items,
    }


# Supports old style call: /wardrobe/all/{user_id}
@router.get("/all/{user_id}")
def get_all_items_path(user_id: str):
    items = db.get_user_items(user_id)
    items = [normalize_item(item) for item in items]

    return {
        "count": len(items),
        "items": items,
    }


# Supports frontend call: /wardrobe/category?user_id=...&category=...
@router.get("/category")
def get_items_by_category_query(
    user_id: str = Query(...),
    category: str = Query(...)
):
    normalized_category = normalize_category(category)
    items = db.get_user_items(user_id)

    filtered_items = []
    for item in items:
        item = normalize_item(item)
        if item["category"] == normalized_category:
            filtered_items.append(item)

    return {
        "category": normalized_category,
        "count": len(filtered_items),
        "items": filtered_items,
    }


# Supports old style call: /wardrobe/category/{user_id}/{category}
@router.get("/category/{user_id}/{category}")
def get_items_by_category_path(user_id: str, category: str):
    normalized_category = normalize_category(category)
    items = db.get_user_items(user_id)

    filtered_items = []
    for item in items:
        item = normalize_item(item)
        if item["category"] == normalized_category:
            filtered_items.append(item)

    return {
        "category": normalized_category,
        "count": len(filtered_items),
        "items": filtered_items,
    }


@router.get("/item/{item_id}")
def get_item(item_id: str):
    item = db.get_item(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return normalize_item(item)


@router.put("/update/{item_id}")
def update_item(item_id: str, request: UpdateItemRequest):
    existing_item = db.get_item(item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = {}

    if request.name is not None:
        updates["name"] = request.name
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
        updates["image_url"] = request.image_url
    if request.tags is not None:
        updates["tags"] = request.tags

    if not updates:
        updated_item = db.get_item(item_id)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Item not found")

        return {
            "message": "No changes provided",
            "item": normalize_item(updated_item),
        }

    success = db.update_item(item_id, updates)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update item")

    updated_item = db.get_item(item_id)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Updated item not found")

    return {
        "message": "Item updated successfully",
        "item": normalize_item(updated_item),
    }


@router.delete("/delete/{item_id}")
def delete_item(item_id: str):
    existing_item = db.get_item(item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")

    success = db.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete item")

    return {
        "message": "Item deleted successfully",
        "item": normalize_item(existing_item),
    }
