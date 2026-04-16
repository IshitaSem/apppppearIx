from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from pymongo import DESCENDING
from datetime import datetime
from typing import Optional
import uuid
import os
import logging

from database import db

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
UPLOAD_URL_PREFIX = "/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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


def serialize_doc(doc):
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def serialize_list(cursor):
    return [serialize_doc(doc) for doc in cursor]


@router.post("/posts")
async def create_post(
    user_id: str = Form(...),
    caption: str = Form(...),
    image: UploadFile = File(...),
):
    if not image.filename:
        raise HTTPException(status_code=400, detail="No image provided")

    allowed_ext = {"jpg", "jpeg", "png", "webp", "gif"}
    file_ext = image.filename.split(".")[-1].lower()

    if file_ext not in allowed_ext:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file_ext}")

    file_id = str(uuid.uuid4())
    filename = f"post_{file_id}.{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")

    with open(file_path, "wb") as f:
        f.write(content)

    user_doc = db.get_user_by_id(user_id)
    username = "Anonymous"
    if user_doc and user_doc.get("email"):
        username = user_doc["email"].split("@")[0].capitalize()

    post = {
        "id": file_id,
        "user_id": user_id,
        "username": username,
        "caption": caption,
        "image_url": f"{UPLOAD_URL_PREFIX}/{filename}",
        "created_at": datetime.utcnow().isoformat(),
        "likes_count": 0,
        "dislikes_count": 0,
        "likes_by": [],
        "dislikes_by": [],
        "saved_by": [],
    }

    created_post = db.create_post(post)
    if not created_post:
        raise HTTPException(status_code=500, detail="Failed to create post")

    logger.info(f"Created post {file_id} by {user_id}, file saved at {file_path}")

    return {
        "success": True,
        "message": "Post created successfully",
        "post": created_post,
    }


@router.get("/posts")
def get_posts(user_id: Optional[str] = None):
    posts = db.get_posts(user_id=user_id)
    return {"feed": posts}


@router.post("/posts/{post_id}/like")
def toggle_like(post_id: str, request: LikeRequest):
    post_doc = db.get_post_by_id(post_id)
    if not post_doc:
        raise HTTPException(status_code=404, detail="Post not found")

    user_id = request.user_id
    likes_by = post_doc.get("likes_by", [])
    dislikes_by = post_doc.get("dislikes_by", [])

    if user_id in likes_by:
        success = db.update_post_interaction(post_id, user_id, "unlike")
    else:
        if user_id in dislikes_by:
            db.update_post_interaction(post_id, user_id, "undislike")
        success = db.update_post_interaction(post_id, user_id, "like")

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update like")

    updated_post = db.get_post_by_id(post_id)
    return {"success": True, "post": updated_post}


@router.post("/posts/{post_id}/dislike")
def toggle_dislike(post_id: str, request: LikeRequest):
    post_doc = db.get_post_by_id(post_id)
    if not post_doc:
        raise HTTPException(status_code=404, detail="Post not found")

    user_id = request.user_id
    dislikes_by = post_doc.get("dislikes_by", [])
    likes_by = post_doc.get("likes_by", [])

    if user_id in dislikes_by:
        success = db.update_post_interaction(post_id, user_id, "undislike")
    else:
        if user_id in likes_by:
            db.update_post_interaction(post_id, user_id, "unlike")
        success = db.update_post_interaction(post_id, user_id, "dislike")

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update dislike")

    updated_post = db.get_post_by_id(post_id)
    return {"success": True, "post": updated_post}


@router.post("/posts/{post_id}/save")
def toggle_save(post_id: str, request: LikeRequest):
    post_doc = db.get_post_by_id(post_id)
    if not post_doc:
        raise HTTPException(status_code=404, detail="Post not found")

    user_id = request.user_id
    saved_by = post_doc.get("saved_by", [])

    action = "unsave" if user_id in saved_by else "save"
    success = db.update_post_interaction(post_id, user_id, action)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update save")

    updated_post = db.get_post_by_id(post_id)
    return {"success": True, "post": updated_post}


@router.get("/saved/{user_id}")
def get_saved(user_id: str):
    saved = db.get_saved_posts(user_id)
    for p in saved:
        p["is_liked_by_current_user"] = user_id in p.get("likes_by", [])
        p["is_disliked_by_current_user"] = user_id in p.get("dislikes_by", [])
        p["is_saved_by_current_user"] = True
    return {"saved": saved}
