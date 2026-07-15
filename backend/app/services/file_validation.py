"""File validation service.

Provides validation for uploaded files, including size limits, MIME type
checking, and detection of malicious or malformed content.
"""

import logging
import os
import re
from typing import BinaryIO

import magic

from app.core.exceptions import BadRequestException

logger = logging.getLogger(__name__)

# Constants
MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/png",
    "image/jpeg",
}
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
ARCHIVE_MIMES = {"application/zip", "application/x-rar-compressed", "application/x-tar", "application/gzip"}
SCRIPT_MIMES = {"application/x-sh", "application/javascript", "text/x-python", "application/x-executable"}

class FileValidationService:
    """Service for securely validating uploaded files."""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal and invalid characters."""
        # Remove path information
        basename = os.path.basename(filename)
        # Keep only alphanumeric characters, dots, dashes, and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9.\-_]', '_', basename)
        return sanitized

    @staticmethod
    def validate_size(size: int, max_size: int = MAX_RESUME_SIZE_BYTES) -> None:
        """Validate file size does not exceed maximum."""
        if size > max_size:
            logger.warning(f"File size {size} exceeds max size {max_size}")
            raise BadRequestException("File size exceeds the maximum allowed limit.")

    @staticmethod
    def validate_content(file_bytes: bytes, filename: str) -> str:
        """Deep validate file content using libmagic and extension matching.
        
        Args:
            file_bytes: The raw bytes of the file.
            filename: The original filename.
            
        Returns:
            The detected MIME type.
            
        Raises:
            BadRequestException: If the file is invalid or potentially malicious.
        """
        # Validate extension first
        _, ext = os.path.splitext(filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            raise BadRequestException(f"File extension {ext} is not allowed.")

        # Validate actual MIME type using magic
        try:
            detected_mime = magic.from_buffer(file_bytes, mime=True)
        except Exception as e:
            logger.error(f"Error detecting MIME type: {e}")
            raise BadRequestException("Unable to read file content.")

        if detected_mime not in ALLOWED_MIME_TYPES:
            # Check if it's an explicitly rejected type for better error messages
            if detected_mime in ARCHIVE_MIMES:
                raise BadRequestException("Archives are not allowed.")
            if detected_mime in SCRIPT_MIMES or "executable" in detected_mime:
                raise BadRequestException("Executable files and scripts are not allowed.")
            
            raise BadRequestException(f"File type {detected_mime} is not allowed.")

        # Additional checks for PDFs
        if detected_mime == "application/pdf":
            # Very basic sanity check for PDF header
            if not file_bytes.startswith(b"%PDF-"):
                raise BadRequestException("Malformed PDF file detected.")
            # Note: Checking for encryption is typically done during parsing (e.g., PyMuPDF)
            # because parsing the PDF structure directly here is too complex.

        return detected_mime
