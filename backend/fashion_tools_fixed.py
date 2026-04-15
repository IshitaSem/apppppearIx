from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from collections import defaultdict
from database import wardrobe_collection

router = APIRouter(prefix="/tools", tags=["Fashion Tools"])


class JudgeOutfitRequest(BaseModel):
    user_id: str
    occasion: str = "casual"
    style_preference: Optional[str] = None
    items: List[dict] = []


class JudgeOutfitResponse(BaseModel):
    score: int
    verdict: str
    strengths: List[str]
    issues: List[str]
    tips: List[str]


class OutfitGeneratorRequest(BaseModel):
    user_id: str
    occasion: str = "casual"


class VirtualTryOnRequest(BaseModel):
    user_id: str
    item_ids: List[str]


color_compatibility = {
    "black": ["white", "grey", "red", "blue", "green", "yellow"],
    "white": ["black", "navy", "red", "pink"],
    "grey": ["black", "white", "blue", "yellow"],
    "blue": ["white", "grey", "orange", "beige"],
    "red": ["black", "white", "grey", "navy"],
    "green": ["white", "beige", "brown"],
    "yellow": ["blue", "purple", "navy"],
    "brown": ["beige", "white", "blue"],
    "beige": ["blue", "brown", "black"],
    "pink": ["grey", "white", "navy"],
}


def filter_items_by_user(user_id: str) -> List[dict]:
    """Filter wardrobe items by user_id"""
    return [item for item in wardrobe_collection if item.get("user_id") == user_id]


def score_color_combination(items: List[dict]) -> int:
    if len(items) < 2:
        return 3
    
    colors = [item.get("color", "unknown").lower() for item in items if item.get("color")]
    score = 5  # base
    
    for i in range(len(colors) - 1):
        c1 = colors[i]
        c2 = colors[i + 1]
        if c1 in color_compatibility and c2 in color_compatibility[c1]:
            score += 2
        else:
            score -= 1
    
    return max(0, min(10, score))


def get_category_completeness(items: List[dict]) -> tuple[int, list]:
    categories = defaultdict(int)
    for item in items:
        cat = item.get("category", "unknown").lower()
        categories[cat] += 1
    
    completeness = 0
    issues = []
    
    has_top_bottom = categories["top"] + categories["dress"] > 0 and categories["bottom"] > 0
    has_shoes = categories["shoes"] > 0
    
    if not has_top_bottom:
        issues.append("Missing top or bottom")
        completeness -= 3
    if not has_shoes:
        issues.append("No shoes")
        completeness -= 1
    
    completeness += min(5, len(items))
    return max(0, min(10, completeness)), issues


def get_occasion_match(occasion: str, items: List[dict]) -> tuple[int, list]:
    score = 5
    matches = []
    issues = []
    
    occasion_lower = occasion.lower()
    
    occasion_scores = {
        "casual": {"casual": 10, "streetwear": 8, "sporty": 7},
        "college": {"casual": 9, "minimal": 8, "streetwear": 7},
        "formal": {"formal": 10, "business": 9, "elegant": 8},
        "party": {"party": 10, "trendy": 8, "bold": 8},
    }
    
    for item in items:
        tags = [t.lower() for t in item.get("tags", [])]
        item_occasion = item.get("occasion", "").lower()
        
        for tag in tags:
            if occasion_lower in occasion_scores and tag in occasion_scores[occasion_lower]:
                score += 2
                matches.append(f"{item['name']} matches {occasion}")
                break
        
        if item_occasion and occasion_lower not in item_occasion:
            issues.append(f"{item['name']} not ideal for {occasion}")
            score -= 1
    
    return max(0, min(10, score)), matches + issues


