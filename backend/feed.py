import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from database import db

router = APIRouter(prefix="/feed", tags=["Feed"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def serialize_post(post: dict, current_user_id: Optional[str] = None) -> dict:
    if not post:
        return {}

    image_url = post.get("image_url", "")
    if image_url and not image_url.startswith("http"):
        if not image_url.startswith("/"):
            image_url = f"/{image_url}"

    likes_by = post.get("likes_by", [])
    dislikes_by = post.get("dislikes_by", [])
    saved_by = post.get("saved_by", [])

    return {
        "id": post.get("id"),
        "user_id": post.get("user_id"),
        "username": post.get("username", "User"),
        "caption": post.get("caption", ""),
        "image_url": image_url,
        "created_at": str(post.get("created_at", "")),
        "likes_count": post.get("likes_count", len(likes_by)),
        "dislikes_count": post.get("dislikes_count", len(dislikes_by)),
        "likes_by": likes_by,
        "dislikes_by": dislikes_by,
        "saved_by": saved_by,
        "is_liked_by_current_user": current_user_id in likes_by if current_user_id else False,
        "is_disliked_by_current_user": current_user_id in dislikes_by if current_user_id else False,
        "is_saved_by_current_user": current_user_id in saved_by if current_user_id else False,
    }


@router.post("/posts")
async def create_post(
    user_id: str = Form(...),
    caption: str = Form(...),
    image: UploadFile = File(...),
):
    try:
        if not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required")

        if not caption.strip():
            raise HTTPException(status_code=400, detail="caption is required")

        image_bytes = await image.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Image file is empty")

        ext = os.path.splitext(image.filename or "")[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".png"

        file_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        post = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": "User",
            "caption": caption.strip(),
            "image_url": f"/uploads/{file_name}",
            "created_at": datetime.utcnow(),
            "likes_by": [],
            "dislikes_by": [],
            "saved_by": [],
            "likes_count": 0,
            "dislikes_count": 0,
        }

        created_post = db.create_post(post)
        if not created_post:
            raise HTTPException(status_code=500, detail="Failed to save post")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Post created successfully",
                "post": serialize_post(created_post, user_id),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create post failed: {str(e)}")


@router.get("/posts")
def get_posts(user_id: Optional[str] = None):
    try:
        posts = db.get_posts(user_id=user_id)
        serialized = [serialize_post(post, user_id) for post in posts]

        return {
            "success": True,
            "feed": serialized,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")


@router.post("/posts/{post_id}/like")
def toggle_like(post_id: str, payload: dict):
    try:
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        post = next((p for p in db.get_posts(user_id=user_id) if p.get("id") == post_id), None)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        likes_by = post.get("likes_by", [])
        dislikes_by = post.get("dislikes_by", [])

        if user_id in likes_by:
            db.update_post_interaction(post_id, user_id, "unlike")
            updated = db.feed_collection.find_one({"id": post_id})
            if updated:
                updated["likes_by"] = [u for u in updated.get("likes_by", []) if u != user_id]
                updated["likes_count"] = max(0, len(updated.get("likes_by", [])))
        else:
            db.update_post_interaction(post_id, user_id, "like")
            updated = db.feed_collection.find_one({"id": post_id})

        return {
            "success": True,
            "post": serialize_post(updated, user_id),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Like failed: {str(e)}")


@router.post("/posts/{post_id}/dislike")
def toggle_dislike(post_id: str, payload: dict):
    try:
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        post = next((p for p in db.get_posts(user_id=user_id) if p.get("id") == post_id), None)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        dislikes_by = post.get("dislikes_by", [])

        if user_id in dislikes_by:
            db.feed_collection.update_one(
                {"id": post_id},
                {
                    "$pull": {"dislikes_by": user_id},
                    "$set": {"dislikes_count": max(0, len(dislikes_by) - 1)},
                },
            )
        else:
            db.update_post_interaction(post_id, user_id, "dislike")

        updated = db.feed_collection.find_one({"id": post_id})

        return {
            "success": True,
            "post": serialize_post(updated, user_id),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dislike failed: {str(e)}")


@router.post("/posts/{post_id}/save")
def toggle_save(post_id: str, payload: dict):
    try:
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        post = db.feed_collection.find_one({"id": post_id})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        saved_by = post.get("saved_by", [])

        if user_id in saved_by:
            db.update_post_interaction(post_id, user_id, "unsave")
        else:
            db.update_post_interaction(post_id, user_id, "save")

        updated = db.feed_collection.find_one({"id": post_id})

        return {
            "success": True,
            "post": serialize_post(updated, user_id),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")


@router.get("/saved/{user_id}")
def get_saved_posts(user_id: str):
    try:
        posts = db.get_saved_posts(user_id)
        serialized = [serialize_post(post, user_id) for post in posts]

        return {
            "success": True,
            "saved": serialized,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch saved posts: {str(e)}")
