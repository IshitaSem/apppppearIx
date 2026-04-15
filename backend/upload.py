from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import uuid
import os
import base64
from PIL import Image
import io
import logging
from datetime import datetime
import requests
from database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_FOLDER = "uploads"
UPLOAD_URL_PREFIX = "/uploads"
MODAL_BG_URL = "https://ishitasem--bg-remove-fastapi-app.modal.run/remove-bg"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


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


def remove_bg_with_modal(image_bytes: bytes) -> tuple[bytes, bool, Optional[str]]:
    try:
        files = {
            "file": ("image.png", image_bytes, "application/octet-stream")
        }

        response = requests.post(MODAL_BG_URL, files=files, timeout=120)

        if response.status_code == 200 and response.content:
            return response.content, True, None

        logger.warning(
            f"Modal BG remove failed with status {response.status_code}: {response.text}"
        )
        return image_bytes, False, f"Modal returned status {response.status_code}"

    except Exception as e:
        logger.warning(f"Modal BG remove error: {e}")
        return image_bytes, False, str(e)


@router.post("/")
async def upload_image(
    user_id: str = Form(...),
    use_bg_removal: bool = Form(False),
    item_name: str = Form(...),
    category: str = Form(...),
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
):
    uploaded_file = pick_uploaded_file(file, image)

    if not uploaded_file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    allowed_extensions = {"jpg", "jpeg", "png", "gif", "webp"}
    file_ext = uploaded_file.filename.split(".")[-1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{file_ext} not allowed. Use: {', '.join(sorted(allowed_extensions))}"
        )

    file_id = str(uuid.uuid4())
    original_filename = f"{file_id}.{file_ext}"
    original_path = os.path.join(UPLOAD_FOLDER, original_filename)

    content = await uploaded_file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        with open(original_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save original image: {e}")
        raise HTTPException(status_code=500, detail="Failed to save image")

    final_content = content
    final_filename = original_filename
    bg_removed = False
    processing_error = None

    if use_bg_removal:
        processed_bytes, bg_removed, processing_error = remove_bg_with_modal(content)

        if bg_removed:
            final_filename = f"{file_id}_bg_removed.png"
            final_path = os.path.join(UPLOAD_FOLDER, final_filename)

            try:
                with open(final_path, "wb") as f:
                    f.write(processed_bytes)
                final_content = processed_bytes
            except Exception as e:
                logger.warning(f"Failed to save bg removed image: {e}")
                final_filename = original_filename
                bg_removed = False
                processing_error = f"Failed to save processed image: {e}"

    final_image_path = os.path.join(UPLOAD_FOLDER, final_filename)

    from wardrobe import CATEGORY_MAP
    raw_category = category.strip().lower()

    try:
        detected_color = get_dominant_color(final_image_path)
        normalized_category = CATEGORY_MAP.get(raw_category, raw_category)
    except Exception as e:
        logger.warning(f"Attribute detection failed: {e}")
        detected_color = "unknown"
        normalized_category = raw_category

    item = {
        "id": file_id,
        "user_id": user_id,
        "name": item_name.strip(),
        "category": normalized_category,
        "color": detected_color,
        "image_path": final_filename,
        "image_url": f"{UPLOAD_URL_PREFIX}/{final_filename}",
        "original_image_url": f"{UPLOAD_URL_PREFIX}/{original_filename}",
        "background_removed": bg_removed,
        "processing_error": processing_error,
        "created_at": datetime.utcnow().isoformat()
    }

    added_item = db.add_item(item)
    if added_item:
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "data": added_item
        }

    raise HTTPException(status_code=500, detail="Failed to save item metadata")


@router.post("/remove-background")
async def remove_background(
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
):
    uploaded_file = pick_uploaded_file(file, image)

    if not uploaded_file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    content = await uploaded_file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        original_image = Image.open(io.BytesIO(content)).convert("RGBA")
    except Exception as e:
        logger.error(f"Invalid image file: {e}")
        raise HTTPException(status_code=400, detail="Invalid image file")

    processed_bytes, bg_removed, processing_error = remove_bg_with_modal(content)

    try:
        result_image = Image.open(io.BytesIO(processed_bytes)).convert("RGBA")
    except Exception:
        result_image = original_image
        bg_removed = False

    result_bytes = io.BytesIO()
    result_image.save(result_bytes, format="PNG")
    encoded_image = base64.b64encode(result_bytes.getvalue()).decode("utf-8")

    return {
        "success": True,
        "message": "Background removal processed",
        "data": {
            "image_base64": encoded_image,
            "background_removed": bg_removed
        },
        "error": processing_error
    }
