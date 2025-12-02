"""
FAZA 19 - Device Identity Manager

This module manages device identities in the Unified Interaction Layer.
It handles device registration, public key management, and device tracking
across the multi-device ecosystem.

CRITICAL PRIVACY RULE:
    This module NEVER processes biometric data.
    Device identity is based on cryptographic keys only (simulated).

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import json


class DeviceType(Enum):
    """Types of devices that can connect to SENTI OS."""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    WEB = "web"
    CLI = "cli"
    IOT = "iot"
    UNKNOWN = "unknown"


class DeviceStatus(Enum):
    """Status of a registered device."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    PENDING_VERIFICATION = "pending_verification"


@dataclass
class DeviceIdentity:
    """
    Represents a device identity in the system.

    SECURITY:
        - Device ID is cryptographically generated
        - Public key for E2E encryption (simulated)
        - No biometric data stored
        - Zero-trust verification
    """
    device_id: str
    device_name: str
    device_type: DeviceType
    public_key: str  # Simulated public key
    status: DeviceStatus
    registered_at: datetime
    last_seen: datetime
    user_identifier: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    trust_score: float = 0.5  # 0.0 to 1.0, starts neutral

    def to_dict(self) -> Dict[str, Any]:
        """Convert device identity to dictionary."""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type.value,
            "public_key": self.public_key,
            "status": self.status.value,
            "registered_at": self.registered_at.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "user_identifier": self.user_identifier,
            "metadata": self.metadata,
            "trust_score": self.trust_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceIdentity":
        """Create DeviceIdentity from dictionary."""
        return cls(
            device_id=data["device_id"],
            device_name=data["device_name"],
            device_type=DeviceType(data["device_type"]),
            public_key=data["public_key"],
            status=DeviceStatus(data["status"]),
            registered_at=datetime.fromisoformat(data["registered_at"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            user_identifier=data.get("user_identifier"),
            metadata=data.get("metadata", {}),
            trust_score=data.get("trust_score", 0.5)
        )


class DeviceIdentityManager:
    """
    Manages device identities in the Unified Interaction Layer.

    This manager implements zero-trust device identity management with
    cryptographic verification (simulated) and trust scoring.

    PRIVACY GUARANTEE:
        - No biometric data processing
        - Device identity based on cryptographic keys only
        - Full audit trail of device activities
        - GDPR-compliant device tracking
    """

    def __init__(self):
        """Initialize the device identity manager."""
        self._devices: Dict[str, DeviceIdentity] = {}
        self._device_links: Dict[str, List[str]] = {}  # user -> device IDs
        self._key_counter = 0

    def generate_device_id(self, device_name: str, device_type: DeviceType) -> str:
        """
        Generate a unique device ID.

        Args:
            device_name: Human-readable device name.
            device_type: Type of device.

        Returns:
            Unique device ID string.
        """
        # Generate cryptographically secure random bytes
        random_bytes = secrets.token_bytes(32)
        timestamp = str(datetime.utcnow().timestamp()).encode()
        device_info = f"{device_name}:{device_type.value}".encode()

        # Combine and hash
        combined = random_bytes + timestamp + device_info
        device_id_hash = hashlib.sha256(combined).hexdigest()

        return f"device_{device_id_hash[:24]}"

    def generate_public_key(self, device_id: str) -> str:
        """
        Generate a simulated public key for a device.

        Args:
            device_id: The device ID.

        Returns:
            Simulated public key string.

        Note:
            In production, this would use real cryptographic key generation.
            For FAZA 19, we simulate the key structure.
        """
        self._key_counter += 1
        key_material = f"{device_id}:{self._key_counter}:{datetime.utcnow().timestamp()}"
        key_hash = hashlib.sha256(key_material.encode()).hexdigest()

        # Simulate a public key format (similar to base64-encoded key)
        return f"PK_{key_hash[:64]}"

    def register_device(
        self,
        device_name: str,
        device_type: DeviceType,
        user_identifier: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeviceIdentity:
        """
        Register a new device in the system.

        Args:
            device_name: Human-readable device name.
            device_type: Type of device.
            user_identifier: Optional user identifier.
            metadata: Optional device metadata.

        Returns:
            DeviceIdentity object for the registered device.
        """
        # Generate device ID
        device_id = self.generate_device_id(device_name, device_type)

        # Generate public key
        public_key = self.generate_public_key(device_id)

        # Create device identity
        now = datetime.utcnow()
        device = DeviceIdentity(
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            public_key=public_key,
            status=DeviceStatus.PENDING_VERIFICATION,
            registered_at=now,
            last_seen=now,
            user_identifier=user_identifier,
            metadata=metadata or {},
            trust_score=0.5  # Start with neutral trust
        )

        # Store device
        self._devices[device_id] = device

        # Link to user if provided
        if user_identifier:
            if user_identifier not in self._device_links:
                self._device_links[user_identifier] = []
            self._device_links[user_identifier].append(device_id)

        return device

    def verify_device(self, device_id: str) -> bool:
        """
        Verify a device and activate it.

        Args:
            device_id: The device ID to verify.

        Returns:
            True if verified successfully, False if not found.
        """
        device = self._devices.get(device_id)
        if not device:
            return False

        device.status = DeviceStatus.ACTIVE
        device.trust_score = 0.7  # Boost trust after verification
        return True

    def get_device(self, device_id: str) -> Optional[DeviceIdentity]:
        """
        Get a device identity by ID.

        Args:
            device_id: The device ID.

        Returns:
            DeviceIdentity if found, None otherwise.
        """
        device = self._devices.get(device_id)
        if device:
            # Update last seen
            device.last_seen = datetime.utcnow()
        return device

    def get_devices_for_user(self, user_identifier: str) -> List[DeviceIdentity]:
        """
        Get all devices linked to a user.

        Args:
            user_identifier: The user identifier.

        Returns:
            List of DeviceIdentity objects.
        """
        device_ids = self._device_links.get(user_identifier, [])
        return [self._devices[did] for did in device_ids if did in self._devices]

    def update_device_status(
        self,
        device_id: str,
        status: DeviceStatus
    ) -> bool:
        """
        Update device status.

        Args:
            device_id: The device ID.
            status: New status.

        Returns:
            True if updated, False if not found.
        """
        device = self._devices.get(device_id)
        if not device:
            return False

        device.status = status
        return True

    def revoke_device(self, device_id: str) -> bool:
        """
        Revoke a device (permanent action).

        Args:
            device_id: The device ID to revoke.

        Returns:
            True if revoked, False if not found.
        """
        device = self._devices.get(device_id)
        if not device:
            return False

        device.status = DeviceStatus.REVOKED
        device.trust_score = 0.0
        return True

    def suspend_device(self, device_id: str) -> bool:
        """
        Temporarily suspend a device.

        Args:
            device_id: The device ID to suspend.

        Returns:
            True if suspended, False if not found.
        """
        device = self._devices.get(device_id)
        if not device:
            return False

        device.status = DeviceStatus.SUSPENDED
        device.trust_score = max(0.0, device.trust_score - 0.3)
        return True

    def reactivate_device(self, device_id: str) -> bool:
        """
        Reactivate a suspended device.

        Args:
            device_id: The device ID to reactivate.

        Returns:
            True if reactivated, False if not found or revoked.
        """
        device = self._devices.get(device_id)
        if not device or device.status == DeviceStatus.REVOKED:
            return False

        device.status = DeviceStatus.ACTIVE
        device.trust_score = min(1.0, device.trust_score + 0.2)
        return True

    def update_trust_score(
        self,
        device_id: str,
        delta: float,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update device trust score.

        Args:
            device_id: The device ID.
            delta: Change in trust score (-1.0 to +1.0).
            reason: Optional reason for update.

        Returns:
            True if updated, False if not found.
        """
        device = self._devices.get(device_id)
        if not device:
            return False

        # Update trust score (clamp between 0.0 and 1.0)
        device.trust_score = max(0.0, min(1.0, device.trust_score + delta))

        # Store reason in metadata
        if reason:
            if "trust_updates" not in device.metadata:
                device.metadata["trust_updates"] = []
            device.metadata["trust_updates"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "delta": delta,
                "reason": reason,
                "new_score": device.trust_score
            })

        return True

    def is_device_trusted(
        self,
        device_id: str,
        min_trust_score: float = 0.6
    ) -> bool:
        """
        Check if a device is trusted.

        Args:
            device_id: The device ID.
            min_trust_score: Minimum trust score required (default: 0.6).

        Returns:
            True if device is trusted and active.
        """
        device = self._devices.get(device_id)
        if not device:
            return False

        return (
            device.status == DeviceStatus.ACTIVE and
            device.trust_score >= min_trust_score
        )

    def get_active_devices(self) -> List[DeviceIdentity]:
        """
        Get all active devices.

        Returns:
            List of active DeviceIdentity objects.
        """
        return [
            device for device in self._devices.values()
            if device.status == DeviceStatus.ACTIVE
        ]

    def get_device_count(self) -> Dict[str, int]:
        """
        Get device counts by status.

        Returns:
            Dictionary with counts per status.
        """
        counts = {status.value: 0 for status in DeviceStatus}
        for device in self._devices.values():
            counts[device.status.value] += 1
        return counts

    def cleanup_inactive_devices(self, inactive_days: int = 90) -> int:
        """
        Mark devices as inactive if not seen for specified days.

        Args:
            inactive_days: Days of inactivity before marking inactive.

        Returns:
            Number of devices marked inactive.
        """
        threshold = datetime.utcnow() - timedelta(days=inactive_days)
        count = 0

        for device in self._devices.values():
            if (device.status == DeviceStatus.ACTIVE and
                device.last_seen < threshold):
                device.status = DeviceStatus.INACTIVE
                count += 1

        return count

    def export_devices(self) -> Dict[str, Any]:
        """
        Export all device identities.

        Returns:
            Dictionary with all device data.
        """
        return {
            "exported_at": datetime.utcnow().isoformat(),
            "total_devices": len(self._devices),
            "devices": [device.to_dict() for device in self._devices.values()]
        }

    def import_devices(self, data: Dict[str, Any]) -> int:
        """
        Import device identities from export data.

        Args:
            data: Exported device data.

        Returns:
            Number of devices imported.
        """
        count = 0
        for device_data in data.get("devices", []):
            try:
                device = DeviceIdentity.from_dict(device_data)
                self._devices[device.device_id] = device

                # Rebuild user links
                if device.user_identifier:
                    if device.user_identifier not in self._device_links:
                        self._device_links[device.user_identifier] = []
                    if device.device_id not in self._device_links[device.user_identifier]:
                        self._device_links[device.user_identifier].append(device.device_id)

                count += 1
            except Exception:
                # Skip invalid devices
                continue

        return count

    def get_device_summary(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of device information (safe for display).

        Args:
            device_id: The device ID.

        Returns:
            Dictionary with device summary, or None if not found.
        """
        device = self._devices.get(device_id)
        if not device:
            return None

        return {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "device_type": device.device_type.value,
            "status": device.status.value,
            "trust_score": device.trust_score,
            "registered_at": device.registered_at.isoformat(),
            "last_seen": device.last_seen.isoformat(),
            "has_public_key": bool(device.public_key)
        }


def get_info() -> Dict[str, str]:
    """
    Get module information.

    Returns:
        Dictionary with module metadata.
    """
    return {
        "module": "device_identity_manager",
        "faza": "19",
        "version": "1.0.0",
        "description": "Multi-device identity management with zero-trust architecture",
        "privacy_compliant": "true",
        "processes_biometrics": "false",
        "authentication_method": "cryptographic_keys_only"
    }
