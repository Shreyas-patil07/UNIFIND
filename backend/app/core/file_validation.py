"""
Comprehensive file validation for secure uploads.
Validates MIME types, file content (magic bytes), size, and filenames.
"""

import logging
import re

try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

# File type configurations
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Magic bytes for image validation
IMAGE_MAGIC_BYTES = {
    b"\xFF\xD8\xFF": "image/jpeg",  # JPEG
    b"\x89PNG\r\n\x1a\n": "image/png",  # PNG
    b"RIFF": "image/webp",  # WebP (needs additional check)
}

# File size limits
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_PROFILE_IMAGE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB

# Filename validation
SAFE_FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]+$")
MAX_FILENAME_LENGTH = 255


class FileValidationError(HTTPException):
    """Custom exception for file validation failures."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename

    Raises:
        FileValidationError: If filename is invalid
    """
    if not filename:
        raise FileValidationError("Filename cannot be empty")

    # Remove path components
    filename = filename.split("/")[-1].split("\\")[-1]

    # Remove any null bytes
    filename = filename.replace("\x00", "")

    # Check length
    if len(filename) > MAX_FILENAME_LENGTH:
        raise FileValidationError(f"Filename too long (max {MAX_FILENAME_LENGTH} characters)")

    # Validate characters
    if not SAFE_FILENAME_PATTERN.match(filename):
        # Replace unsafe characters with underscores
        filename = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)
        logger.info(f"Sanitized filename to: {filename}")

    # Prevent hidden files
    if filename.startswith("."):
        filename = "_" + filename[1:]

    # Ensure there's an extension
    if "." not in filename:
        raise FileValidationError("Filename must have an extension")

    return filename


def validate_image_extension(filename: str) -> str:
    """
    Validate image file extension.

    Args:
        filename: Filename to validate

    Returns:
        str: Lowercase extension (e.g., '.jpg')

    Raises:
        FileValidationError: If extension is not allowed
    """
    filename_lower = filename.lower()
    extension = None

    for ext in ALLOWED_IMAGE_EXTENSIONS:
        if filename_lower.endswith(ext):
            extension = ext
            break

    if not extension:
        allowed = ", ".join(ALLOWED_IMAGE_EXTENSIONS)
        raise FileValidationError(f"Invalid file extension. Allowed: {allowed}")

    return extension


def detect_mime_type_from_content(content: bytes) -> Optional[str]:
    """
    Detect MIME type from file content using magic bytes.

    Args:
        content: File content bytes

    Returns:
        Optional[str]: Detected MIME type or None
    """
    # Check magic bytes
    for magic_bytes, mime_type in IMAGE_MAGIC_BYTES.items():
        if content.startswith(magic_bytes):
            # Special handling for WebP
            if mime_type == "image/webp":
                # WebP files start with RIFF and contain WEBP
                if len(content) >= 12 and content[8:12] == b"WEBP":
                    return mime_type
            else:
                return mime_type

    # Fallback to python-magic if available
    if MAGIC_AVAILABLE and magic:
        try:
            mime = magic.Magic(mime=True)
            detected_mime = mime.from_buffer(content[:2048])  # Check first 2KB
            return detected_mime
        except Exception as e:
            logger.warning(f"python-magic detection failed: {e}")
            return None

    return None


def validate_image_content(content: bytes, declared_mime: str) -> None:
    """
    Validate image content matches declared MIME type.

    Args:
        content: File content bytes
        declared_mime: MIME type from Content-Type header

    Raises:
        FileValidationError: If content doesn't match declared type
    """
    detected_mime = detect_mime_type_from_content(content)

    if not detected_mime:
        logger.warning("Could not detect MIME type from content")
        return  # Allow if detection fails (fallback to MIME type check)

    # Normalize MIME types for comparison
    detected_mime = detected_mime.lower()
    declared_mime = declared_mime.lower()

    # Handle JPEG variations
    if detected_mime in ["image/jpeg", "image/jpg"]:
        detected_mime = "image/jpeg"
    if declared_mime in ["image/jpeg", "image/jpg"]:
        declared_mime = "image/jpeg"

    if detected_mime != declared_mime:
        logger.warning(
            f"MIME type mismatch: declared={declared_mime}, " f"detected={detected_mime}"
        )
        raise FileValidationError(
            f"File content does not match declared type. "
            f"Expected {declared_mime}, detected {detected_mime}"
        )


