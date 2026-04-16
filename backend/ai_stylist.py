from fastapi import APIRouter, HTTPException, Request
from database import db
import os

router = APIRouter(prefix="/ai", tags=["AI Stylist"])


CATEGORY_MAP = {
    "top": "top",
    "tops": "top",
    "shirt": "top",
    "shirts": "top",
    "tshirt": "top",
    "t-shirt": "top",
    "t-shirts": "top",
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
    c = str(category).strip().lower()
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

    if image_path:
        filename = os.path.basename(image_path)
        return f"{base_url}/uploads/{filename}"

    if image_url_relative:
        if not image_url_relative.startswith("/"):
            image_url_relative = f"/{image_url_relative}"
        if "/uploads/" in image_url_relative:
            idx = image_url_relative.index("/uploads/")
            return f"{base_url}{image_url_relative[idx:]}"

    if image_url:
        if image_url.startswith("http://") or image_url.startswith("https://"):
            return image_url
        if "/uploads/" in image_url:
            idx = image_url.index("/uploads/")
            return f"{base_url}{image_url[idx:]}"

    return ""


def serialize_item(request: Request, item: dict) -> dict:
    if not item:
        return {}

    return {
        "id": str(item.get("id", "")),
        "user_id": str(item.get("user_id", "")),
        "name": item.get("name", ""),
        "category": normalize_category(item.get("category", "")),
        "subcategory": item.get("subcategory"),
        "color": item.get("color", "unknown"),
        "secondary_color": item.get("secondary_color"),
        "pattern": item.get("pattern"),
        "season": item.get("season"),
        "occasion": item.get("occasion"),
        "brand": item.get("brand"),
        "image_path": str(item.get("image_path", "")).strip(),
        "image_url": build_clean_image_url(request, item),
        "tags": item.get("tags", []),
        "created_at": str(item.get("created_at", "")),
    }


def categorize_items(items: list[dict]) -> dict:
    grouped = {
        "top": [],
        "bottom": [],
        "dress": [],
        "shoes": [],
        "accessories": [],
        "outerwear": [],
        "other": [],
    }

    for item in items:
        category = normalize_category(item.get("category", ""))
        if category in grouped:
            grouped[category].append(item)
        else:
            grouped["other"].append(item)

    return grouped


@router.get("/generate-outfit")
def generate_outfit(request: Request, user_id: str, occasion: str):
    items = db.get_user_items(user_id)

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No wardrobe items found for this user"
        )

    grouped = categorize_items(items)

    tops = grouped["top"]
    bottoms = grouped["bottom"]
    dresses = grouped["dress"]
    shoes = grouped["shoes"]
    accessories = grouped["accessories"]
    outerwear = grouped["outerwear"]

    occasion_lower = occasion.strip().lower()

    outfit_items = []
    notes = []

    # Primary outfit choice
    if occasion_lower in ["casual", "casual day", "college", "daily", "everyday"]:
        if tops and bottoms:
            outfit_items.append(serialize_item(request, tops[0]))
            outfit_items.append(serialize_item(request, bottoms[0]))
            notes.append("Picked a casual top and bottom combination.")
        elif dresses:
            outfit_items.append(serialize_item(request, dresses[0]))
            notes.append("Picked an easy casual dress option.")
        elif tops:
            outfit_items.append(serialize_item(request, tops[0]))
            notes.append("Picked a casual top from available wardrobe items.")
        elif bottoms:
            outfit_items.append(serialize_item(request, bottoms[0]))
            notes.append("Picked a casual bottom from available wardrobe items.")
        else:
            raise HTTPException(
                status_code=400,
                detail="No suitable casual clothing items found in wardrobe"
            )

    elif occasion_lower in ["formal", "office", "interview"]:
        if dresses:
            outfit_items.append(serialize_item(request, dresses[0]))
            notes.append("Picked a dress suitable for a formal occasion.")
        elif tops and bottoms:
            outfit_items.append(serialize_item(request, tops[0]))
            outfit_items.append(serialize_item(request, bottoms[0]))
            notes.append("Picked a polished top and bottom combination.")
        elif tops:
            outfit_items.append(serialize_item(request, tops[0]))
            notes.append("Picked a formal top from available wardrobe items.")
        else:
            raise HTTPException(
                status_code=400,
                detail="No suitable formal clothing items found in wardrobe"
            )

    elif occasion_lower in ["party", "evening", "special occasion"]:
        if dresses:
            outfit_items.append(serialize_item(request, dresses[0]))
            notes.append("Picked a dress suitable for a party look.")
        elif tops and bottoms:
            outfit_items.append(serialize_item(request, tops[0]))
            outfit_items.append(serialize_item(request, bottoms[0]))
            notes.append("Picked a stylish top and bottom combination.")
        elif tops:
            outfit_items.append(serialize_item(request, tops[0]))
            notes.append("Picked a standout top from available wardrobe items.")
        else:
            raise HTTPException(
                status_code=400,
                detail="No suitable party clothing items found in wardrobe"
            )

    else:
        if tops and bottoms:
            outfit_items.append(serialize_item(request, tops[0]))
            outfit_items.append(serialize_item(request, bottoms[0]))
            notes.append("Picked a balanced outfit from available wardrobe items.")
        elif dresses:
            outfit_items.append(serialize_item(request, dresses[0]))
            notes.append("Picked a dress from available wardrobe items.")
        elif tops:
            outfit_items.append(serialize_item(request, tops[0]))
            notes.append("Picked a top from available wardrobe items.")
        elif bottoms:
            outfit_items.append(serialize_item(request, bottoms[0]))
            notes.append("Picked a bottom from available wardrobe items.")
        else:
            raise HTTPException(
                status_code=400,
                detail="No suitable clothing items found in wardrobe"
            )

    # Optional add-ons
    if outerwear:
        if occasion_lower in ["formal", "office", "interview", "party", "evening", "special occasion"]:
            outfit_items.append(serialize_item(request, outerwear[0]))
            notes.append("Added outerwear for styling.")

    if shoes:
        outfit_items.append(serialize_item(request, shoes[0]))
        notes.append("Added shoes to complete the look.")

    if accessories:
        outfit_items.append(serialize_item(request, accessories[0]))
        notes.append("Added an accessory for styling.")

    if not outfit_items:
        raise HTTPException(
            status_code=400,
            detail="Could not build an outfit from available items"
        )

    return {
        "success": True,
        "occasion": occasion,
        "user_id": user_id,
        "items": outfit_items,
        "notes": notes,
    }
