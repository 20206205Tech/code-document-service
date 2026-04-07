import mimetypes
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, UploadFile, status
from loguru import logger

import env


class FileValidationError(Exception):
    """Custom exception for file validation errors"""


def validate_file_extension(filename: str) -> str:
    """
    Validate file extension against allowed extensions

    Args:
        filename: Name of the file to validate

    Returns:
        Lowercase file extension

    Raises:
        FileValidationError: If extension is not allowed
    """
    file_path = Path(filename)
    extension = file_path.suffix.lower()

    if not extension:
        raise FileValidationError("File must have an extension")

    if extension not in env.ALLOWED_FILE_EXTENSIONS:
        raise FileValidationError(
            f"File extension '{extension}' is not allowed. "
            f"Allowed extensions: {', '.join(env.ALLOWED_FILE_EXTENSIONS)}"
        )

    return extension


def validate_file_size(file: UploadFile, max_size: int = env.MAX_FILE_SIZE) -> None:
    """
    Validate file size

    Args:
        file: Uploaded file object
        max_size: Maximum allowed file size in bytes

    Raises:
        FileValidationError: If file is too large
    """
    # Try to get file size from headers first
    file.file.seek(0, 2)  # Seek to end of file
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer

    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        file_size_mb = file_size / (1024 * 1024)
        raise FileValidationError(
            f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb:.2f}MB)"
        )


def validate_upload_file(file: UploadFile) -> Tuple[str, str]:
    """
    Comprehensive validation for uploaded files

    Args:
        file: FastAPI UploadFile object

    Returns:
        Tuple of (filename, file_extension)

    Raises:
        HTTPException: If validation fails
    """
    try:
        # Validate filename exists
        if not file.filename:
            raise FileValidationError("Filename is required")

        # Validate extension
        extension = validate_file_extension(file.filename)

        # Validate file size
        validate_file_size(file)

        logger.info(f"✅ File validation passed: {file.filename} ({extension})")
        return file.filename, extension

    except FileValidationError as e:
        logger.error(f"❌ File validation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def get_content_type(filename: str) -> str:
    """
    Get MIME content type for a filename

    Args:
        filename: Name of the file

    Returns:
        MIME type string
    """
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"