async def validate_image_upload(
    file: UploadFile, max_size: int = MAX_IMAGE_SIZE_BYTES, require_content_validation: bool = True
) -> Tuple[bytes, str]:
    """
    Comprehensive image upload validation.

    Validates:
    - Filename safety
    - File extension
    - MIME type
    - File size
    - Content (magic bytes)

    Args:
        file: Uploaded file
        max_size: Maximum file size in bytes
        require_content_validation: If True, validate file content

    Returns:
        Tuple[bytes, str]: (file_content, sanitized_filename)

    Raises:
        FileValidationError: If validation fails
    """
    # Validate filename
    if not file.filename:
        raise FileValidationError("No filename provided")

    sanitized_name = sanitize_filename(file.filename)
    extension = validate_image_extension(sanitized_name)

    # Validate MIME type
    if not file.content_type:
        raise FileValidationError("No content type provided")

    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        allowed = ", ".join(ALLOWED_IMAGE_MIME_TYPES)
        raise FileValidationError(f"Invalid content type '{file.content_type}'. Allowed: {allowed}")

    # Read and validate size
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise FileValidationError("Failed to read uploaded file")

    if len(content) == 0:
        raise FileValidationError("Uploaded file is empty")

    if len(content) > max_size:
        size_mb = len(content) / 1024 / 1024
        max_mb = max_size / 1024 / 1024
        raise FileValidationError(f"File too large: {size_mb:.1f}MB (max {max_mb:.0f}MB)")

    # Validate content matches declared MIME type
    if require_content_validation:
        validate_image_content(content, file.content_type)

    logger.info(
        f"File validation passed: {sanitized_name} " f"({len(content)} bytes, {file.content_type})"
    )

    return content, sanitized_name


def validate_image_dimensions(
    content: bytes,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    min_width: Optional[int] = None,
    min_height: Optional[int] = None,
) -> Tuple[int, int]:
    """
    Validate image dimensions using PIL/Pillow.

    Args:
        content: Image file content
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        min_width: Minimum width in pixels
        min_height: Minimum height in pixels

    Returns:
        Tuple[int, int]: (width, height)

    Raises:
        FileValidationError: If dimensions are invalid
    """
    try:
        import io

        from PIL import Image

        image = Image.open(io.BytesIO(content))
        width, height = image.size

        if max_width and width > max_width:
            raise FileValidationError(f"Image width {width}px exceeds maximum {max_width}px")

        if max_height and height > max_height:
            raise FileValidationError(f"Image height {height}px exceeds maximum {max_height}px")

        if min_width and width < min_width:
            raise FileValidationError(f"Image width {width}px below minimum {min_width}px")

        if min_height and height < min_height:
            raise FileValidationError(f"Image height {height}px below minimum {min_height}px")

        return width, height

    except ImportError:
        logger.warning("PIL/Pillow not available, skipping dimension validation")
        return (0, 0)
    except FileValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to validate image dimensions: {e}")
        raise FileValidationError("Invalid image file")


# ==================== RATE LIMITING HELPERS ====================


class UploadRateLimiter:
    """
    Simple in-memory rate limiter for uploads.
    For production, use Redis-based rate limiting.
    """

    def __init__(self):
        self._upload_counts: dict = {}  # user_id -> (count, reset_time)

    def check_limit(self, user_id: str, max_uploads: int = 20, window_seconds: int = 3600) -> None:
        """
        Check if user has exceeded upload rate limit.

        Args:
            user_id: User ID
            max_uploads: Maximum uploads per window
            window_seconds: Time window in seconds

        Raises:
            HTTPException: If rate limit exceeded
        """
        import time

        current_time = time.time()

        if user_id in self._upload_counts:
            count, reset_time = self._upload_counts[user_id]

            # Reset if window expired
            if current_time >= reset_time:
                self._upload_counts[user_id] = (1, current_time + window_seconds)
                return

            # Check limit
            if count >= max_uploads:
                remaining_time = int(reset_time - current_time)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Upload limit exceeded. Try again in {remaining_time} seconds.",
                )

            # Increment count
            self._upload_counts[user_id] = (count + 1, reset_time)
        else:
            # First upload
            self._upload_counts[user_id] = (1, current_time + window_seconds)

    def cleanup_expired(self) -> None:
        """Remove expired entries (call periodically)."""
        import time

        current_time = time.time()

        expired_users = [
            user_id
            for user_id, (_, reset_time) in self._upload_counts.items()
            if current_time >= reset_time
        ]

        for user_id in expired_users:
            del self._upload_counts[user_id]


# Global rate limiter instance
upload_rate_limiter = UploadRateLimiter()
