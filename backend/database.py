import os
from datetime import date, datetime
from dotenv import load_dotenv
from bson import ObjectId
from pymongo import MongoClient
from pymongo.server_api import ServerApi

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


def serialize_value(value):
    """Recursively convert MongoDB/BSON values into JSON-safe Python values."""
    if value is None:
        return None

    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {key: serialize_value(val) for key, val in value.items()}

    if isinstance(value, list):
        return [serialize_value(item) for item in value]

    if isinstance(value, tuple):
        return [serialize_value(item) for item in value]

    return value


def serialize_doc(doc):
    """Convert a MongoDB document to a JSON-serializable dict."""
    if doc is None:
        return None

    if not isinstance(doc, dict):
        return serialize_value(doc)

    return {key: serialize_value(value) for key, value in doc.items()}


def serialize_list(docs):
    """Convert MongoDB cursor/list to a JSON-serializable list."""
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