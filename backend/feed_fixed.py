from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from database import feed_collection, users_collection, serialize_doc, serialize_list
from pydantic import BaseModel
from pymongo import DESCENDING
import uuid
import os
from datetime import datetime
from typing import Optional
import logging
import os

BASE_URL = os.getenv("BASE_URL", "http://192.168.1.3:8000")

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads"
"image_url": f"{UPLOAD_URL_PREFIX}/{original_filename}",
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

    # Find username - SERIALIZE to be safe
    user_doc = serialize_doc(users_collection.find_one({"id": user_id}))
    username = "Anonymous"
    if user_doc and "email" in user_doc:
        username = user_doc["email"].split("@")[0].capitalize()

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

    # Insert and get inserted document (SERIALIZED)
    result = feed_collection.insert_one(post)
    inserted_post = serialize_doc(feed_collection.find_one({"_id": result.inserted_id}))
    
    logger.info(f"Created post {file_id} by {user_id}")

    return {
        "success": True,
        "message": "Post created successfully",
        "post": inserted_post  # Always serialized
    }

@router.get("/posts")
def get_posts(user_id: Optional[str] = None):
    # FIXED: Always serialize list from find()
    posts_cursor = feed_collection.find().sort("created_at", DESCENDING)
    posts = serialize_list(posts_cursor)
    
    if user_id:
        for p in posts:
            p["is_liked_by_current_user"] = user_id in p.get("likes_by", [])
            p["is_disliked_by_current_user"] = user_id in p.get("dislikes_by", [])
            p["is_saved_by_current_user"] = user_id in p.get("saved_by", [])
    return {"feed": posts}

@router.post("/posts/{post_id}/like")
def toggle_like(post_id: str, request: LikeRequest):
    post_doc = feed_collection.find_one({"id": post_id})
    if not post_doc:
        raise HTTPException(status_code=404, detail="Post not found")

    user_id = request.user_id
    likes_by = post_doc.get("likes_by", [])
    dislikes_by = post_doc.get("dislikes_by", [])

    if user_id in likes_by:
        # Unlike
        feed_collection.update_one(
            {"id": post_id},
            {
                "$pull": {"likes_by": user_id},
                "$inc": {"likes_count": -1}
            }
        )
    else:
        # Like (remove dislike if exists)
        if user_id in dislikes_by:
            feed_collection.update_one(
                {"id": post_id},
                {
                    "$pull": {"dislikes_by": user_id},
                    "$inc": {"dislikes_count": -1}
                }
            )
        feed_collection.update_one(
            {"id": post_id},
            {
                "$addToSet": {"likes_by": user_id},
                "$inc": {"likes_count": 1}
            }
        )

    # FIXED: Always return serialized post
    updated_post = serialize_doc(feed_collection.find_one({"id": post_id}))
    return {"success": True, "post": updated_post}

@router.post("/posts/{post_id}/dislike")
def toggle_dislike(post_id: str, request: LikeRequest):
    post_doc = feed_collection.find_one({"id": post_id})
    if not post_doc:
        raise HTTPException(status_code=404, detail="Post not found")

    user_id = request.user_id
    dislikes_by = post_doc.get("dislikes_by", [])
    likes_by = post_doc.get("likes_by", [])

    if user_id in dislikes_by:
        # Undislike
        feed_collection.update_one(
            {"id": post_id},
            {
                "$pull": {"dislikes_by": user_id},
                "$inc": {"dislikes_count": -1}
            }
        )
    else:
        # Dislike (remove like if exists)
        if user_id in likes_by:
            feed_collection.update_one(
                {"id": post_id},
                {
                    "$pull": {"likes_by": user_id},
                    "$inc": {"likes_count": -1}
                }
            )
        feed_collection.update_one(
            {"id": post_id},
            {
                "$addToSet": {"dislikes_by": user_id},
                "$inc": {"dislikes_count": 1}
            }
        )

    # FIXED: Always return serialized post
    updated_post = serialize_doc(feed_collection.find_one({"id": post_id}))
    return {"success": True, "post": updated_post}

@router.post("/posts/{post_id}/save")
def toggle_save(post_id: str, request: LikeRequest):
    post_doc = feed_collection.find_one({"id": post_id})
    if not post_doc:
        raise HTTPException(status_code=404, detail="Post not found")

    user_id = request.user_id
    saved_by = post_doc.get("saved_by", [])

    if user_id in saved_by:
        feed_collection.update_one(
            {"id": post_id},
            {"$pull": {"saved_by": user_id}}
        )
    else:
        feed_collection.update_one(
            {"id": post_id},
            {"$addToSet": {"saved_by": user_id}}
        )

    updated_post = serialize_doc(feed_collection.find_one({"id": post_id}))
    return {"success": True, "post": updated_post}

@router.get("/saved/{user_id}")
def get_saved(user_id: str):
    saved_cursor = feed_collection.find({"saved_by": user_id})
    saved = serialize_list(saved_cursor)
    for p in saved:
        p["is_liked_by_current_user"] = user_id in p.get("likes_by", [])
        p["is_disliked_by_current_user"] = user_id in p.get("dislikes_by", [])
        p["is_saved_by_current_user"] = True
    return {"saved": saved}

