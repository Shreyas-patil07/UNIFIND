"""
Upload routes - image upload to Cloudinary.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List

from app.api.dependencies.auth import get_current_user
from app.services.cloudinary_service import (
    upload_product_image,
    upload_profile_image,
    extract_public_id,
    delete_product_image,
    is_cloudinary_url
)
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["uploads"])

MAX_IMAGES_PER_REQUEST = 5


@router.post("/product-image", status_code=status.HTTP_201_CREATED)
async def upload_single_product_image(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """
    Upload a single product image.
    Returns: { "url": str, "public_id": str }
    """
    result = await upload_product_image(file)
    return result


@router.post("/product-images", status_code=status.HTTP_201_CREATED)
async def upload_multiple_product_images(
    files: List[UploadFile] = File(...),
    current_user: str = Depends(get_current_user)
):
    """
    Upload up to 5 product images in one request.
    Returns: { "urls": [str], "public_ids": [str] }
    """
    if len(files) > MAX_IMAGES_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_IMAGES_PER_REQUEST} images per upload."
        )
    
    urls = []
    public_ids = []
    
    for file in files:
        result = await upload_product_image(file)
        urls.append(result["url"])
        public_ids.append(result["public_id"])
    
    return {"urls": urls, "public_ids": public_ids}


@router.post("/profile-image", status_code=status.HTTP_201_CREATED)
async def upload_profile_image_endpoint(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """
    Upload a profile image and automatically delete the old one.
    
    This endpoint:
    1. Fetches the user's current avatar from Firestore
    2. Uploads the new profile image to Cloudinary
    3. Deletes the old profile image from Cloudinary (if it exists)
    4. Returns the new image URL
    
    Returns: { "url": str, "public_id": str, "old_image_deleted": bool }
    """
    db = get_db()
    
    # Get user's current avatar
    user_doc = db.collection('users').document(current_user).get()
    old_avatar = None
    old_image_deleted = False
    
    if user_doc.exists:
        user_data = user_doc.to_dict()
        old_avatar = user_data.get('avatar')
    
    # Upload new profile image
    logger.info(f"Uploading new profile image for user {current_user}")
    result = await upload_profile_image(file)
    
    # Delete old profile image if it exists and is a Cloudinary URL
    if old_avatar and is_cloudinary_url(old_avatar):
        logger.info(f"Deleting old profile image for user {current_user}: {old_avatar}")
        public_id = extract_public_id(old_avatar)
        if public_id:
            try:
                delete_product_image(public_id)
                old_image_deleted = True
                logger.info(f"Successfully deleted old profile image: {public_id}")
            except Exception as e:
                logger.warning(f"Failed to delete old profile image {public_id}: {e}")
                # Don't fail the request if deletion fails
    
    return {
        "url": result["url"],
        "public_id": result["public_id"],
        "old_image_deleted": old_image_deleted
    }
