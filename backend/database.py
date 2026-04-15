import os
import pymongo
from pymongo.errors import ConnectionFailure, PyMongoError
from typing import List, Dict, Any, Optional
import logging
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Database:
    _client = None
    _db = None
    
    def __init__(self):
        self.mongo_url = os.getenv("MONGO_URL")
        if not self.mongo_url:
            raise ValueError("MONGO_URL environment variable is required")
        
        try:
            self._client = pymongo.MongoClient(self.mongo_url)
            self._db = self._client["appearix"]
            # Test connection
            self._client.admin.command('ping')
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
        """Get wardrobe items for user"""
        try:
            return list(self.wardrobe_collection.find({"user_id": user_id}).sort("created_at", -1))
        except PyMongoError as e:
            logger.error(f"Error fetching user items: {e}")
            return []
    
    def add_item(self, item: Dict) -> Optional[Dict]:
        """Add wardrobe item"""
        try:
            item["created_at"] = item.get("created_at", pymongo.datetime.datetime.utcnow())
            result = self.wardrobe_collection.insert_one(item)
            item["_id"] = result.inserted_id
            return item
        except PyMongoError as e:
            logger.error(f"Error adding item: {e}")
            return None
    
    def get_item(self, item_id: str) -> Optional[Dict]:
        """Get single item"""
        try:
            return self.wardrobe_collection.find_one({"id": item_id})
        except PyMongoError as e:
            logger.error(f"Error getting item {item_id}: {e}")
            return None
    
    def update_item(self, item_id: str, updates: Dict) -> bool:
        """Update item"""
        try:
            result = self.wardrobe_collection.update_one(
                {"id": item_id},
                {"$set": {**updates, "updated_at": pymongo.datetime.datetime.utcnow()}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating item {item_id}: {e}")
            return False
    
    def delete_item(self, item_id: str) -> bool:
        """Delete item"""
        try:
            result = self.wardrobe_collection.delete_one({"id": item_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Error deleting item {item_id}: {e}")
            return False
    
    def create_user(self, user: Dict) -> Optional[Dict]:
        """Create user"""
        try:
            result = self.users_collection.insert_one(user)
            user["_id"] = result.inserted_id
            return user
        except PyMongoError:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            return self.users_collection.find_one({"email": email.lower()})
        except PyMongoError:
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            return self.users_collection.find_one({"id": user_id})
        except PyMongoError:
            return None
    
    def save_outfit(self, outfit: Dict) -> Optional[Dict]:
        """Save outfit"""
        try:
            result = self.outfits_collection.insert_one(outfit)
            outfit["_id"] = result.inserted_id
            return outfit
        except PyMongoError:
            return None
    
    def get_user_outfits(self, user_id: str) -> List[Dict]:
        """Get user outfits"""
        try:
            return list(self.outfits_collection.find({"user_id": user_id}))
        except PyMongoError:
            return []
    
    def save_plan(self, plan: Dict) -> Optional[Dict]:
        """Save planner item"""
        try:
            result = self.planner_collection.insert_one(plan)
            plan["_id"] = result.inserted_id
            return plan
        except PyMongoError:
            return None
    
    def get_user_plans(self, user_id: str) -> List[Dict]:
        """Get user plans"""
        try:
            return list(self.planner_collection.find({"user_id": user_id}))
        except PyMongoError:
            return []
    
    def create_post(self, post: Dict) -> Optional[Dict]:
        """Create feed post"""
        try:
            result = self.feed_collection.insert_one(post)
            post["_id"] = result.inserted_id
            return post
        except PyMongoError:
            return None
    
    def get_posts(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get feed posts"""
        try:
            pipeline = [{"$sort": {"created_at": -1}}]
            if user_id:
                pipeline.append({
                    "$addFields": {
                        "is_liked_by_current_user": {"$in": [user_id, "$likes_by"]},
                        "is_disliked_by_current_user": {"$in": [user_id, "$dislikes_by"]},
                        "is_saved_by_current_user": {"$in": [user_id, "$saved_by"]}
                    }
                })
            return list(self.feed_collection.aggregate(pipeline))
        except PyMongoError as e:
            logger.error(f"Error getting posts: {e}")
            return []
    
    def update_post_interaction(self, post_id: str, user_id: str, action: str) -> bool:
        """Like/dislike/save post"""
        try:
            if action == "like":
                self.feed_collection.update_one(
                    {"id": post_id},
                    {
                        "$addToSet": {"likes_by": user_id},
                        "$pull": {"dislikes_by": user_id},
                        "$inc": {"likes_count": 1, "dislikes_count": -1}
                    }
                )
            elif action == "dislike":
                self.feed_collection.update_one(
                    {"id": post_id},
                    {
                        "$addToSet": {"dislikes_by": user_id},
                        "$pull": {"likes_by": user_id},
                        "$inc": {"dislikes_count": 1, "likes_count": -1}
                    }
                )
            elif action == "save":
                self.feed_collection.update_one(
                    {"id": post_id},
                    {"$addToSet": {"saved_by": user_id}}
                )
            elif action == "unsave":
                self.feed_collection.update_one(
                    {"id": post_id},
                    {"$pull": {"saved_by": user_id}}
                )
            return True
        except PyMongoError:
            return False
    
    def get_saved_posts(self, user_id: str) -> List[Dict]:
        """Get saved posts for user"""
        try:
            return list(self.feed_collection.find({"saved_by": user_id}).sort("created_at", -1))
        except PyMongoError:
            return []

# Global instance
db = Database()

