"""
FAZA 19 - Device Linking Service

This module handles secure device pairing and linking using QR code flows
and simulated X3DH key exchange protocol.

CRITICAL PRIVACY RULE:
    This module NEVER processes biometric data.
    Device linking is based on cryptographic verification only (simulated).

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import json


class LinkingStatus(Enum):
    """Status of device linking process."""
    INITIATED = "initiated"
    QR_GENERATED = "qr_generated"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class LinkingRequest:
    """Represents a device linking request."""
    request_id: str
    initiator_device_id: str
    target_device_id: Optional[str]
    status: LinkingStatus
    pairing_token: str
    qr_code_data: str
    expires_at: datetime
    created_at: datetime
    completed_at: Optional[datetime] = None
    shared_secret: Optional[str] = None  # Simulated X3DH result


class DeviceLinkingService:
    """
    Manages secure device linking using QR code flow and simulated X3DH.

    This service implements zero-trust device pairing with cryptographic
    verification (simulated) to ensure secure multi-device connections.

    PRIVACY GUARANTEE:
        - No biometric data processing
        - Cryptographic pairing only (simulated)
        - Time-limited pairing tokens
        - Explicit user approval required
    """

    def __init__(self, token_expiry_minutes: int = 5):
        """
        Initialize the device linking service.

        Args:
            token_expiry_minutes: Minutes until pairing token expires (default: 5).
        """
        self.token_expiry_minutes = token_expiry_minutes
        self._linking_requests: Dict[str, LinkingRequest] = {}
        self._device_pairs: Dict[str, str] = {}  # device_id -> linked_device_id

    def initiate_linking(
        self,
        initiator_device_id: str,
        device_name: str = "New Device"
    ) -> LinkingRequest:
        """
        Initiate device linking process.

        Args:
            initiator_device_id: Device ID that initiates linking.
            device_name: Human-readable name for linking.

        Returns:
            LinkingRequest with QR code data.
        """
        # Generate request ID
        request_id = self._generate_request_id()

        # Generate pairing token
        pairing_token = self._generate_pairing_token()

        # Generate QR code data (simulated)
        qr_data = self._generate_qr_code_data(request_id, pairing_token, device_name)

        # Create linking request
        now = datetime.utcnow()
        request = LinkingRequest(
            request_id=request_id,
            initiator_device_id=initiator_device_id,
            target_device_id=None,
            status=LinkingStatus.QR_GENERATED,
            pairing_token=pairing_token,
            qr_code_data=qr_data,
            expires_at=now + timedelta(minutes=self.token_expiry_minutes),
            created_at=now
        )

        self._linking_requests[request_id] = request
        return request

    def scan_qr_and_request_link(
        self,
        qr_code_data: str,
        scanning_device_id: str
    ) -> Optional[str]:
        """
        Scan QR code and request device linking.

        Args:
            qr_code_data: QR code data scanned by device.
            scanning_device_id: Device ID of scanning device.

        Returns:
            Request ID if successful, None if invalid/expired.
        """
        # Parse QR code data
        parsed = self._parse_qr_code_data(qr_code_data)
        if not parsed:
            return None

        request_id = parsed.get("request_id")
        pairing_token = parsed.get("pairing_token")

        request = self._linking_requests.get(request_id)
        if not request:
            return None

        # Check expiration
        if datetime.utcnow() > request.expires_at:
            request.status = LinkingStatus.EXPIRED
            return None

        # Check token
        if request.pairing_token != pairing_token:
            return None

        # Update request
        request.target_device_id = scanning_device_id
        request.status = LinkingStatus.PENDING_APPROVAL

        return request_id

    def approve_linking(self, request_id: str) -> bool:
        """
        Approve device linking (user consent).

        Args:
            request_id: The linking request ID.

        Returns:
            True if approved, False if not found/invalid.
        """
        request = self._linking_requests.get(request_id)
        if not request:
            return False

        if request.status != LinkingStatus.PENDING_APPROVAL:
            return False

        # Simulate X3DH key exchange
        shared_secret = self._simulate_x3dh_key_exchange(
            request.initiator_device_id,
            request.target_device_id
        )

        request.shared_secret = shared_secret
        request.status = LinkingStatus.APPROVED

        return True

    def complete_linking(self, request_id: str) -> bool:
        """
        Complete device linking after approval.

        Args:
            request_id: The linking request ID.

        Returns:
            True if completed, False if not approved.
        """
        request = self._linking_requests.get(request_id)
        if not request:
            return False

        if request.status != LinkingStatus.APPROVED:
            return False

        # Create device pair link
        if request.target_device_id:
            self._device_pairs[request.initiator_device_id] = request.target_device_id
            self._device_pairs[request.target_device_id] = request.initiator_device_id

        request.status = LinkingStatus.COMPLETED
        request.completed_at = datetime.utcnow()

        return True

    def reject_linking(self, request_id: str, reason: Optional[str] = None) -> bool:
        """
        Reject device linking request.

        Args:
            request_id: The linking request ID.
            reason: Optional rejection reason.

        Returns:
            True if rejected, False if not found.
        """
        request = self._linking_requests.get(request_id)
        if not request:
            return False

        request.status = LinkingStatus.REJECTED
        return True

    def get_linking_request(self, request_id: str) -> Optional[LinkingRequest]:
        """
        Get linking request by ID.

        Args:
            request_id: The request ID.

        Returns:
            LinkingRequest if found, None otherwise.
        """
        return self._linking_requests.get(request_id)

    def get_linked_devices(self, device_id: str) -> List[str]:
        """
        Get all devices linked to a device.

        Args:
            device_id: The device ID.

        Returns:
            List of linked device IDs.
        """
        linked = []
        for dev_id, linked_id in self._device_pairs.items():
            if dev_id == device_id:
                linked.append(linked_id)
        return linked

    def unlink_devices(self, device_id_1: str, device_id_2: str) -> bool:
        """
        Unlink two devices.

        Args:
            device_id_1: First device ID.
            device_id_2: Second device ID.

        Returns:
            True if unlinked, False if not linked.
        """
        if (self._device_pairs.get(device_id_1) == device_id_2 and
            self._device_pairs.get(device_id_2) == device_id_1):

            del self._device_pairs[device_id_1]
            del self._device_pairs[device_id_2]
            return True

        return False

    def cleanup_expired_requests(self) -> int:
        """
        Clean up expired linking requests.

        Returns:
            Number of requests cleaned up.
        """
        now = datetime.utcnow()
        to_remove = []

        for request_id, request in self._linking_requests.items():
            if request.expires_at < now and request.status not in [
                LinkingStatus.COMPLETED, LinkingStatus.REJECTED
            ]:
                request.status = LinkingStatus.EXPIRED
                to_remove.append(request_id)

        for request_id in to_remove:
            del self._linking_requests[request_id]

        return len(to_remove)

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        random_bytes = secrets.token_bytes(16)
        timestamp = str(datetime.utcnow().timestamp()).encode()
        combined = random_bytes + timestamp
        request_hash = hashlib.sha256(combined).hexdigest()
        return f"link_req_{request_hash[:20]}"

    def _generate_pairing_token(self) -> str:
        """Generate pairing token."""
        token_bytes = secrets.token_bytes(32)
        return hashlib.sha256(token_bytes).hexdigest()[:16]

    def _generate_qr_code_data(
        self,
        request_id: str,
        pairing_token: str,
        device_name: str
    ) -> str:
        """Generate QR code data (JSON format)."""
        data = {
            "type": "senti_device_link",
            "version": "1.0",
            "request_id": request_id,
            "pairing_token": pairing_token,
            "device_name": device_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(data)

    def _parse_qr_code_data(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """Parse QR code data."""
        try:
            data = json.loads(qr_data)
            if data.get("type") == "senti_device_link":
                return data
        except Exception:
            pass
        return None

    def _simulate_x3dh_key_exchange(
        self,
        device_id_1: str,
        device_id_2: Optional[str]
    ) -> str:
        """
        Simulate X3DH key exchange.

        In production, this would perform actual X3DH protocol.
        For FAZA 19, we simulate the shared secret generation.
        """
        if not device_id_2:
            device_id_2 = "unknown"

        # Simulate key exchange result
        material = f"{device_id_1}:{device_id_2}:{datetime.utcnow().timestamp()}"
        shared_secret = hashlib.sha256(material.encode()).hexdigest()
        return shared_secret


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "device_linking_service",
        "faza": "19",
        "version": "1.0.0",
        "description": "Secure device pairing with QR code and simulated X3DH",
        "privacy_compliant": "true",
        "processes_biometrics": "false"
    }
