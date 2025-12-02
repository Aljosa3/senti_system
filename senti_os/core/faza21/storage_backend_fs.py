"""
FAZA 21 - Filesystem Storage Backend

Local filesystem backend with atomic writes and safe directory management.

Author: SENTI OS Core Team
License: Proprietary
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime


class StorageBackendFS:
    """
    Filesystem-based storage backend.

    Provides atomic writes via temporary files and safe file operations.
    """

    def __init__(self, storage_dir: str = "/home/pisarna/senti_system/data/faza21"):
        """
        Initialize filesystem storage backend.

        Args:
            storage_dir: Directory for persistent storage.
        """
        self.storage_dir = Path(storage_dir)
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def write(self, filename: str, data: bytes) -> bool:
        """
        Write data to file atomically.

        Uses temporary file and atomic rename for safety.

        Args:
            filename: Target filename.
            data: Data bytes to write.

        Returns:
            True if write successful.
        """
        try:
            file_path = self.storage_dir / filename
            temp_path = self.storage_dir / f".{filename}.tmp"

            # Write to temporary file
            with open(temp_path, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())

            # Atomic rename
            temp_path.replace(file_path)

            return True
        except Exception as e:
            # Clean up temp file if exists
            if temp_path.exists():
                temp_path.unlink()
            return False

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read data from file.

        Args:
            filename: Filename to read.

        Returns:
            File data bytes, or None if not found.
        """
        try:
            file_path = self.storage_dir / filename
            if not file_path.exists():
                return None

            with open(file_path, 'rb') as f:
                return f.read()
        except Exception:
            return None

    def exists(self, filename: str) -> bool:
        """Check if file exists."""
        return (self.storage_dir / filename).exists()

    def delete(self, filename: str) -> bool:
        """Delete file."""
        try:
            file_path = self.storage_dir / filename
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception:
            return False

    def list_files(self) -> list:
        """List all files in storage directory."""
        try:
            return [f.name for f in self.storage_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
        except Exception:
            return []

    def get_file_size(self, filename: str) -> Optional[int]:
        """Get file size in bytes."""
        try:
            file_path = self.storage_dir / filename
            if file_path.exists():
                return file_path.stat().st_size
            return None
        except Exception:
            return None

    def get_modified_time(self, filename: str) -> Optional[datetime]:
        """Get file modification time."""
        try:
            file_path = self.storage_dir / filename
            if file_path.exists():
                timestamp = file_path.stat().st_mtime
                return datetime.fromtimestamp(timestamp)
            return None
        except Exception:
            return None


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "storage_backend_fs",
        "faza": "21",
        "version": "1.0.0",
        "description": "Filesystem storage backend with atomic writes"
    }
