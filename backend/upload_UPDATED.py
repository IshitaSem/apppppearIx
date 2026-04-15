from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import uuid
import os
import base64
from PIL import Image
import io
import logging
from datetime import datetime
from database import wardrobe_collection

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_FOLDER = "uploads"
BASE_URL = os.getenv("BASE_URL", "http://192.168.1.3:8000")  # URL prefix for served uploads
"image_url": f"{BASE_URL}/uploads/{final_filename}",
"original_image_url": f"{BASE_URL}/uploads/{original_filename}",

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except Exception as e:
    REMBG_AVAILABLE = False
    logging.warning(f"rembg not available: {e}")

logger = logging.getLogger(__name__)


def get_dominant_color(image_path: str) -> str:
    try:
        image = Image.open(image_path).convert("RGB")
        image = image.resize((50, 50))
        pixels = list(image.getdata())

        avg_color = tuple(sum(col) // len(col) for col in zip(*pixels))
        r, g, b = avg_color

        if b > r and b > g:
            return "blue"
        elif r > g and r > b:
            return "red"
        elif g > r and g > b:
            return "green"
        elif r > 180 and g > 180 and b > 180:
            return "white"
        elif r < 70 and g < 70 and b < 70:
            return "black"
        elif r > 150 and g > 100 and b < 100:
            return "brown"
        elif r > 180 and g > 180 and b < 120:
            return "yellow"
        else:
            return "unknown"
    except Exception as e:
        logger.warning(f"Color detection failed: {e}")
        return "unknown"


def detect_clothing_type(filename: str) -> str:
    name = filename.lower()

    top_keywords = [
        "shirt", "tshirt", "t-shirt", "top", "hoodie",
        "sweater", "tee", "blouse", "kurti"
    ]
    bottom_keywords = [
        "jeans", "pant", "pants", "trouser", "bottom",
        "skirt", "shorts", "leggings"
    ]
    shoes_keywords = [
        "shoe", "shoes", "sneaker", "heel", "heels",
        "boot", "boots", "sandals"
    ]

    for word in top_keywords:
        if word in name:
            return "top"

    for word in bottom_keywords:
        if word in name:
            return "bottom"

    for word in shoes_keywords:
        if word in name:
            return "shoes"

    return "unknown"


def pick_uploaded_file(
    file: Optional[UploadFile],
    image: Optional[UploadFile],
) -> UploadFile:
    uploaded = file or image
    if uploaded is None:
        raise HTTPException(
            status_code=400,
            detail="No uploaded file found. Send multipart field 'file' or 'image'."
        )
    return uploaded


@router.post("/")
async def upload_image(
    user_id: str = Form(...),
    use_bg_removal: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
):
    """Upload image with optional background removal. Returns backend-served URLs."""
    uploaded_file = pick_uploaded_file(file, image)

    if not uploaded_file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Validate file type
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    file_ext = uploaded_file.filename.split(".")[-1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type .{file_ext} not allowed. Use: {', '.join(allowed_extensions)}"
        )

    file_id = str(uuid.uuid4())
    original_filename = f"{file_id}.{file_ext}"
    original_path = os.path.join(UPLOAD_FOLDER, original_filename)

    content = await uploaded_file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Save original
    try:
        with open(original_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save image")

    # Attempt BG removal
    final_filename = original_filename
    bg_removed = False
    processing_error = None

    if use_bg_removal:
        if not REMBG_AVAILABLE:
            processing_error = "Background remover not available"
            logger.warning("BG removal requested but rembg not available")
        else:
            try:
                input_image = Image.open(io.BytesIO(content))
                if input_image.mode == 'RGBA':
                    input_image = input_image.convert('RGB')
                
                result = remove(input_image)
                
                bg_removed_filename = f"bg_removed_{file_id}.png"
                bg_removed_path = os.path.join(UPLOAD_FOLDER, bg_removed_filename)
                
                if isinstance(result, Image.Image):
                    result.save(bg_removed_path, "PNG")
                else:
                    with open(bg_removed_path, "wb") as out:
                        out.write(result)
                
                final_filename = bg_removed_filename
                bg_removed = True
                logger.info(f"Background removed: {file_id}")
            except Exception as e:
                # Graceful fallback
                logger.warning(f"BG removal failed: {e}")
                processing_error = f"Background removal failed"
                final_filename = original_filename
                bg_removed = False

    # Detect attributes
    final_image_path = os.path.join(UPLOAD_FOLDER, final_filename)
    try:
        detected_color = get_dominant_color(final_image_path)
        detected_category = detect_clothing_type(uploaded_file.filename)
    except Exception as e:
        logger.warning(f"Attribute detection failed: {e}")
        detected_color = "unknown"
        detected_category = "unknown"

    # Response with backend URLs
    item = {
        "id": file_id,
        "user_id": user_id,
        "name": uploaded_file.filename.split(".")[0],
        "category": detected_category.lower(),
        "color": detected_color,
        "image_url": f"{UPLOAD_URL_PREFIX}/{final_filename}",
        "original_image_url": f"{UPLOAD_URL_PREFIX}/{original_filename}",
        "background_removed": bg_removed,
        "created_at": datetime.utcnow().isoformat()
    }

    wardrobe_collection.insert_one(...)

    return {
        "success": True,
        "message": "Image uploaded successfully" if not processing_error else f"Image uploaded, {processing_error}",
        "data": item,
        "error": processing_error
    }


@router.post("/remove-background")
async def remove_background(
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
):
    """Remove background and return base64."""
    if not REMBG_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="Background remover not installed"
        )

    uploaded_file = pick_uploaded_file(file, image)

    if not uploaded_file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    content = await uploaded_file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        input_image = Image.open(io.BytesIO(content))
        if input_image.mode == 'RGBA':
            input_image = input_image.convert('RGB')
        
        result = remove(input_image)
        
        if isinstance(result, Image.Image):
            result_bytes = io.BytesIO()
            result.save(result_bytes, format="PNG")
            result_bytes = result_bytes.getvalue()
        else:
            result_bytes = result
        
        encoded_image = base64.b64encode(result_bytes).decode("utf-8")
        
        return {
            "success": True,
            "message": "Background removed successfully",
            "data": {
                "image_base64": encoded_image,
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"BG removal failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Background removal failed: {str(e)}"
        )
