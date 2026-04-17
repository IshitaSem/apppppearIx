from fastapi import APIRouter, HTTPException
from database import wardrobe_items
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import random

router = APIRouter(prefix="/ai", tags=["AI Stylist"])


class GenerateOutfitRequest(BaseModel):
    user_id: str
    occasion: str
    season: Optional[str] = None


def normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def get_item_category(item: Dict[str, Any]) -> str:
    return normalize_text(item.get("category"))


def get_item_subcategory(item: Dict[str, Any]) -> str:
    return normalize_text(item.get("subcategory"))


def get_item_name(item: Dict[str, Any]) -> str:
    return normalize_text(item.get("name"))


def matches_any(text: str, words: List[str]) -> bool:
    return any(word in text for word in words)


def is_top(item: Dict[str, Any]) -> bool:
    category = get_item_category(item)
    subcategory = get_item_subcategory(item)
    name = get_item_name(item)

    return (
        category in ["top", "tops", "shirt", "tshirt", "t-shirt", "blouse"]
        or matches_any(subcategory, ["top", "shirt", "tshirt", "t-shirt", "blouse", "kurti"])
        or matches_any(name, ["top", "shirt", "tshirt", "t-shirt", "blouse", "kurti"])
    )


def is_bottom(item: Dict[str, Any]) -> bool:
    category = get_item_category(item)
    subcategory = get_item_subcategory(item)
    name = get_item_name(item)

    return (
        category in ["bottom", "bottoms", "jeans", "trousers", "pants", "skirt"]
        or matches_any(subcategory, ["bottom", "jeans", "trouser", "pants", "skirt", "palazzo"])
        or matches_any(name, ["jeans", "trouser", "pants", "skirt", "palazzo"])
    )


def is_dress(item: Dict[str, Any]) -> bool:
    category = get_item_category(item)
    subcategory = get_item_subcategory(item)
    name = get_item_name(item)

    return (
        category in ["dress", "dresses", "gown"]
        or matches_any(subcategory, ["dress", "gown", "one piece", "one-piece"])
        or matches_any(name, ["dress", "gown", "one piece", "one-piece"])
    )


def is_shoes(item: Dict[str, Any]) -> bool:
    category = get_item_category(item)
    subcategory = get_item_subcategory(item)
    name = get_item_name(item)

    return (
        category in ["shoes", "shoe", "footwear", "sneakers", "heels"]
        or matches_any(subcategory, ["shoe", "footwear", "sneaker", "heel", "loafer", "boots", "sandals"])
        or matches_any(name, ["shoe", "footwear", "sneaker", "heel", "loafer", "boots", "sandals"])
    )


def is_accessory(item: Dict[str, Any]) -> bool:
    category = get_item_category(item)
    subcategory = get_item_subcategory(item)
    name = get_item_name(item)

    return (
        category in ["accessories", "accessory", "jewelry", "bag"]
        or matches_any(subcategory, ["accessory", "jewelry", "bag", "watch", "belt", "scarf"])
        or matches_any(name, ["bag", "watch", "belt", "scarf", "earring", "necklace", "bracelet"])
    )


def is_outerwear(item: Dict[str, Any]) -> bool:
    category = get_item_category(item)
    subcategory = get_item_subcategory(item)
    name = get_item_name(item)

    return (
        category in ["outerwear", "outer layer", "jacket", "coat", "blazer", "hoodie", "cardigan", "sweater"]
        or matches_any(subcategory, ["outerwear", "jacket", "coat", "blazer", "hoodie", "cardigan", "sweater"])
        or matches_any(name, ["jacket", "coat", "blazer", "hoodie", "cardigan", "sweater", "shrug"])
    )


def pick_best_outer_layer(outerwear_items: List[Dict[str, Any]], occasion: str, season: str) -> Optional[Dict[str, Any]]:
    if not outerwear_items:
        return None

    occasion = normalize_text(occasion)
    season = normalize_text(season)

    formal_words = ["formal", "office", "interview", "party"]
    casual_words = ["casual", "college", "daily", "day out", "outing"]
    winter_words = ["winter", "cold"]

    if occasion in formal_words:
        blazers = [
            item for item in outerwear_items
            if matches_any(
                f"{get_item_category(item)} {get_item_subcategory(item)} {get_item_name(item)}",
                ["blazer", "coat"]
            )
        ]
        if blazers:
            return random.choice(blazers)

    if occasion in casual_words:
        casual_outer = [
            item for item in outerwear_items
            if matches_any(
                f"{get_item_category(item)} {get_item_subcategory(item)} {get_item_name(item)}",
                ["jacket", "hoodie", "cardigan", "shrug", "sweater"]
            )
        ]
        if casual_outer:
            return random.choice(casual_outer)

    if season in winter_words:
        winter_outer = [
            item for item in outerwear_items
            if matches_any(
                f"{get_item_category(item)} {get_item_subcategory(item)} {get_item_name(item)}",
                ["coat", "jacket", "hoodie", "cardigan", "sweater", "blazer"]
            )
        ]
        if winter_outer:
            return random.choice(winter_outer)

    return random.choice(outerwear_items)


