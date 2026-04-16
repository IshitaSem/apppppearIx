from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import os

from database import db

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])


CATEGORY_MAP = {
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

    "dress": "dress",
    "dresses": "dress",
    "gown": "dress",

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


def get_public_base_url(request: Request) -> str:
    env_url = os.getenv("BACKEND_PUBLIC_BASE_URL", "").strip()
    if env_url:
        return env_url.rstrip("/")
    return str(request.base_url).rstrip("/")


def build_clean_image_url(request: Request, item: dict) -> str:
    base_url = get_public_base_url(request)

    image_path = str(item.get("image_path", "")).strip()
    image_url_relative = str(item.get("image_url_relative", "")).strip()
    image_url = str(item.get("image_url", "")).strip()

    # 1. Best source: image_path
    if image_path:
        filename = os.path.basename(image_path)
        return f"{base_url}/uploads/{filename}"

    # 2. Next best: relative upload path
    if image_url_relative:
        if not image_url_relative.startswith("/"):
            image_url_relative = f"/{image_url_relative}"
        if "/uploads/" in image_url_relative:
            idx = image_url_relative.index("/uploads/")
            return f"{base_url}{image_url_relative[idx:]}"

    # 3. Try salvaging stored image_url
    if image_url:
        if "/uploads/" in image_url:
            idx = image_url.index("/uploads/")
            upload_part = image_url[idx:]
            return f"{base_url}{upload_part}"

    return ""


def normalize_item(item: dict, request: Optional[Request] = None) -> dict:
    normalized = dict(item)
    normalized["category"] = normalize_category(normalized.get("category", ""))

    if request:
        clean_image_url = build_clean_image_url(request, normalized)
        normalized["image_url"] = clean_image_url

        if clean_image_url and "/uploads/" in clean_image_url:
            normalized["image_url_relative"] = clean_image_url.replace(
                get_public_base_url(request), ""
            )

        original_image_url = str(normalized.get("original_image_url", "")).strip()
        if original_image_url and "/uploads/" in original_image_url:
            idx = original_image_url.index("/uploads/")
            normalized["original_image_url"] = (
                f"{get_public_base_url(request)}{original_image_url[idx:]}"
            )

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
        item = normalize_item(item, request)
        if item["category"] == normalized_category:
            filtered_items.append(item)

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
        item = normalize_item(item, request)
        if item["category"] == normalized_category:
            filtered_items.append(item)

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
def update_item(item_id: str, request_body: UpdateItemRequest, request: Request):
    existing_item = db.get_item(item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = {}

    if request_body.name is not None:
        updates["name"] = request_body.name
    if request_body.category is not None:
        updates["category"] = normalize_category(request_body.category)
    if request_body.subcategory is not None:
        updates["subcategory"] = request_body.subcategory
    if request_body.color is not None:
        updates["color"] = request_body.color
    if request_body.secondary_color is not None:
        updates["secondary_color"] = request_body.secondary_color
    if request_body.pattern is not None:
        updates["pattern"] = request_body.pattern
    if request_body.season is not None:
        updates["season"] = request_body.season
    if request_body.occasion is not None:
        updates["occasion"] = request_body.occasion
    if request_body.brand is not None:
        updates["brand"] = request_body.brand
    if request_body.image_url is not None:
        updates["image_url"] = request_body.image_url
    if request_body.tags is not None:
        updates["tags"] = request_body.tags

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
