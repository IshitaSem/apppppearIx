from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

from database import test_mongodb_connection

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
    version="1.0.0",
    description="Backend API for Appearix - Smart Wardrobe Styling"
)

frontend_urls_env = os.getenv(
    "FRONTEND_URLS",
    "http://localhost:3000,"
    "http://127.0.0.1:3000,"
    "http://localhost:5000,"
    "http://127.0.0.1:5000,"
    "http://localhost:8000,"
    "http://127.0.0.1:8000,"
    "https://appearix-frontend.web.app,"
    "https://appearix-frontend.firebaseapp.com"
)

allowed_origins = [url.strip() for url in frontend_urls_env.split(",") if url.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
def startup_event():
    print("Starting Appearix backend...")
    print("Allowed CORS origins:", allowed_origins)
    try:
        db_ok = test_mongodb_connection()
        print("MongoDB connected:", db_ok)
    except Exception as e:
        print("MongoDB startup failed:", str(e))


@app.get("/")
def home():
    return {
        "message": "Appearix backend is running",
        "status": "ok"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/test-db")
def test_db():
    try:
        success = test_mongodb_connection()
        return {"mongodb_connected": success}
    except Exception as e:
        return {
            "mongodb_connected": False,
            "error": str(e)
        }


app.include_router(upload_router)
app.include_router(auth_router)
app.include_router(wardrobe_router)
app.include_router(outfit_router)
app.include_router(planner_router)
app.include_router(ai_stylist_router)
app.include_router(feed_router)
app.include_router(fashion_tools_router)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
