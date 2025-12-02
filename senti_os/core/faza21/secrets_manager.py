"""
FAZA 21 - Secrets Manager

Manages encrypted secrets like OAuth tokens and platform session tokens.
NO PASSWORD STORAGE.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class Secret:
    """Represents a stored secret."""
    secret_id: str
    secret_type: str  # "oauth_token", "platform_session", etc.
    value: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def is_expired(self) -> bool:
        """Check if secret is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() >= self.expires_at


class SecretsManager:
    """
    Manages encrypted secrets.

    SECURITY GUARANTEE:
        - NO password storage
        - Only tokens and session IDs
        - Automatic expiration checking
        - Encrypted at rest via EncryptedStorage
    """

    def __init__(self, encrypted_storage, storage_backend):
        """
        Initialize secrets manager.

        Args:
            encrypted_storage: EncryptedStorage instance.
            storage_backend: StorageBackendFS instance.
        """
        self.encrypted_storage = encrypted_storage
        self.storage_backend = storage_backend
        self._secrets: Dict[str, Secret] = {}
        self._load_secrets()

    def store_secret(
        self,
        secret_id: str,
        secret_type: str,
        value: str,
        expires_in_hours: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Store a secret.

        Args:
            secret_id: Unique secret identifier.
            secret_type: Type of secret.
            value: Secret value (token, session ID, etc.).
            expires_in_hours: Optional expiration time.
            metadata: Optional metadata.

        Returns:
            True if stored successfully.
        """
        # Validate no password storage
        if "password" in secret_type.lower():
            raise ValueError("Password storage not allowed")

        expires_at = None
        if expires_in_hours is not None:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        secret = Secret(
            secret_id=secret_id,
            secret_type=secret_type,
            value=value,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            metadata=metadata or {}
        )

        self._secrets[secret_id] = secret
        return self._save_secrets()

    def get_secret(self, secret_id: str) -> Optional[str]:
        """
        Retrieve secret value.

        Args:
            secret_id: Secret identifier.

        Returns:
            Secret value if found and not expired, None otherwise.
        """
        secret = self._secrets.get(secret_id)
        if not secret:
            return None

        if secret.is_expired():
            self.delete_secret(secret_id)
            return None

        return secret.value

    def delete_secret(self, secret_id: str) -> bool:
        """Delete a secret."""
        if secret_id in self._secrets:
            del self._secrets[secret_id]
            return self._save_secrets()
        return False

    def list_secrets(self, secret_type: Optional[str] = None) -> List[str]:
        """List secret IDs, optionally filtered by type."""
        self._cleanup_expired()

        if secret_type:
            return [
                sid for sid, secret in self._secrets.items()
                if secret.secret_type == secret_type
            ]
        return list(self._secrets.keys())

    def rotate_secret(self, secret_id: str, new_value: str) -> bool:
        """
        Rotate a secret (update with new value).

        Args:
            secret_id: Secret to rotate.
            new_value: New secret value.

        Returns:
            True if rotated successfully.
        """
        secret = self._secrets.get(secret_id)
        if not secret:
            return False

        secret.value = new_value
        secret.created_at = datetime.utcnow()
        return self._save_secrets()

    def _cleanup_expired(self) -> int:
        """Remove expired secrets."""
        expired = [
            sid for sid, secret in self._secrets.items()
            if secret.is_expired()
        ]

        for sid in expired:
            del self._secrets[sid]

        if expired:
            self._save_secrets()

        return len(expired)

    def _save_secrets(self) -> bool:
        """Save secrets to encrypted storage."""
        try:
            data = {
                "schema_version": "1.0",
                "last_updated": datetime.utcnow().isoformat(),
                "secrets": [
                    {
                        "secret_id": s.secret_id,
                        "secret_type": s.secret_type,
                        "value": s.value,
                        "created_at": s.created_at.isoformat(),
                        "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                        "metadata": s.metadata
                    }
                    for s in self._secrets.values()
                ]
            }

            encrypted = self.encrypted_storage.encrypt(data)
            return self.storage_backend.write("secrets.json", encrypted)
        except Exception:
            return False

    def _load_secrets(self):
        """Load secrets from encrypted storage."""
        try:
            encrypted = self.storage_backend.read("secrets.json")
            if not encrypted:
                return

            data = self.encrypted_storage.decrypt(encrypted)

            for secret_data in data.get("secrets", []):
                secret = Secret(
                    secret_id=secret_data["secret_id"],
                    secret_type=secret_data["secret_type"],
                    value=secret_data["value"],
                    created_at=datetime.fromisoformat(secret_data["created_at"]),
                    expires_at=datetime.fromisoformat(secret_data["expires_at"]) if secret_data.get("expires_at") else None,
                    metadata=secret_data.get("metadata", {})
                )
                self._secrets[secret.secret_id] = secret

            self._cleanup_expired()
        except Exception:
            pass


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "secrets_manager",
        "faza": "21",
        "version": "1.0.0",
        "description": "Encrypted secrets management (NO passwords)",
        "stores_passwords": "false",
        "stores_biometrics": "false"
    }
