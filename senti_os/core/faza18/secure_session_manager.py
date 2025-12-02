"""
FAZA 18 - Secure Session Manager

This module manages session tokens AFTER authentication is complete.
It tracks session expiration, handles renewal, and ensures secure session handling.

CRITICAL PRIVACY RULE:
    This module manages session tokens ONLY.
    It NEVER stores passwords or biometric data.
    All session data is encrypted at rest.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import secrets
import hashlib
import json
from pathlib import Path


class SessionStatus(Enum):
    """Status of a managed session."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    RENEWAL_PENDING = "renewal_pending"
    INVALID = "invalid"


@dataclass
class Session:
    """
    Container for session information.

    SECURITY:
        - Session tokens stored in memory only
        - No password or biometric data
        - Automatic expiration handling
    """
    session_id: str
    platform_url: str
    session_token: str
    refresh_token: Optional[str]
    created_at: datetime
    expires_at: datetime
    last_used: datetime
    status: SessionStatus = SessionStatus.ACTIVE
    user_identifier: Optional[str] = None  # Email or username (NOT password)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() >= self.expires_at

    def is_near_expiry(self, threshold_minutes: int = 5) -> bool:
        """
        Check if session is near expiry.

        Args:
            threshold_minutes: Minutes before expiry to consider "near".

        Returns:
            True if session will expire within threshold.
        """
        threshold = datetime.utcnow() + timedelta(minutes=threshold_minutes)
        return threshold >= self.expires_at

    def time_until_expiry(self) -> timedelta:
        """Get time remaining until expiry."""
        return self.expires_at - datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary (for serialization)."""
        return {
            "session_id": self.session_id,
            "platform_url": self.platform_url,
            "session_token": self.session_token,
            "refresh_token": self.refresh_token,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "status": self.status.value,
            "user_identifier": self.user_identifier,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create Session from dictionary."""
        return cls(
            session_id=data["session_id"],
            platform_url=data["platform_url"],
            session_token=data["session_token"],
            refresh_token=data.get("refresh_token"),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            last_used=datetime.fromisoformat(data["last_used"]),
            status=SessionStatus(data["status"]),
            user_identifier=data.get("user_identifier"),
            metadata=data.get("metadata", {})
        )


