"""
Upload routes - image upload to Cloudinary with enhanced security.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.core.file_validation import (
    MAX_IMAGE_SIZE_BYTES,
    MAX_PROFILE_IMAGE_SIZE_BYTES,
    upload_rate_limiter,
    validate_image_upload,
)
from app.core.security import limiter
from app.services.cloudinary_service import (
    delete_product_image,
    extract_public_id,
    is_cloudinary_url,
    upload_product_image,
    upload_profile_image,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["uploads"])

MAX_IMAGES_PER_REQUEST = 5


@router.post("/product-image", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/hour")  # Rate limit: 20 uploads per hour
async def upload_single_product_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """
    Upload a single product image with comprehensive validation.

    Security features:
    - Filename sanitization
    - MIME type validation
    - File content validation (magic bytes)
    - Size limits (5MB)
    - Rate limiting (20/hour)

    Returns: { "url": str, "public_id": str }
    """
    # Check rate limit
    upload_rate_limiter.check_limit(current_user, max_uploads=20, window_seconds=3600)

    # Validate file
    content, sanitized_filename = await validate_image_upload(
        file, max_size=MAX_IMAGE_SIZE_BYTES, require_content_validation=True
    )

    # Create a new UploadFile with validated content
    from io import BytesIO
    from starlette.datastructures import Headers

    validated_file = UploadFile(
        filename=sanitized_filename,
        file=BytesIO(content),
        headers=Headers({"content-type": file.content_type or "image/jpeg"}),
    )

    # Upload to Cloudinary
    result = await upload_product_image(validated_file)

    logger.info(f"User {current_user} uploaded product image: {result['public_id']}")

    return result


@router.post("/product-images", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")  # Rate limit: 10 batch uploads per hour
async def upload_multiple_product_images(
    request: Request,
    files: List[UploadFile] = File(...),
    current_user: str = Depends(get_current_user),
):
    """
    Upload up to 5 product images in one request with validation.

    Security features:
    - Per-file validation
    - Batch size limits
    - Rate limiting (10 batch uploads/hour)

    Returns: { "urls": [str], "public_ids": [str] }
    """
    if len(files) > MAX_IMAGES_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_IMAGES_PER_REQUEST} images per upload.",
        )

    # Check rate limit (counts as multiple uploads)
    upload_rate_limiter.check_limit(current_user, max_uploads=20, window_seconds=3600)

    urls = []
    public_ids = []

    for idx, file in enumerate(files):
        try:
            # Validate each file
            content, sanitized_filename = await validate_image_upload(
                file, max_size=MAX_IMAGE_SIZE_BYTES, require_content_validation=True
            )

            # Create validated UploadFile
            from io import BytesIO
            from starlette.datastructures import Headers

            validated_file = UploadFile(
                filename=sanitized_filename,
                file=BytesIO(content),
                headers=Headers({"content-type": file.content_type or "image/jpeg"}),
            )

            # Upload to Cloudinary
            result = await upload_product_image(validated_file)
            urls.append(result["url"])
            public_ids.append(result["public_id"])

        except HTTPException as e:
            # If any file fails, log and continue or fail entire batch
            logger.error(f"File {idx} validation failed: {e.detail}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {idx + 1} validation failed: {e.detail}",
            )

    logger.info(f"User {current_user} uploaded {len(files)} product images: {public_ids}")

    return {"urls": urls, "public_ids": public_ids}


@router.post("/profile-image", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")  # Rate limit: 10 profile uploads per hour
async def upload_profile_image_endpoint(
    request: Request,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """
    Upload a profile image with validation and automatic old image deletion.

    Security features:
    - Stricter size limit (2MB for profiles)
    - Content validation
    - Rate limiting (10/hour)
    - Automatic cleanup of old images

    This endpoint:
    1. Validates the uploaded file
    2. Fetches the user's current avatar from Firestore
    3. Uploads the new profile image to Cloudinary
    4. Deletes the old profile image from Cloudinary (if it exists)
    5. Returns the new image URL

    Returns: { "url": str, "public_id": str, "old_image_deleted": bool }
    """
    # Check rate limit
    upload_rate_limiter.check_limit(current_user, max_uploads=10, window_seconds=3600)

    # Validate file with stricter size limit for profiles
    content, sanitized_filename = await validate_image_upload(
        file, max_size=MAX_PROFILE_IMAGE_SIZE_BYTES, require_content_validation=True
    )

    db = get_db()

    # Get user's current avatar
    user_doc = db.collection("users").document(current_user).get()
    old_avatar = None
    old_image_deleted = False

    if user_doc.exists:
        user_data = user_doc.to_dict()
        old_avatar = user_data.get("avatar")

    # Create validated UploadFile
    from io import BytesIO
    from starlette.datastructures import Headers

    validated_file = UploadFile(
        filename=sanitized_filename,
        file=BytesIO(content),
        headers=Headers({"content-type": file.content_type or "image/jpeg"}),
    )

    # Upload new profile image
    logger.info(f"Uploading new profile image for user {current_user}")
    result = await upload_profile_image(validated_file)

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

    logger.info(f"User {current_user} uploaded profile image: {result['public_id']}")

    return {
        "url": result["url"],
        "public_id": result["public_id"],
        "old_image_deleted": old_image_deleted,
    }
