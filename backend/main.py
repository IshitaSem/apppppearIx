from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from upload import router as upload_router
from auth import router as auth_router
from wardrobe import router as wardrobe_router
from planner import router as planner_router
from ai_stylist import router as ai_stylist_router
from feed import router as feed_router
from fashion_tools import router as fashion_tools_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Appearix Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

logger.info(f"Static uploads directory: {UPLOADS_DIR}")

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.on_event("startup")
async def startup_event():
    logger.info("Appearix backend starting...")
    logger.info(f"BASE_DIR: {BASE_DIR}")
    logger.info(f"UPLOADS_DIR: {UPLOADS_DIR}")
    logger.info(f"Uploads directory exists: {os.path.exists(UPLOADS_DIR)}")


@app.get("/")
def home():
    return {
        "message": "Appearix Backend is running",
        "uploads_url": "/uploads",
    }


@app.get("/health")
def health():
    files = []
    try:
        files = os.listdir(UPLOADS_DIR)
    except Exception:
        files = []

    return {
        "status": "healthy",
        "uploads_dir": UPLOADS_DIR,
        "uploads_exists": os.path.exists(UPLOADS_DIR),
        "uploads_file_count": len(files),
        "uploads_files": files[:20],
    }


app.include_router(upload_router)
app.include_router(auth_router)
app.include_router(wardrobe_router)
app.include_router(planner_router)
app.include_router(ai_stylist_router)
app.include_router(feed_router)
app.include_router(fashion_tools_router)
