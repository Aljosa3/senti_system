"""
Working Memory - FAZA 12
Location: senti_core_module/senti_memory/working_memory.py

Short-term, volatile memory with TTL expiration.
- Clears on system restart
- Automatic expiration (default: 3 minutes)
- Thread-safe operations
"""

import threading
import time
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class WorkingMemory:
    """
    Short-term memory with automatic expiration.
    Not persisted to disk - volatile memory only.
    """

    def __init__(self, default_ttl_seconds: int = 180):
        """
        Initialize working memory.

        Args:
            default_ttl_seconds: Default time-to-live in seconds (default: 180 = 3 minutes)
        """
        self.default_ttl = default_ttl_seconds
        self.memory: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    # =====================================================
    # CORE OPERATIONS
    # =====================================================

    def add(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Add item to working memory.

        Args:
            key: Memory key
            value: Value to store
            ttl_seconds: Optional custom TTL (uses default if None)

        Returns:
            Success status
        """
        with self.lock:
            try:
                ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
                expiry_time = datetime.now() + timedelta(seconds=ttl)

                self.memory[key] = {
                    "value": value,
                    "created_at": datetime.now().isoformat(),
                    "expires_at": expiry_time.isoformat(),
                    "ttl_seconds": ttl
                }
                return True
            except Exception as e:
                print(f"[WorkingMemory] Failed to add item: {e}")
                return False

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from working memory.
        Returns None if expired or not found.

        Args:
            key: Memory key

        Returns:
            Stored value or None
        """
        with self.lock:
            if key not in self.memory:
                return None

            item = self.memory[key]
            expires_at = datetime.fromisoformat(item["expires_at"])

            # Check if expired
            if datetime.now() > expires_at:
                del self.memory[key]
                return None

            return item["value"]

    def remove(self, key: str) -> bool:
        """
        Remove item from working memory.

        Args:
            key: Memory key

        Returns:
            True if removed, False if not found
        """
        with self.lock:
            if key in self.memory:
                del self.memory[key]
                return True
            return False

    def update(self, key: str, value: Any) -> bool:
        """
        Update existing item (preserves TTL).

        Args:
            key: Memory key
            value: New value

        Returns:
            True if updated, False if not found
        """
        with self.lock:
            if key not in self.memory:
                return False

            # Preserve expiry time
            self.memory[key]["value"] = value
            return True

    # =====================================================
    # CLEANUP & MANAGEMENT
    # =====================================================

    def cleanup_expired(self) -> int:
        """
        Remove all expired items.

        Returns:
            Number of items removed
        """
        with self.lock:
            now = datetime.now()
            expired_keys = []

            for key, item in self.memory.items():
                expires_at = datetime.fromisoformat(item["expires_at"])
                if now > expires_at:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.memory[key]

            return len(expired_keys)

    def clear(self) -> int:
        """
        Clear all working memory.

        Returns:
            Number of items cleared
        """
        with self.lock:
            count = len(self.memory)
            self.memory.clear()
            return count

    # =====================================================
    # QUERY & INSPECTION
    # =====================================================

    def exists(self, key: str) -> bool:
        """
        Check if key exists and is not expired.

        Args:
            key: Memory key

        Returns:
            True if exists and valid
        """
        return self.get(key) is not None

    def get_all_keys(self) -> list:
        """
        Get all valid (non-expired) keys.

        Returns:
            List of keys
        """
        with self.lock:
            now = datetime.now()
            valid_keys = []

            for key, item in self.memory.items():
                expires_at = datetime.fromisoformat(item["expires_at"])
                if now <= expires_at:
                    valid_keys.append(key)

            return valid_keys

    def get_stats(self) -> Dict[str, Any]:
        """
        Get working memory statistics.

        Returns:
            Stats dictionary
        """
        with self.lock:
            now = datetime.now()
            valid_count = 0
            expired_count = 0

            for item in self.memory.values():
                expires_at = datetime.fromisoformat(item["expires_at"])
                if now <= expires_at:
                    valid_count += 1
                else:
                    expired_count += 1

            return {
                "total_items": len(self.memory),
                "valid_items": valid_count,
                "expired_items": expired_count,
                "default_ttl_seconds": self.default_ttl
            }

    def get_item_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an item.

        Args:
            key: Memory key

        Returns:
            Item info dictionary or None
        """
        with self.lock:
            if key not in self.memory:
                return None

            item = self.memory[key]
            expires_at = datetime.fromisoformat(item["expires_at"])
            now = datetime.now()

            return {
                "key": key,
                "created_at": item["created_at"],
                "expires_at": item["expires_at"],
                "ttl_seconds": item["ttl_seconds"],
                "is_expired": now > expires_at,
                "has_value": True
            }
