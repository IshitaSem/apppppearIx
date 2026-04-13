from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from upload import router as upload_router
from auth import router as auth_router
from wardrobe import router as wardrobe_router
from outfit import router as outfit_router
from planner import router as planner_router
from ai_stylist import router as ai_stylist_router
from feed import router as feed_router
from fashion_tools import router as fashion_tools_router
import uvicorn

app = FastAPI(title="Appearix Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(upload_router)
app.include_router(auth_router)
app.include_router(wardrobe_router)
app.include_router(outfit_router)
app.include_router(planner_router)
app.include_router(ai_stylist_router)
app.include_router(feed_router)
app.include_router(fashion_tools_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1", 
        port=8000,
        reload=True
    )
