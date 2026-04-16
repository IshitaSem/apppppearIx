from fastapi import APIRouter, HTTPException
from database import wardrobe_items
from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional, List

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])


def normalize_category(category: str) -> str:
    if not category:
        return "other"

    c = category.strip().lower()

    mapping = {
        "top": "top",
        "tops": "top",
        "shirt": "top",
        "tshirt": "top",
        "t-shirt": "top",
        "tee": "top",
        "blouse": "top",

        "bottom": "bottom",
        "bottoms": "bottom",
        "jeans": "bottom",
        "pants": "bottom",
        "trouser": "bottom",
        "trousers": "bottom",
        "skirt": "bottom",
        "shorts": "bottom",

        "dress": "dress",
        "dresses": "dress",

        "shoe": "shoes",
        "shoes": "shoes",
        "sneaker": "shoes",
        "sneakers": "shoes",
        "heel": "shoes",
        "heels": "shoes",
        "sandal": "shoes",
        "sandals": "shoes",
        "boot": "shoes",
        "boots": "shoes",

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
    }

    return mapping.get(c, c)


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
        "created_at": datetime.utcnow().isoformat(),
    }

    wardrobe_items.append(item)
    return {"message": "Item added successfully", "item": item}


@router.get("/all/{user_id}")
def get_all_items(user_id: str):
    items = [item for item in wardrobe_items if item["user_id"] == user_id]
    return {
        "count": len(items),
        "items": items,
    }


@router.get("/category/{user_id}/{category}")
def get_items_by_category(user_id: str, category: str):
    normalized = normalize_category(category)

    filtered_items = [
        item for item in wardrobe_items
        if item["user_id"] == user_id and normalize_category(item.get("category", "")) == normalized
    ]

    return {
        "category": normalized,
        "count": len(filtered_items),
        "items": filtered_items,
    }


@router.get("/item/{item_id}")
def get_item(item_id: str):
    for item in wardrobe_items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/update/{item_id}")
def update_item(item_id: str, request: UpdateItemRequest):
    for item in wardrobe_items:
        if item["id"] == item_id:
            if request.name is not None:
                item["name"] = request.name
            if request.category is not None:
                item["category"] = normalize_category(request.category)
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

            return {"message": "Item updated successfully", "item": item}

    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/delete/{item_id}")
def delete_item(item_id: str):
    for index, item in enumerate(wardrobe_items):
        if item["id"] == item_id:
            deleted_item = wardrobe_items.pop(index)
            return {"message": "Item deleted successfully", "item": deleted_item}

    raise HTTPException(status_code=404, detail="Item not found")
