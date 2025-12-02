"""
FAZA 21 - Persistence Layer

Secure encrypted persistent storage for SENTI OS with GDPR/ZVOP/EU AI Act compliance.

CRITICAL SECURITY GUARANTEE:
    - NO password storage
    - NO biometric data storage
    - All data encrypted at rest (simulated AES256-GCM)
    - Full audit trail
    - Snapshot and rollback support

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict, Optional, Any

# Import all components
from senti_os.core.faza21.master_key_manager import MasterKeyManager
from senti_os.core.faza21.encrypted_storage import EncryptedStorage
from senti_os.core.faza21.storage_backend_fs import StorageBackendFS
from senti_os.core.faza21.storage_schemas import StorageSchemas
from senti_os.core.faza21.secrets_manager import SecretsManager, Secret
from senti_os.core.faza21.snapshot_engine import SnapshotEngine, Snapshot
from senti_os.core.faza21.persistence_manager import PersistenceManager


# Module exports
__all__ = [
    "FAZA21Stack",
    "MasterKeyManager",
    "EncryptedStorage",
    "StorageBackendFS",
    "StorageSchemas",
    "SecretsManager",
    "Secret",
    "SnapshotEngine",
    "Snapshot",
    "PersistenceManager",
    "get_info"
]


class FAZA21Stack:
    """
    Complete FAZA 21 persistence layer stack.

    Provides unified interface for encrypted persistent storage.
    """

    def __init__(self, storage_dir: str = "/home/pisarna/senti_system/data/faza21"):
        """
        Initialize complete FAZA 21 stack.

        Args:
            storage_dir: Directory for persistent storage.
        """
        # Initialize components
        self.master_key_manager = MasterKeyManager()
        self.storage_backend = StorageBackendFS(storage_dir)
        self.encrypted_storage = EncryptedStorage(self.master_key_manager)
        self.snapshot_engine = SnapshotEngine(self.storage_backend)
        self.secrets_manager = SecretsManager(
            self.encrypted_storage,
            self.storage_backend
        )
        self.persistence_manager = PersistenceManager(
            self.master_key_manager,
            self.encrypted_storage,
            self.storage_backend,
            self.snapshot_engine,
            self.secrets_manager
        )

    def initialize(self, passphrase: Optional[str] = None) -> bool:
        """
        Initialize persistence layer.

        Args:
            passphrase: Optional passphrase for master key derivation.

        Returns:
            True if initialized successfully.
        """
        return self.persistence_manager.initialize(passphrase)

    def save(self, category: str, data: Any) -> bool:
        """Save data to encrypted storage."""
        return self.persistence_manager.save(category, data)

    def load(self, category: str) -> Optional[Any]:
        """Load data from encrypted storage."""
        return self.persistence_manager.load(category)

    def create_snapshot(self, snapshot_type: str = "manual") -> Optional[str]:
        """Create storage snapshot."""
        return self.persistence_manager.create_snapshot(snapshot_type)

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore from snapshot."""
        return self.persistence_manager.restore_snapshot(snapshot_id)

    def store_secret(
        self,
        secret_id: str,
        secret_type: str,
        value: str,
        expires_in_hours: Optional[int] = None
    ) -> bool:
        """Store encrypted secret."""
        return self.secrets_manager.store_secret(
            secret_id,
            secret_type,
            value,
            expires_in_hours
        )

    def get_secret(self, secret_id: str) -> Optional[str]:
        """Retrieve secret."""
        return self.secrets_manager.get_secret(secret_id)

    def get_status(self) -> Dict[str, Any]:
        """Get stack status."""
        return self.persistence_manager.get_status()

    def shutdown(self):
        """Shutdown persistence layer and clear keys."""
        self.master_key_manager.clear_key()


def get_info() -> Dict[str, str]:
    """
    Get FAZA 21 module information.

    Returns:
        Dictionary with comprehensive module metadata.
    """
    return {
        "module": "faza21",
        "name": "Persistence Layer",
        "version": "1.0.0",
        "faza": "21",
        "description": "Secure encrypted persistent storage for SENTI OS",

        # Privacy Guarantees
        "privacy_compliant": "true",
        "gdpr_compliant": "true",
        "zvop_compliant": "true",
        "eu_ai_act_compliant": "true",

        # Critical Security Rules
        "stores_passwords": "false",
        "stores_biometrics": "false",
        "stores_raw_credentials": "false",

        # What it DOES store
        "stores_session_tokens": "true",
        "stores_oauth_tokens": "true",
        "stores_platform_sessions": "true",
        "stores_device_identities": "true",
        "stores_permissions": "true",
        "stores_settings": "true",

        # Security Features
        "encryption": "simulated_aes256_gcm",
        "key_derivation": "simulated_pbkdf2",
        "integrity_checks": "true",
        "tamper_detection": "true",
        "audit_logging": "true",

        # Capabilities
        "supports_snapshots": "true",
        "supports_rollback": "true",
        "supports_automatic_save": "true",
        "supports_file_locking": "true",
        "supports_atomic_writes": "true",

        # Components
        "components": {
            "master_key_manager": "Master encryption key management",
            "encrypted_storage": "Simulated AES256-GCM encryption",
            "storage_backend_fs": "Filesystem backend with atomic writes",
            "storage_schemas": "Data schemas for all storage files",
            "secrets_manager": "Encrypted secrets management (NO passwords)",
            "snapshot_engine": "Snapshot and rollback functionality",
            "persistence_manager": "Unified persistence API"
        },

        # Architecture
        "architecture": "encrypted_at_rest",
        "approach": "privacy_by_default",

        # Storage Files
        "storage_files": [
            "devices.json (encrypted)",
            "permissions.json (encrypted)",
            "sessions.json (encrypted)",
            "settings.json (encrypted)",
            "orch_history.json (encrypted)",
            "oauth_tokens.json (encrypted)",
            "platform_sessions.json (encrypted)",
            "secrets.json (encrypted)"
        ],

        # Contact
        "author": "SENTI OS Core Team",
        "license": "Proprietary"
    }


# Version info
__version__ = "1.0.0"
__author__ = "SENTI OS Core Team"
__license__ = "Proprietary"
