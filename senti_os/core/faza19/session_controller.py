"""
FAZA 19 - Session Controller

Manages multi-device sessions with token issuance, expiration tracking,
and revocation support.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets


class SessionStatus(Enum):
    """Session status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class DeviceSession:
    """Device session information."""
    session_id: str
    device_id: str
    session_token: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    status: SessionStatus


class SessionController:
    """Multi-device session management."""

    def __init__(self, default_expiry_hours: int = 24):
        """Initialize session controller."""
        self.default_expiry_hours = default_expiry_hours
        self._sessions: Dict[str, DeviceSession] = {}
        self._device_sessions: Dict[str, List[str]] = {}

    def create_session(
        self,
        device_id: str,
        expiry_hours: Optional[int] = None
    ) -> DeviceSession:
        """Create new session for device."""
        session_id = self._generate_session_id()
        session_token = self._generate_session_token()
        now = datetime.utcnow()
        expiry = expiry_hours or self.default_expiry_hours

        session = DeviceSession(
            session_id=session_id,
            device_id=device_id,
            session_token=session_token,
            created_at=now,
            expires_at=now + timedelta(hours=expiry),
            last_activity=now,
            status=SessionStatus.ACTIVE
        )

        self._sessions[session_id] = session

        if device_id not in self._device_sessions:
            self._device_sessions[device_id] = []
        self._device_sessions[device_id].append(session_id)

        return session

    def validate_session(self, session_token: str) -> Optional[DeviceSession]:
        """Validate session token and return session if valid."""
        for session in self._sessions.values():
            if session.session_token == session_token:
                if session.status == SessionStatus.ACTIVE:
                    if datetime.utcnow() < session.expires_at:
                        session.last_activity = datetime.utcnow()
                        return session
                    else:
                        session.status = SessionStatus.EXPIRED
        return None

    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session."""
        session = self._sessions.get(session_id)
        if session:
            session.status = SessionStatus.REVOKED
            return True
        return False

    def revoke_all_device_sessions(self, device_id: str) -> int:
        """Revoke all sessions for a device."""
        session_ids = self._device_sessions.get(device_id, [])
        count = 0
        for sid in session_ids:
            if self.revoke_session(sid):
                count += 1
        return count

    def get_active_sessions(self, device_id: str) -> List[DeviceSession]:
        """Get all active sessions for device."""
        session_ids = self._device_sessions.get(device_id, [])
        return [
            self._sessions[sid] for sid in session_ids
            if sid in self._sessions and
            self._sessions[sid].status == SessionStatus.ACTIVE and
            self._sessions[sid].expires_at > datetime.utcnow()
        ]

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        now = datetime.utcnow()
        count = 0
        for session in self._sessions.values():
            if session.expires_at < now and session.status == SessionStatus.ACTIVE:
                session.status = SessionStatus.EXPIRED
                count += 1
        return count

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        random_bytes = secrets.token_bytes(16)
        timestamp = str(datetime.utcnow().timestamp()).encode()
        combined = random_bytes + timestamp
        return f"sess_{hashlib.sha256(combined).hexdigest()[:20]}"

    def _generate_session_token(self) -> str:
        """Generate session token."""
        return hashlib.sha256(secrets.token_bytes(32)).hexdigest()


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "session_controller",
        "faza": "19",
        "version": "1.0.0",
        "description": "Multi-device session management"
    }
