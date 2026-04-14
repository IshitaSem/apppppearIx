import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "appearix_db")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env")

client = MongoClient(
    MONGO_URI,
    server_api=ServerApi("1")
)

db = client[MONGO_DB_NAME]

# MongoDB collections
users_collection = db["users"]
wardrobe_collection = db["wardrobe_items"]
planner_collection = db["planner"]
posts_collection = db["posts"]
outfits_collection = db["outfits"]
feed_collection = db["feed"]

# Backward-compatible aliases for old files
users = users_collection
wardrobe_items = wardrobe_collection
planner = planner_collection
planner_items = planner_collection
posts = posts_collection
outfits = outfits_collection
feed = feed_collection


def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict - SAFE recursive serializer"""
    if doc is None:
        return None
    
    result = {}
    if "_id" in doc:
        result["_id"] = str(doc["_id"])
    
    for key, value in doc.items():
        if isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_item(item) for item in value]
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime.datetime):
            result[key] = value.isoformat()
        elif isinstance(value, (str, int, float, bool, type(None))):
            result[key] = value
        else:
            # Fallback for other types
            result[key] = str(value)
    
    return result


def serialize_item(item):
    """Helper to serialize single item in list - checks type first"""
    if isinstance(item, dict):
        return serialize_doc(item)
    elif isinstance(item, ObjectId):
        return str(item)
    elif isinstance(item, datetime.datetime):
        return item.isoformat()
    elif isinstance(item, (str, int, float, bool, type(None))):
        return item
    else:
        return str(item)


def serialize_list(docs):
    """Convert MongoDB cursor/list to JSON-serializable list"""
    if docs is None:
        return []
    return [serialize_doc(doc) for doc in docs]


def test_mongodb_connection():
    try:
        client.admin.command("ping")
        print("✅ MongoDB connected successfully")
        return True
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
        return False