def pick_matching_shoes(shoes: List[Dict[str, Any]], occasion: str) -> Optional[Dict[str, Any]]:
    if not shoes:
        return None

    occasion = normalize_text(occasion)

    formal_shoes = [
        item for item in shoes
        if matches_any(
            f"{get_item_category(item)} {get_item_subcategory(item)} {get_item_name(item)}",
            ["heels", "heel", "loafer", "formal", "boots"]
        )
    ]

    casual_shoes = [
        item for item in shoes
        if matches_any(
            f"{get_item_category(item)} {get_item_subcategory(item)} {get_item_name(item)}",
            ["sneaker", "sandals", "casual", "shoe"]
        )
    ]

    if occasion in ["formal", "office", "interview", "party"] and formal_shoes:
        return random.choice(formal_shoes)

    if occasion in ["casual", "college", "daily", "outing"] and casual_shoes:
        return random.choice(casual_shoes)

    return random.choice(shoes)


def pick_accessories(accessories: List[Dict[str, Any]], limit: int = 2) -> List[Dict[str, Any]]:
    if not accessories:
        return []
    random.shuffle(accessories)
    return accessories[:limit]


@router.get("/generate-outfit")
def generate_outfit(user_id: str, occasion: str, season: Optional[str] = None):
    user_id = normalize_text(user_id)
    occasion = normalize_text(occasion)
    season = normalize_text(season)

    items = [
        item for item in wardrobe_items
        if normalize_text(item.get("user_id")) == user_id
    ]

    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items found for this user")

    tops = [item for item in items if is_top(item)]
    bottoms = [item for item in items if is_bottom(item)]
    dresses = [item for item in items if is_dress(item)]
    shoes = [item for item in items if is_shoes(item)]
    accessories = [item for item in items if is_accessory(item)]
    outerwear = [item for item in items if is_outerwear(item)]

    outfit = {
        "top": None,
        "bottom": None,
        "dress": None,
        "outer_layer": None,
        "shoes": None,
        "accessories": [],
        "notes": []
    }

    # Main outfit selection
    if occasion in ["casual", "college", "daily", "outing"]:
        if tops and bottoms:
            outfit["top"] = random.choice(tops)
            outfit["bottom"] = random.choice(bottoms)
            outfit["notes"].append("Selected a casual main outfit using a top and bottom.")
        elif dresses:
            outfit["dress"] = random.choice(dresses)
            outfit["notes"].append("Selected a casual dress because separate top/bottom was not available.")
        else:
            raise HTTPException(status_code=400, detail="Not enough wardrobe items to create a casual outfit")

    elif occasion in ["formal", "office", "interview", "party"]:
        if dresses:
            outfit["dress"] = random.choice(dresses)
            outfit["notes"].append("Selected a dress for a more polished formal look.")
        elif tops and bottoms:
            outfit["top"] = random.choice(tops)
            outfit["bottom"] = random.choice(bottoms)
            outfit["notes"].append("Selected a formal-style top and bottom combination.")
        else:
            raise HTTPException(status_code=400, detail="Not enough wardrobe items to create a formal outfit")

    else:
        if tops and bottoms:
            outfit["top"] = random.choice(tops)
            outfit["bottom"] = random.choice(bottoms)
            outfit["notes"].append("Selected a general outfit using available top and bottom.")
        elif dresses:
            outfit["dress"] = random.choice(dresses)
            outfit["notes"].append("Selected a general dress outfit.")
        else:
            raise HTTPException(status_code=400, detail="Not enough wardrobe items to create an outfit")

    # Outer layer logic
    should_add_outer_layer = False

    if season in ["winter", "cold"]:
        should_add_outer_layer = True
        outfit["notes"].append("Outer layer added because season is winter/cold.")

    if occasion in ["formal", "office", "interview", "party", "college"]:
        should_add_outer_layer = True
        outfit["notes"].append("Outer layer considered based on occasion styling.")

    if should_add_outer_layer and outerwear:
        outfit["outer_layer"] = pick_best_outer_layer(outerwear, occasion, season)
        outfit["notes"].append("Selected a matching outer layer from wardrobe.")
    else:
        outfit["notes"].append("No outer layer added.")

    # Shoes
    outfit["shoes"] = pick_matching_shoes(shoes, occasion)
    if outfit["shoes"]:
        outfit["notes"].append("Matching shoes added to complete the look.")

    # Accessories
    outfit["accessories"] = pick_accessories(accessories, limit=2)
    if outfit["accessories"]:
        outfit["notes"].append("Accessories added to enhance the outfit.")

    return {
        "success": True,
        "user_id": user_id,
        "occasion": occasion,
        "season": season if season else "not provided",
        "outfit": outfit
    }
