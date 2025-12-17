"""
FAZA 59.5 — IntegrityHasher with Real Cryptographic Hashing
------------------------------------------------------------
Cryptographic integrity verification using SHA-256.
"""

import hashlib
from pathlib import Path
from typing import Optional


class IntegrityHasher:
    """
    Cryptographic integrity hasher using SHA-256.
    Provides deterministic, auditable hashing for files and text.
    """

    ALGORITHM = "sha256"
    BUFFER_SIZE = 65536  # 64KB chunks for file reading

    def compute_file_hash(self, path: str) -> str:
        """
        Compute SHA-256 hash of a file.

        Args:
            path: Absolute path to file

        Returns:
            Hexadecimal SHA-256 hash string

        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be read
        """
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Cannot hash non-existent file: {path}")

        if not file_path.is_file():
            raise ValueError(f"Cannot hash directory: {path}")

        hasher = hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.BUFFER_SIZE)
                    if not chunk:
                        break
                    hasher.update(chunk)
        except PermissionError as e:
            raise PermissionError(f"Cannot read file for hashing: {path}") from e

        return hasher.hexdigest()

    def compute_text_hash(self, text: str) -> str:
        """
        Compute SHA-256 hash of text string.

        Args:
            text: Text to hash

        Returns:
            Hexadecimal SHA-256 hash string
        """
        hasher = hashlib.sha256()
        hasher.update(text.encode('utf-8'))
        return hasher.hexdigest()

    def verify_file_hash(self, path: str, expected_hash: str) -> bool:
        """
        Verify file hash matches expected value.

        Args:
            path: Absolute path to file
            expected_hash: Expected SHA-256 hash (hexadecimal)

        Returns:
            True if hash matches, False otherwise
        """
        try:
            actual_hash = self.compute_file_hash(path)
            return actual_hash == expected_hash.lower()
        except (FileNotFoundError, PermissionError, ValueError):
            return False
