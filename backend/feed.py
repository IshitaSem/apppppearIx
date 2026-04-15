from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from database import feed_collection, users_collection, serialize_doc, serialize_list
from pydantic import BaseModel
from pymongo import DESCENDING
import uuid
import os
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter(prefix="/feed", tags=["Global Feed"])


def get_base_url(request: Request) -> str:
    env_base_url = os.getenv("BASE_URL", "").strip()
    if env_base_url:
        return env_base_url.rstrip("/")
    return str(request.base_url).rstrip("/")


def build_file_url(request: Request, filename: str) -> str:
    return f"{get_base_url(request)}/uploads/{filename}"


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
    request: Request,
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
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")

    with open(original_path, "wb") as f:
        f.write(content)

    user_doc = serialize_doc(users_collection.find_one({"id": user_id}))
    username = "Anonymous"
    if user_doc and user_doc.get("email"):
        username = user_doc["email"].split("@")[0].capitalize()

    post = {
        "id": file_id,
        "user_id": user_id,
        "username": username,
        "caption": caption.strip(),
        "image_url": build_file_url(request, original_filename),
        "image_path": original_filename,
        "created_at": datetime.utcnow().isoformat(),
        "likes_count": 0,
        "dislikes_count": 0,
        "likes_by": [],
        "dislikes_by": [],
        "saved_by": []
    }

    result = feed_collection.insert_one(post)
    logger.info(f"Created post {file_id} by {user_id}")

    inserted_post = serialize_doc(feed_collection.find_one({"_id": result.inserted_id}))

    return {
        "success": True,
        "post": inserted_post
    }


@router.get("/posts")
def get_posts(user_id: Optional[str] = None):
    posts = serialize_list(list(feed_collection.find().sort("created_at", DESCENDING)))
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
        feed_collection.update_one(
            {"id": post_id},
            {
                "$pull": {"likes_by": user_id},
                "$inc": {"likes_count": -1}
            }
        )
    else:
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
        feed_collection.update_one(
            {"id": post_id},
            {
                "$pull": {"dislikes_by": user_id},
                "$inc": {"dislikes_count": -1}
            }
        )
    else:
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
    saved = serialize_list(list(feed_collection.find({"saved_by": user_id})))
    for p in saved:
        p["is_liked_by_current_user"] = user_id in p.get("likes_by", [])
        p["is_disliked_by_current_user"] = user_id in p.get("dislikes_by", [])
        p["is_saved_by_current_user"] = True
    return {"saved": saved}
