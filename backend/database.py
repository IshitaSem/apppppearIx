import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

import pymongo
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.mongo_url = os.getenv("MONGO_URL")
        if not self.mongo_url:
            raise ValueError("MONGO_URL environment variable is required")

        try:
            self._client = pymongo.MongoClient(self.mongo_url)
            self._db = self._client["appearix"]

            self._client.admin.command("ping")
            logger.info("MongoDB connected successfully")
        except ConnectionFailure:
            logger.error("MongoDB connection failed")
            raise
        except Exception as e:
            logger.error(f"MongoDB init error: {e}")
            raise

    @property
    def wardrobe_collection(self):
        return self._db["wardrobe_items"]

    @property
    def users_collection(self):
        return self._db["users"]

    @property
    def outfits_collection(self):
        return self._db["outfits"]

    @property
    def planner_collection(self):
        return self._db["planner"]

    @property
    def feed_collection(self):
        return self._db["feed"]

    def get_user_items(self, user_id: str) -> List[Dict]:
        try:
            return list(
                self.wardrobe_collection.find({"user_id": user_id}).sort(
                    "created_at", -1
                )
            )
        except PyMongoError as e:
            logger.error(f"Error fetching user items: {e}")
            return []

    def add_item(self, item: Dict) -> Optional[Dict]:
        try:
            item["created_at"] = item.get("created_at", datetime.utcnow())
            result = self.wardrobe_collection.insert_one(item)
            item["_id"] = str(result.inserted_id)
            return item
        except PyMongoError as e:
            logger.error(f"Error adding item: {e}")
            return None

    def get_item(self, item_id: str) -> Optional[Dict]:
        try:
            return self.wardrobe_collection.find_one({"id": item_id})
        except PyMongoError as e:
            logger.error(f"Error getting item {item_id}: {e}")
            return None

    def update_item(self, item_id: str, updates: Dict) -> bool:
        try:
            updates["updated_at"] = datetime.utcnow()
            result = self.wardrobe_collection.update_one(
                {"id": item_id},
                {"$set": updates},
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating item {item_id}: {e}")
            return False

    def delete_item(self, item_id: str) -> bool:
        try:
            result = self.wardrobe_collection.delete_one({"id": item_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Error deleting item {item_id}: {e}")
            return False

    def create_user(self, user: Dict) -> Optional[Dict]:
        try:
            user["email"] = user.get("email", "").lower()
            user["created_at"] = user.get("created_at", datetime.utcnow())
            result = self.users_collection.insert_one(user)
            user["_id"] = str(result.inserted_id)
            return user
        except PyMongoError as e:
            logger.error(f"Error creating user: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        try:
            return self.users_collection.find_one({"email": email.lower()})
        except PyMongoError as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        try:
            return self.users_collection.find_one({"id": user_id})
        except PyMongoError as e:
            logger.error(f"Error getting user by id: {e}")
            return None

    def save_outfit(self, outfit: Dict) -> Optional[Dict]:
        try:
            outfit["created_at"] = outfit.get("created_at", datetime.utcnow())
            result = self.outfits_collection.insert_one(outfit)
            outfit["_id"] = str(result.inserted_id)
            return outfit
        except PyMongoError as e:
            logger.error(f"Error saving outfit: {e}")
            return None

    def get_user_outfits(self, user_id: str) -> List[Dict]:
        try:
            return list(
                self.outfits_collection.find({"user_id": user_id}).sort(
                    "created_at", -1
                )
            )
        except PyMongoError as e:
            logger.error(f"Error getting user outfits: {e}")
            return []

    def save_plan(self, plan: Dict) -> Optional[Dict]:
        try:
            plan["created_at"] = plan.get("created_at", datetime.utcnow())
            result = self.planner_collection.insert_one(plan)
            plan["_id"] = str(result.inserted_id)
            return plan
        except PyMongoError as e:
            logger.error(f"Error saving plan: {e}")
            return None

    def get_user_plans(self, user_id: str) -> List[Dict]:
        try:
            return list(
                self.planner_collection.find({"user_id": user_id}).sort(
                    "created_at", -1
                )
            )
        except PyMongoError as e:
            logger.error(f"Error getting user plans: {e}")
            return []

    def create_post(self, post: Dict) -> Optional[Dict]:
        try:
            post["created_at"] = post.get("created_at", datetime.utcnow())
            post.setdefault("likes_by", [])
            post.setdefault("dislikes_by", [])
            post.setdefault("saved_by", [])
            post.setdefault("likes_count", 0)
            post.setdefault("dislikes_count", 0)

            result = self.feed_collection.insert_one(post)
            post["_id"] = str(result.inserted_id)
            return post
        except PyMongoError as e:
            logger.error(f"Error creating post: {e}")
            return None

    def get_posts(self, user_id: Optional[str] = None) -> List[Dict]:
        try:
            pipeline = [{"$sort": {"created_at": -1}}]

            if user_id:
                pipeline.append(
                    {
                        "$addFields": {
                            "is_liked_by_current_user": {
                                "$in": [user_id, {"$ifNull": ["$likes_by", []]}]
                            },
                            "is_disliked_by_current_user": {
                                "$in": [user_id, {"$ifNull": ["$dislikes_by", []]}]
                            },
                            "is_saved_by_current_user": {
                                "$in": [user_id, {"$ifNull": ["$saved_by", []]}]
                            },
                        }
                    }
                )

            return list(self.feed_collection.aggregate(pipeline))
        except PyMongoError as e:
            logger.error(f"Error getting posts: {e}")
            return []

    def update_post_interaction(self, post_id: str, user_id: str, action: str) -> bool:
        try:
            post = self.feed_collection.find_one({"id": post_id})
            if not post:
                return False

            likes_by = post.get("likes_by", [])
            dislikes_by = post.get("dislikes_by", [])
            saved_by = post.get("saved_by", [])

            update_query = {}

            if action == "like":
                if user_id not in likes_by:
                    update_query.setdefault("$addToSet", {})["likes_by"] = user_id
                    update_query.setdefault("$inc", {})["likes_count"] = 1

                if user_id in dislikes_by:
                    update_query.setdefault("$pull", {})["dislikes_by"] = user_id
                    update_query.setdefault("$inc", {})["dislikes_count"] = -1

            elif action == "unlike":
                if user_id in likes_by:
                    update_query.setdefault("$pull", {})["likes_by"] = user_id
                    update_query.setdefault("$inc", {})["likes_count"] = -1

            elif action == "dislike":
                if user_id not in dislikes_by:
                    update_query.setdefault("$addToSet", {})["dislikes_by"] = user_id
                    update_query.setdefault("$inc", {})["dislikes_count"] = 1

                if user_id in likes_by:
                    update_query.setdefault("$pull", {})["likes_by"] = user_id
                    update_query.setdefault("$inc", {})["likes_count"] = -1

            elif action == "undislike":
                if user_id in dislikes_by:
                    update_query.setdefault("$pull", {})["dislikes_by"] = user_id
                    update_query.setdefault("$inc", {})["dislikes_count"] = -1

            elif action == "save":
                if user_id not in saved_by:
                    update_query.setdefault("$addToSet", {})["saved_by"] = user_id

            elif action == "unsave":
                if user_id in saved_by:
                    update_query.setdefault("$pull", {})["saved_by"] = user_id

            if not update_query:
                return True

            self.feed_collection.update_one({"id": post_id}, update_query)
            return True

        except PyMongoError as e:
            logger.error(f"Error updating post interaction: {e}")
            return False

    def get_saved_posts(self, user_id: str) -> List[Dict]:
        try:
            return list(
                self.feed_collection.find({"saved_by": user_id}).sort(
                    "created_at", -1
                )
            )
        except PyMongoError as e:
            logger.error(f"Error getting saved posts: {e}")
            return []

    def get_post_by_id(self, post_id: str) -> Optional[Dict]:
        try:
            return self.feed_collection.find_one({"id": post_id})
        except PyMongoError as e:
            logger.error(f"Error getting post by id {post_id}: {e}")
            return None


db = Database()