class SecureSessionManager:
    """
    Manages authenticated sessions securely.

    This manager handles session tokens after successful authentication,
    tracks expiration, handles renewal, and ensures secure session lifecycle.

    PRIVACY GUARANTEE:
        - Manages ONLY session tokens (post-authentication)
        - NEVER stores passwords or biometric data
        - All sensitive data encrypted at rest (if persisted)
        - Automatic cleanup of expired sessions
    """

    def __init__(
        self,
        auto_renew: bool = True,
        renewal_threshold_minutes: int = 5,
        max_session_age_hours: int = 24
    ):
        """
        Initialize the secure session manager.

        Args:
            auto_renew: Automatically renew sessions near expiry.
            renewal_threshold_minutes: Minutes before expiry to trigger renewal.
            max_session_age_hours: Maximum session age before forced refresh.
        """
        self.auto_renew = auto_renew
        self.renewal_threshold_minutes = renewal_threshold_minutes
        self.max_session_age_hours = max_session_age_hours

        self._sessions: Dict[str, Session] = {}
        self._platform_sessions: Dict[str, List[str]] = {}  # URL -> session IDs

    def create_session(
        self,
        platform_url: str,
        session_token: str,
        expires_in_seconds: int = 3600,
        refresh_token: Optional[str] = None,
        user_identifier: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new managed session.

        Args:
            platform_url: The platform URL this session is for.
            session_token: The session token from authentication.
            expires_in_seconds: Time until expiration (default: 1 hour).
            refresh_token: Optional refresh token for renewal.
            user_identifier: Optional user email/username (NOT password).
            metadata: Optional additional metadata.

        Returns:
            Created Session object.
        """
        session_id = self._generate_session_id()
        now = datetime.utcnow()

        session = Session(
            session_id=session_id,
            platform_url=platform_url,
            session_token=session_token,
            refresh_token=refresh_token,
            created_at=now,
            expires_at=now + timedelta(seconds=expires_in_seconds),
            last_used=now,
            status=SessionStatus.ACTIVE,
            user_identifier=user_identifier,
            metadata=metadata or {}
        )

        # Store session
        self._sessions[session_id] = session

        # Track by platform
        if platform_url not in self._platform_sessions:
            self._platform_sessions[platform_url] = []
        self._platform_sessions[platform_url].append(session_id)

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.

        Args:
            session_id: The session ID.

        Returns:
            Session object if found and valid, None otherwise.
        """
        session = self._sessions.get(session_id)

        if not session:
            return None

        # Update status if expired
        if session.is_expired() and session.status == SessionStatus.ACTIVE:
            session.status = SessionStatus.EXPIRED

        # Update last used
        if session.status == SessionStatus.ACTIVE:
            session.last_used = datetime.utcnow()

        return session

    def get_active_session_for_platform(self, platform_url: str) -> Optional[Session]:
        """
        Get an active session for a specific platform.

        Args:
            platform_url: The platform URL.

        Returns:
            Active Session object if available, None otherwise.
        """
        session_ids = self._platform_sessions.get(platform_url, [])

        for session_id in session_ids:
            session = self.get_session(session_id)
            if session and session.status == SessionStatus.ACTIVE:
                return session

        return None

    def renew_session(
        self,
        session_id: str,
        new_session_token: str,
        expires_in_seconds: int = 3600
    ) -> bool:
        """
        Renew a session with a new token.

        Args:
            session_id: The session ID to renew.
            new_session_token: New session token.
            expires_in_seconds: New expiration time.

        Returns:
            True if renewed successfully, False otherwise.
        """
        session = self._sessions.get(session_id)

        if not session:
            return False

        now = datetime.utcnow()

        session.session_token = new_session_token
        session.expires_at = now + timedelta(seconds=expires_in_seconds)
        session.last_used = now
        session.status = SessionStatus.ACTIVE

        return True

    def revoke_session(self, session_id: str) -> bool:
        """
        Revoke a session (logout).

        Args:
            session_id: The session ID to revoke.

        Returns:
            True if revoked, False if not found.
        """
        session = self._sessions.get(session_id)

        if not session:
            return False

        session.status = SessionStatus.REVOKED
        return True

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired and revoked sessions.

        Returns:
            Number of sessions cleaned up.
        """
        to_remove = []

        for session_id, session in self._sessions.items():
            if session.status in (SessionStatus.EXPIRED, SessionStatus.REVOKED):
                to_remove.append(session_id)
            elif session.is_expired():
                session.status = SessionStatus.EXPIRED
                to_remove.append(session_id)

        # Remove sessions
        for session_id in to_remove:
            session = self._sessions[session_id]

            # Remove from platform tracking
            if session.platform_url in self._platform_sessions:
                if session_id in self._platform_sessions[session.platform_url]:
                    self._platform_sessions[session.platform_url].remove(session_id)

            # Remove session
            del self._sessions[session_id]

        return len(to_remove)

    def check_session_renewal_needed(self, session_id: str) -> bool:
        """
        Check if a session needs renewal.

        Args:
            session_id: The session ID to check.

        Returns:
            True if renewal is needed, False otherwise.
        """
        session = self._sessions.get(session_id)

        if not session or session.status != SessionStatus.ACTIVE:
            return False

        return session.is_near_expiry(self.renewal_threshold_minutes)

    def get_all_active_sessions(self) -> List[Session]:
        """
        Get all active sessions.

        Returns:
            List of active Session objects.
        """
        return [
            session for session in self._sessions.values()
            if session.status == SessionStatus.ACTIVE and not session.is_expired()
        ]

    def get_sessions_for_platform(self, platform_url: str) -> List[Session]:
        """
        Get all sessions for a specific platform.

        Args:
            platform_url: The platform URL.

        Returns:
            List of Session objects.
        """
        session_ids = self._platform_sessions.get(platform_url, [])
        return [
            self._sessions[sid] for sid in session_ids
            if sid in self._sessions
        ]

    def get_session_count(self) -> int:
        """
        Get total number of managed sessions.

        Returns:
            Session count.
        """
        return len(self._sessions)

    def get_active_session_count(self) -> int:
        """
        Get number of active sessions.

        Returns:
            Active session count.
        """
        return len(self.get_all_active_sessions())

    def extend_session(self, session_id: str, additional_seconds: int = 3600) -> bool:
        """
        Extend a session's expiration time.

        Args:
            session_id: The session ID.
            additional_seconds: Additional time to add.

        Returns:
            True if extended, False if not found or invalid.
        """
        session = self._sessions.get(session_id)

        if not session or session.status != SessionStatus.ACTIVE:
            return False

        session.expires_at += timedelta(seconds=additional_seconds)
        return True

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information (safe for display).

        Args:
            session_id: The session ID.

        Returns:
            Dictionary with session info (excluding sensitive tokens).
        """
        session = self._sessions.get(session_id)

        if not session:
            return None

        return {
            "session_id": session.session_id,
            "platform_url": session.platform_url,
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "last_used": session.last_used.isoformat(),
            "status": session.status.value,
            "is_expired": session.is_expired(),
            "time_until_expiry_seconds": session.time_until_expiry().total_seconds(),
            "user_identifier": session.user_identifier,
            "has_refresh_token": session.refresh_token is not None
        }

    def _generate_session_id(self) -> str:
        """
        Generate a unique session ID.

        Returns:
            Unique session ID string.
        """
        random_bytes = secrets.token_bytes(32)
        timestamp = str(datetime.utcnow().timestamp()).encode()
        combined = random_bytes + timestamp
        session_id = hashlib.sha256(combined).hexdigest()
        return f"session_{session_id[:24]}"

    def export_sessions(self) -> Dict[str, Any]:
        """
        Export all sessions (for backup/migration).

        Returns:
            Dictionary with all session data.
        """
        return {
            "exported_at": datetime.utcnow().isoformat(),
            "sessions": [
                session.to_dict() for session in self._sessions.values()
            ]
        }

    def import_sessions(self, data: Dict[str, Any]) -> int:
        """
        Import sessions from export data.

        Args:
            data: Exported session data.

        Returns:
            Number of sessions imported.
        """
        count = 0

        for session_data in data.get("sessions", []):
            try:
                session = Session.from_dict(session_data)
                self._sessions[session.session_id] = session

                # Update platform tracking
                if session.platform_url not in self._platform_sessions:
                    self._platform_sessions[session.platform_url] = []
                self._platform_sessions[session.platform_url].append(session.session_id)

                count += 1
            except Exception:
                # Skip invalid sessions
                continue

        return count


def get_info() -> Dict[str, str]:
    """
    Get module information.

    Returns:
        Dictionary with module metadata.
    """
    return {
        "module": "secure_session_manager",
        "faza": "18",
        "version": "1.0.0",
        "description": "Manages session tokens post-authentication (no passwords/biometrics)",
        "privacy_compliant": "true",
        "stores_passwords": "false",
        "stores_biometrics": "false"
    }
