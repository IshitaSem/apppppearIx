from fastapi import APIRouter, HTTPException, Query, Request
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


def build_absolute_url(request: Request, relative_path: str) -> str:
    if not relative_path:
        return ""
    if relative_path.startswith("http://") or relative_path.startswith("https://"):
        return relative_path
    return str(request.base_url).rstrip("/") + relative_path


def normalize_item(item: dict, request: Optional[Request] = None) -> dict:
    normalized = dict(item)
    normalized["category"] = normalize_category(normalized.get("category", ""))

    image_url = normalized.get("image_url")
    original_image_url = normalized.get("original_image_url")

    if request and image_url:
        normalized["image_url"] = build_absolute_url(request, image_url)

    if request and original_image_url:
        normalized["original_image_url"] = build_absolute_url(request, original_image_url)

    return normalized


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
def add_item(request: Request, payload: AddItemRequest):
    item = {
        "id": str(uuid.uuid4()),
        "user_id": payload.user_id,
        "name": payload.name,
        "category": normalize_category(payload.category),
        "subcategory": payload.subcategory,
        "color": payload.color,
        "secondary_color": payload.secondary_color,
        "pattern": payload.pattern,
        "season": payload.season,
        "occasion": payload.occasion,
        "brand": payload.brand,
        "image_url": payload.image_url,
        "tags": payload.tags,
        "created_at": datetime.utcnow().isoformat(),
    }

    saved_item = db.add_item(item)
    if not saved_item:
        raise HTTPException(status_code=500, detail="Failed to add item")

    return {
        "message": "Item added successfully",
        "item": normalize_item(saved_item, request),
    }


@router.get("/all")
def get_all_items_query(request: Request, user_id: str = Query(...)):
    items = db.get_user_items(user_id)
    items = [normalize_item(item, request) for item in items]

    return {
        "count": len(items),
        "items": items,
    }


@router.get("/all/{user_id}")
def get_all_items_path(request: Request, user_id: str):
    items = db.get_user_items(user_id)
    items = [normalize_item(item, request) for item in items]

    return {
        "count": len(items),
        "items": items,
    }


@router.get("/category")
def get_items_by_category_query(
    request: Request,
    user_id: str = Query(...),
    category: str = Query(...)
):
    normalized_category = normalize_category(category)
    items = db.get_user_items(user_id)

    filtered_items = []
    for item in items:
        normalized_item = normalize_item(item, request)
        if normalized_item["category"] == normalized_category:
            filtered_items.append(normalized_item)

    return {
        "category": normalized_category,
        "count": len(filtered_items),
        "items": filtered_items,
    }


@router.get("/category/{user_id}/{category}")
def get_items_by_category_path(request: Request, user_id: str, category: str):
    normalized_category = normalize_category(category)
    items = db.get_user_items(user_id)

    filtered_items = []
    for item in items:
        normalized_item = normalize_item(item, request)
        if normalized_item["category"] == normalized_category:
            filtered_items.append(normalized_item)

    return {
        "category": normalized_category,
        "count": len(filtered_items),
        "items": filtered_items,
    }


@router.get("/item/{item_id}")
def get_item(request: Request, item_id: str):
    item = db.get_item(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return normalize_item(item, request)


@router.put("/update/{item_id}")
def update_item(request: Request, item_id: str, payload: UpdateItemRequest):
    existing_item = db.get_item(item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = {}

    if payload.name is not None:
        updates["name"] = payload.name
    if payload.category is not None:
        updates["category"] = normalize_category(payload.category)
    if payload.subcategory is not None:
        updates["subcategory"] = payload.subcategory
    if payload.color is not None:
        updates["color"] = payload.color
    if payload.secondary_color is not None:
        updates["secondary_color"] = payload.secondary_color
    if payload.pattern is not None:
        updates["pattern"] = payload.pattern
    if payload.season is not None:
        updates["season"] = payload.season
    if payload.occasion is not None:
        updates["occasion"] = payload.occasion
    if payload.brand is not None:
        updates["brand"] = payload.brand
    if payload.image_url is not None:
        updates["image_url"] = payload.image_url
    if payload.tags is not None:
        updates["tags"] = payload.tags

    if not updates:
        updated_item = db.get_item(item_id)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Item not found")

        return {
            "message": "No changes provided",
            "item": normalize_item(updated_item, request),
        }

    success = db.update_item(item_id, updates)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update item")

    updated_item = db.get_item(item_id)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Updated item not found")

    return {
        "message": "Item updated successfully",
        "item": normalize_item(updated_item, request),
    }


@router.delete("/delete/{item_id}")
def delete_item(request: Request, item_id: str):
    existing_item = db.get_item(item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")

    success = db.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete item")

    return {
        "message": "Item deleted successfully",
        "item": normalize_item(existing_item, request),
    }
