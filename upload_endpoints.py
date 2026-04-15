"""
File upload endpoints for JobMitra Backend.
Handles avatar/DP upload, retrieval, and deletion.
"""

import os
import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from auth_endpoints import get_current_user
from db_simple import db

router = APIRouter(tags=["File Upload"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "avatars")
ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/api/v1/users/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload or replace user avatar."""
    user_id = current_user["user_id"]

    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed.")

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image must be less than 5MB.")

    # Delete old avatar if exists
    user = await db.database["users"].find_one({"user_id": user_id})
    old_url = user.get("avatar_url") if user else None
    if old_url:
        old_filename = old_url.split("/")[-1]
        old_path = os.path.join(UPLOAD_DIR, old_filename)
        if os.path.exists(old_path):
            os.remove(old_path)

    # Save new file
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    # Store relative URL in DB
    avatar_url = f"/uploads/avatars/{filename}"
    await db.database["users"].update_one(
        {"user_id": user_id},
        {"$set": {"avatar_url": avatar_url, "updated_at": datetime.utcnow()}}
    )

    return {"avatar_url": avatar_url, "message": "Avatar uploaded successfully."}


@router.delete("/api/v1/users/avatar")
async def delete_avatar(current_user: dict = Depends(get_current_user)):
    """Remove user avatar."""
    user_id = current_user["user_id"]

    user = await db.database["users"].find_one({"user_id": user_id})
    avatar_url = user.get("avatar_url") if user else None

    if avatar_url:
        filename = avatar_url.split("/")[-1]
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    await db.database["users"].update_one(
        {"user_id": user_id},
        {"$set": {"avatar_url": None, "updated_at": datetime.utcnow()}}
    )

    return {"message": "Avatar removed successfully."}
