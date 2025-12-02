"""
FAZA 21 - Persistence Manager

Unified high-level API for persistent storage with encryption,
snapshots, and automatic save-on-change functionality.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import threading


class PersistenceManager:
    """
    Unified persistence manager for SENTI OS.

    Provides high-level API for encrypted persistent storage with:
    - Load-on-boot
    - Save-on-change
    - Auto-snapshot
    - File locking
    - Rollback safety
    - Audit logging
    """

    def __init__(
        self,
        master_key_manager,
        encrypted_storage,
        storage_backend,
        snapshot_engine,
        secrets_manager
    ):
        """Initialize persistence manager with all components."""
        self.master_key_manager = master_key_manager
        self.encrypted_storage = encrypted_storage
        self.storage_backend = storage_backend
        self.snapshot_engine = snapshot_engine
        self.secrets_manager = secrets_manager

        self._data_cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._initialized = False
        self._audit_log: List[Dict] = []

    def initialize(self, passphrase: Optional[str] = None) -> bool:
        """
        Initialize persistence layer.

        Args:
            passphrase: Optional passphrase for key derivation.

        Returns:
            True if initialized successfully.
        """
        try:
            # Initialize master key
            if not self.master_key_manager.is_initialized():
                self.master_key_manager.bootstrap_key(passphrase)

            # Load all data from disk
            self._load_all_data()

            self._initialized = True
            self._log_audit("persistence_initialized", {"success": True})

            return True
        except Exception as e:
            self._log_audit("persistence_init_failed", {"error": str(e)})
            return False

    def save(self, category: str, data: Any) -> bool:
        """
        Save data to encrypted storage.

        Args:
            category: Data category (devices, permissions, sessions, etc.).
            data: Data to save.

        Returns:
            True if saved successfully.
        """
        if not self._initialized:
            return False

        with self._lock:
            try:
                filename = self._get_filename(category)

                # Update cache
                self._data_cache[category] = data

                # Prepare data with metadata
                save_data = {
                    "schema_version": "1.0",
                    "last_updated": datetime.utcnow().isoformat(),
                    "data": data
                }

                # Encrypt
                encrypted = self.encrypted_storage.encrypt(save_data)

                # Write to disk
                success = self.storage_backend.write(filename, encrypted)

                if success:
                    self._log_audit("data_saved", {
                        "category": category,
                        "filename": filename
                    })

                return success
            except Exception as e:
                self._log_audit("save_failed", {
                    "category": category,
                    "error": str(e)
                })
                return False

    def load(self, category: str) -> Optional[Any]:
        """
        Load data from encrypted storage.

        Args:
            category: Data category to load.

        Returns:
            Loaded data, or None if not found.
        """
        if not self._initialized:
            return None

        with self._lock:
            # Check cache first
            if category in self._data_cache:
                return self._data_cache[category]

            try:
                filename = self._get_filename(category)

                # Read from disk
                encrypted = self.storage_backend.read(filename)
                if not encrypted:
                    return None

                # Decrypt
                loaded_data = self.encrypted_storage.decrypt(encrypted)

                # Extract data
                data = loaded_data.get("data")

                # Update cache
                self._data_cache[category] = data

                self._log_audit("data_loaded", {
                    "category": category,
                    "filename": filename
                })

                return data
            except Exception as e:
                self._log_audit("load_failed", {
                    "category": category,
                    "error": str(e)
                })
                return None

    def delete(self, category: str) -> bool:
        """Delete data category."""
        if not self._initialized:
            return False

        with self._lock:
            try:
                filename = self._get_filename(category)

                # Remove from cache
                if category in self._data_cache:
                    del self._data_cache[category]

                # Delete file
                success = self.storage_backend.delete(filename)

                if success:
                    self._log_audit("data_deleted", {"category": category})

                return success
            except Exception:
                return False

    def create_snapshot(self, snapshot_type: str = "manual") -> Optional[str]:
        """Create a snapshot of current state."""
        if not self._initialized:
            return None

        snapshot_id = self.snapshot_engine.create_snapshot(snapshot_type)

        if snapshot_id:
            self._log_audit("snapshot_created", {
                "snapshot_id": snapshot_id,
                "type": snapshot_type
            })

        return snapshot_id

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore from a snapshot."""
        if not self._initialized:
            return False

        success = self.snapshot_engine.restore_snapshot(snapshot_id)

        if success:
            # Clear cache and reload
            self._data_cache.clear()
            self._load_all_data()

            self._log_audit("snapshot_restored", {"snapshot_id": snapshot_id})

        return success

    def list_snapshots(self) -> List:
        """List all available snapshots."""
        if not self._initialized:
            return []

        return self.snapshot_engine.list_snapshots()

    def get_status(self) -> Dict[str, Any]:
        """Get persistence layer status."""
        return {
            "initialized": self._initialized,
            "master_key_initialized": self.master_key_manager.is_initialized(),
            "cached_categories": list(self._data_cache.keys()),
            "storage_files": self.storage_backend.list_files(),
            "snapshot_count": len(self.snapshot_engine.list_snapshots()),
            "audit_log_entries": len(self._audit_log)
        }

    def export_data(self, category: str) -> Optional[Dict]:
        """Export data (for backup/migration)."""
        data = self.load(category)
        if data is None:
            return None

        return {
            "category": category,
            "exported_at": datetime.utcnow().isoformat(),
            "data": data
        }

    def import_data(self, category: str, data: Any) -> bool:
        """Import data (from backup/migration)."""
        return self.save(category, data)

    def verify_integrity(self, category: str) -> bool:
        """Verify data integrity."""
        try:
            filename = self._get_filename(category)
            encrypted = self.storage_backend.read(filename)

            if not encrypted:
                return False

            return self.encrypted_storage.verify_integrity(encrypted)
        except Exception:
            return False

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get audit log entries."""
        return self._audit_log[-limit:]

    def _load_all_data(self):
        """Load all data categories on boot."""
        categories = [
            "devices",
            "permissions",
            "sessions",
            "settings",
            "orch_history",
            "oauth_tokens",
            "platform_sessions"
        ]

        for category in categories:
            self.load(category)

    def _get_filename(self, category: str) -> str:
        """Get filename for category."""
        return f"{category}.json"

    def _log_audit(self, operation: str, details: Dict):
        """Log audit entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "details": details
        }
        self._audit_log.append(entry)

        # Keep last 1000 entries
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-1000:]


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "persistence_manager",
        "faza": "21",
        "version": "1.0.0",
        "description": "Unified encrypted persistent storage manager",
        "stores_passwords": "false",
        "stores_biometrics": "false",
        "encryption": "simulated_aes256_gcm"
    }
