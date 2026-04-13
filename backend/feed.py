from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from database import feed, users
from pydantic import BaseModel
import uuid
import os
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads"
UPLOAD_URL_PREFIX = "/uploads"

router = APIRouter(prefix="/feed", tags=["Global Feed"])

class LikeRequest(BaseModel):
    user_id: str

class PostResponse(BaseModel):
    id: str
    user_id: str
    username: str
    caption: str
    image_url: str
    created_at: str
    likes_count: int
    dislikes_count: int
    likes_by: list[str]
    dislikes_by: list[str]

@router.post("/posts")
async def create_post(
    user_id: str = Form(...),
    caption: str = Form(...),
    image: UploadFile = File(...)
):
    if not image.filename:
        raise HTTPException(status_code=400, detail="No image provided")

    allowed_ext = {"jpg", "jpeg", "png", "webp", "gif"}
    file_ext = image.filename.split(".")[-1].lower()
    if file_ext not in allowed_ext:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file_ext}")

    file_id = str(uuid.uuid4())
    original_filename = f"post_{file_id}.{file_ext}"
    original_path = os.path.join(UPLOAD_FOLDER, original_filename)

    content = await image.read()
    with open(original_path, "wb") as f:
        f.write(content)

    # Find username
    username = "Anonymous"
    for u in users:
        if u["id"] == user_id:
            username = u["email"].split("@")[0].capitalize()  # simple username
            break

    post = {
        "id": file_id,
        "user_id": user_id,
        "username": username,
        "caption": caption,
        "image_url": f"{UPLOAD_URL_PREFIX}/{original_filename}",
        "created_at": datetime.utcnow().isoformat(),
        "likes_count": 0,
        "dislikes_count": 0,
        "likes_by": [],
        "dislikes_by": [],
        "saved_by": []
    }

    feed.append(post)
    logger.info(f"Created post {file_id} by {user_id}")

    return {
        "success": True,
        "message": "Post created successfully",
        "post": post
    }

@router.get("/posts")
def get_posts(user_id: Optional[str] = None):
    result = []
    for post in feed:
        p = post.copy()
        if user_id:
            p["is_liked_by_current_user"] = user_id in post.get("likes_by", [])
            p["is_disliked_by_current_user"] = user_id in post.get("dislikes_by", [])
            p["is_saved_by_current_user"] = user_id in post.get("saved_by", [])
        result.append(p)
    return {"feed": result}

@router.post("/posts/{post_id}/like")
def toggle_like(post_id: str, request: LikeRequest):
    post = next((p for p in feed if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if request.user_id in post["likes_by"]:
        post["likes_by"].remove(request.user_id)
        post["likes_count"] -= 1
    else:
        # unlike dislike if active
        if request.user_id in post["dislikes_by"]:
            post["dislikes_by"].remove(request.user_id)
            post["dislikes_count"] -= 1
        post["likes_by"].append(request.user_id)
        post["likes_count"] += 1

    return {"success": True, "post": post}

@router.post("/posts/{post_id}/dislike")
def toggle_dislike(post_id: str, request: LikeRequest):
    post = next((p for p in feed if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if request.user_id in post["dislikes_by"]:
        post["dislikes_by"].remove(request.user_id)
        post["dislikes_count"] -= 1
    else:
        # unlike like if active
        if request.user_id in post["likes_by"]:
            post["likes_by"].remove(request.user_id)
            post["likes_count"] -= 1
        post["dislikes_by"].append(request.user_id)
        post["dislikes_count"] += 1

    return {"success": True, "post": post}

@router.post("/posts/{post_id}/save")
def toggle_save(post_id: str, request: LikeRequest):
    post = next((p for p in feed if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post["saved_by"] = post.get("saved_by", [])
    
    if request.user_id in post["saved_by"]:
        post["saved_by"].remove(request.user_id)
    else:
        post["saved_by"].append(request.user_id)

    return {"success": True, "post": post}

@router.get("/saved/{user_id}")
def get_saved(user_id: str):
    saved = [p for p in feed if user_id in p.get("saved_by", [])]
    result = []
    for post in saved:
        p = post.copy()
        p["is_liked_by_current_user"] = user_id in p.get("likes_by", [])
        p["is_disliked_by_current_user"] = user_id in p.get("dislikes_by", [])
        p["is_saved_by_current_user"] = True
        result.append(p)
    return {"saved": result}
