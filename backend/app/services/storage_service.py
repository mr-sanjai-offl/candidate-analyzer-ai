"""Supabase storage service.

Provides operations to interact with Supabase Storage buckets, ensuring
secure file uploads, downloads, and URL generation.
"""

import logging
from typing import Optional

from supabase import Client, create_client

from app.core.config import get_settings
from app.core.exceptions import InternalServerException, NotFoundException

logger = logging.getLogger(__name__)


class StorageService:
    """Service layer for interacting with Supabase Storage."""

    def __init__(self) -> None:
        settings = get_settings()
        try:
            self.client: Client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def _ensure_client(self) -> None:
        if not self.client:
            raise InternalServerException("Storage service is not configured properly.")

    def upload_file(self, bucket: str, path: str, file_bytes: bytes, content_type: str) -> str:
        """Upload a file to the specified Supabase Storage bucket."""
        self._ensure_client()
        try:
            res = self.client.storage.from_(bucket).upload(
                path=path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
            # Response contains path if successful
            return path
        except Exception as e:
            logger.error(f"Upload failed to bucket '{bucket}' at path '{path}': {e}")
            raise InternalServerException(f"Failed to upload file: {e}")

    def download_file(self, bucket: str, path: str) -> bytes:
        """Download a file from Supabase Storage."""
        self._ensure_client()
        try:
            res = self.client.storage.from_(bucket).download(path)
            return res
        except Exception as e:
            logger.error(f"Download failed for bucket '{bucket}' at path '{path}': {e}")
            raise NotFoundException("File not found in storage.")

    def delete_file(self, bucket: str, path: str) -> None:
        """Delete a file from Supabase Storage."""
        self._ensure_client()
        try:
            self.client.storage.from_(bucket).remove([path])
        except Exception as e:
            logger.error(f"Delete failed for bucket '{bucket}' at path '{path}': {e}")
            raise InternalServerException("Failed to delete file from storage.")

    def replace_file(self, bucket: str, path: str, file_bytes: bytes, content_type: str) -> str:
        """Update an existing file in Supabase Storage."""
        self._ensure_client()
        try:
            res = self.client.storage.from_(bucket).update(
                path=path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
            return path
        except Exception as e:
            logger.error(f"Replace failed for bucket '{bucket}' at path '{path}': {e}")
            raise InternalServerException("Failed to replace file.")

    def get_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        """Generate a time-limited signed URL for secure file access."""
        self._ensure_client()
        try:
            res = self.client.storage.from_(bucket).create_signed_url(path, expires_in)
            if res and "signedURL" in res:
                return res["signedURL"]
            raise ValueError("No signedURL in response")
        except Exception as e:
            logger.error(f"Failed to generate signed URL for bucket '{bucket}' at path '{path}': {e}")
            raise InternalServerException("Failed to generate secure URL.")

    def get_public_url(self, bucket: str, path: str) -> str:
        """Generate a public URL for a file (only use for public buckets)."""
        self._ensure_client()
        try:
            return self.client.storage.from_(bucket).get_public_url(path)
        except Exception as e:
            logger.error(f"Failed to get public URL for bucket '{bucket}' at path '{path}': {e}")
            raise InternalServerException("Failed to get public URL.")

    def get_metadata(self, bucket: str, path: str) -> dict:
        """Retrieve file metadata from storage (if supported/needed)."""
        # The Supabase python client doesn't have a direct get_metadata for a single file.
        # However, we can list files in the directory to find it.
        self._ensure_client()
        try:
            folder = "/".join(path.split("/")[:-1])
            filename = path.split("/")[-1]
            files = self.client.storage.from_(bucket).list(folder)
            for file_meta in files:
                if file_meta.get("name") == filename:
                    return file_meta
            raise NotFoundException("File metadata not found.")
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to get metadata for bucket '{bucket}' at path '{path}': {e}")
            raise InternalServerException("Failed to retrieve file metadata.")
