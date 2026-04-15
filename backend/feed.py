from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
from database import db

router = APIRouter(prefix="/feed", tags=["Feed"])


class CreatePostRequest(BaseModel):
    user_id: str
    caption: Optional[str] = ""
    image_url: Optional[str] = None
    outfit_item_ids: List[str] = Field(default_factory=list)


class PostActionRequest(BaseModel):
    user_id: str


@router.post("/posts")
def create_post(request: CreatePostRequest):
    try:
        post = {
            "id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "caption": request.caption or "",
            "image_url": request.image_url,
            "outfit_item_ids": request.outfit_item_ids,
            "likes_by": [],
            "dislikes_by": [],
            "saved_by": [],
            "likes_count": 0,
            "dislikes_count": 0,
            "created_at": datetime.utcnow().isoformat(),
        }

        saved_post = db.create_post(post)
        if not saved_post:
            raise HTTPException(status_code=500, detail="Failed to create post")

        return {
            "success": True,
            "message": "Post created successfully",
            "data": saved_post
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")


@router.get("/posts")
def get_posts(user_id: Optional[str] = None):
    try:
        posts = db.get_posts(user_id)
        return {
            "success": True,
            "message": "Posts retrieved successfully",
            "data": posts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving posts: {str(e)}")


@router.post("/posts/{post_id}/like")
def like_post(post_id: str, request: PostActionRequest):
    try:
        ok = db.update_post_interaction(post_id, request.user_id, "like")
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to like post")

        return {
            "success": True,
            "message": "Post liked successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error liking post: {str(e)}")


@router.post("/posts/{post_id}/dislike")
def dislike_post(post_id: str, request: PostActionRequest):
    try:
        ok = db.update_post_interaction(post_id, request.user_id, "dislike")
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to dislike post")

        return {
            "success": True,
            "message": "Post disliked successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disliking post: {str(e)}")


@router.post("/posts/{post_id}/save")
def save_post(post_id: str, request: PostActionRequest):
    try:
        ok = db.update_post_interaction(post_id, request.user_id, "save")
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to save post")

        return {
            "success": True,
            "message": "Post saved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving post: {str(e)}")


@router.post("/posts/{post_id}/unsave")
def unsave_post(post_id: str, request: PostActionRequest):
    try:
        ok = db.update_post_interaction(post_id, request.user_id, "unsave")
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to unsave post")

        return {
            "success": True,
            "message": "Post unsaved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unsaving post: {str(e)}")


@router.get("/saved/{user_id}")
def get_saved_posts(user_id: str):
    try:
        posts = db.get_saved_posts(user_id)
        return {
            "success": True,
            "message": "Saved posts retrieved successfully",
            "data": posts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving saved posts: {str(e)}")
