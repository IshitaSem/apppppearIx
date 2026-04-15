from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import logging
from contextlib import asynccontextmanager
from database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Starting Appearix Backend...")
        os.makedirs("uploads", exist_ok=True)
        logger.info("Backend startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    yield
    # Shutdown
    logger.info("Backend shutting down...")

from upload import router as upload_router
from auth import router as auth_router
from wardrobe import router as wardrobe_router
from outfit import router as outfit_router
from planner import router as planner_router
from ai_stylist import router as ai_stylist_router
from feed import router as feed_router
from fashion_tools import router as fashion_tools_router

app = FastAPI(
    title="Appearix Backend",
    description="Fashion app backend for Railway",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploads safely
app.mount("/uploads", StaticFiles(directory="uploads", html=False), name="uploads")

@app.get("/")
async def home():
    return {"message": "Appearix Backend is running on Railway"}

@app.get("/health")
async def health():
    try:
        # Test DB
        db.wardrobe_collection.count_documents({})
        return {"status": "healthy", "db": "connected"}
    except:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "db": "error"}
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )

# Include all routers
app.include_router(upload_router)
app.include_router(auth_router)
app.include_router(wardrobe_router)
app.include_router(outfit_router)
app.include_router(planner_router)
app.include_router(ai_stylist_router)
app.include_router(feed_router)
app.include_router(fashion_tools_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