@router.post("/judge-outfit")
def judge_outfit(request: JudgeOutfitRequest) -> dict:
    if not request.items:
        raise HTTPException(status_code=400, detail="No items provided")

    # Validate items belong to user
    user_items = filter_items_by_user(request.user_id)
    item_ids = [item["id"] for item in user_items]
    provided_ids = [item.get("id") for item in request.items if item.get("id")]
    
    invalid_items = [iid for iid in provided_ids if iid not in item_ids]
    if invalid_items:
        raise HTTPException(status_code=403, detail=f"Invalid items: {invalid_items}")

    # Score calculations
    color_score = score_color_combination(request.items)
    completeness_score, completeness_issues = get_category_completeness(request.items)
    match_score, match_list = get_occasion_match(request.occasion, request.items)

    # Overall score
    total_score = round((color_score + completeness_score + match_score) / 3)

    # Verdict
    if total_score >= 8:
        verdict = "Perfect Match! 👌"
    elif total_score >= 6:
        verdict = "Good Choice 👍"
    elif total_score >= 4:
        verdict = "Okay 👀"
    else:
        verdict = "Needs Work 😿"

    # Generate feedback
    strengths = ["Base combination works"]
    if color_score >= 7:
        strengths.append("Colors are compatible")
    if completeness_score >= 7:
        strengths.append("Complete outfit")
    
    issues = completeness_issues
    if color_score < 4:
        issues.append("Colors clash")
    
    tips = []
    if "shoes" not in [item.get("category", "").lower() for item in request.items]:
        tips.append("Add shoes to complete the look")
    if len(request.items) < 3:
        tips.append("Consider adding accessories")
    if request.style_preference and request.style_preference not in [item.get("style", "") for item in request.items]:
        tips.append(f"Add more {request.style_preference} items")

    return {
        "success": True,
        "message": "Outfit judged successfully",
        "data": {
            "score": total_score,
            "verdict": verdict,
            "strengths": strengths,
            "issues": issues,
            "tips": tips,
            "breakdown": {
                "color": color_score,
                "completeness": completeness_score,
                "occasion_match": match_score,
            }
        },
        "error": None
    }


@router.post("/outfit-generator")
def outfit_generator(request: OutfitGeneratorRequest):
    """Generate outfit from wardrobe"""
    items = filter_items_by_user(request.user_id)
    grouped = defaultdict(list)
    for item in items:
        cat = item.get("category", "unknown").lower()
        grouped[cat].append(item)
    
    occasion = request.occasion.lower()
    
    outfit = {}
    
    # Occasion logic
    if occasion in ["casual", "college"]:
        top = grouped["tops"][0] if grouped["tops"] else None
        bottom = grouped["bottoms"][0] if grouped["bottoms"] else None
        outfit = {"top": top, "bottom": bottom}
    elif occasion == "formal":
        tops = [t for t in grouped["tops"] if "shirt" in t["name"].lower()]
        bottoms = [b for b in grouped["bottoms"] if "trouser" in b["name"].lower()]
        outfit = {"top": tops[0] if tops else grouped["tops"][0] if grouped["tops"] else None, "bottom": bottoms[0] if bottoms else grouped["bottoms"][0] if grouped["bottoms"] else None}
    elif occasion == "party":
        dress = grouped["dresses"][0] if grouped["dresses"] else None
        outfit = {"dress": dress} if dress else {"top": grouped["tops"][0] if grouped["tops"] else None, "bottom": grouped["bottoms"][0] if grouped["bottoms"] else None}
    
    if "shoes" in grouped and grouped["shoes"]:
        outfit["shoes"] = grouped["shoes"][0]
    
    return {
        "success": True,
        "message": "Outfit generated",
        "data": outfit
    }


@router.post("/virtual-try-on")
def virtual_try_on(request: VirtualTryOnRequest):
    return {
        "success": True,
        "message": "Virtual try-on ready for integration",
        "data": {"status": "placeholder"}
    }


@router.get("/trend-analyzer/{user_id}")
def trend_analyzer(user_id: str):
    items = filter_items_by_user(user_id)
    return {
        "success": True,
        "message": "Trend analysis ready",
        "data": {"items_count": len(items), "status": "placeholder"}
    }
