"""
Minimal ADMIN Session Management
---------------------------------
Provides explicit, time-bound authority for critical operations.

This is NOT a full identity/authentication system.
This is a minimal session mechanism for FAZA 58-60 operations.

FAZA 59.5: Technical stabilization only.
No roles exposed to users.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import secrets


@dataclass
class AdminSession:
    """Represents an active administrative session."""
    session_id: str
    identity: str  # Human-readable identity (not exposed as "role")
    start_time: str  # ISO 8601 timestamp
    expiry_time: str  # ISO 8601 timestamp
    authorized_operations: list  # List of operation types
    active: bool

    def is_expired(self) -> bool:
        """Check if session has expired."""
        if not self.active:
            return True

        expiry = datetime.fromisoformat(self.expiry_time.replace('Z', '+00:00'))
        now = datetime.utcnow()
        return now >= expiry

    def can_perform(self, operation: str) -> bool:
        """Check if session authorizes an operation."""
        if self.is_expired():
            return False
        return operation in self.authorized_operations

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class AdminSessionManager:
    """
    Minimal administrative session manager.

    Provides time-bound authority for critical operations without
    exposing internal role concepts to users.
    """

    DEFAULT_SESSION_DURATION_MINUTES = 30
    CRITICAL_OPERATIONS = [
        "faza58_audit",
        "faza59_confirmation",
        "faza60_lock",
        "core_upgrade",
    ]

    def __init__(self, repo_root: str):
        """
        Initialize session manager.

        Args:
            repo_root: Absolute path to repository root
        """
        self.repo_root = Path(repo_root)
        self.session_file = self.repo_root / ".admin_session.json"
        self.session_log = self.repo_root / ".admin_session_log.jsonl"

        # Ensure log file exists
        if not self.session_log.exists():
            self.session_log.touch()

    def get_active_session(self) -> Optional[AdminSession]:
        """
        Get currently active session.

        Returns:
            AdminSession if active session exists and hasn't expired, None otherwise
        """
        if not self.session_file.exists():
            return None

        try:
            with open(self.session_file, 'r') as f:
                data = json.load(f)

            session = AdminSession(**data)

            # Check if expired
            if session.is_expired():
                return None

            return session

        except (json.JSONDecodeError, IOError, TypeError):
            return None

    def start_session(
        self,
        identity: str,
        duration_minutes: Optional[int] = None
    ) -> AdminSession:
        """
        Start a new administrative session.

        Args:
            identity: Human-readable identity (e.g., "System Architect", "Jane Smith")
            duration_minutes: Session duration (default: 30 minutes)

        Returns:
            AdminSession object

        Raises:
            RuntimeError: If session already active
        """
        # Check for existing active session
        existing = self.get_active_session()
        if existing is not None:
            raise RuntimeError(
                f"Administrative session already active (started at {existing.start_time}).\n"
                f"End the current session before starting a new one."
            )

        # Generate session ID
        session_id = f"admin-{secrets.token_hex(8)}"

        # Calculate expiry
        if duration_minutes is None:
            duration_minutes = self.DEFAULT_SESSION_DURATION_MINUTES

        start_time = datetime.utcnow()
        expiry_time = start_time + timedelta(minutes=duration_minutes)

        # Create session
        session = AdminSession(
            session_id=session_id,
            identity=identity,
            start_time=start_time.isoformat() + "Z",
            expiry_time=expiry_time.isoformat() + "Z",
            authorized_operations=self.CRITICAL_OPERATIONS,
            active=True
        )

        # Save session
        with open(self.session_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)

        # Log session start
        self._log_event({
            "event": "session_start",
            "session_id": session_id,
            "identity": identity,
            "timestamp": session.start_time,
            "duration_minutes": duration_minutes
        })

        return session

    def end_session(self) -> None:
        """
        End the current administrative session.

        Raises:
            RuntimeError: If no active session exists
        """
        session = self.get_active_session()
        if session is None:
            raise RuntimeError("No active administrative session to end.")

        # Mark session as inactive
        session.active = False

        # Save updated session
        with open(self.session_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)

        # Log session end
        self._log_event({
            "event": "session_end",
            "session_id": session.session_id,
            "identity": session.identity,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    def check_authorization(self, operation: str) -> tuple[bool, str]:
        """
        Check if current session authorizes an operation.

        Args:
            operation: Operation to check (e.g., "faza58_audit")

        Returns:
            Tuple of (authorized, reason)
        """
        session = self.get_active_session()

        if session is None:
            return False, "No active administrative session. Start session to proceed."

        if session.is_expired():
            return False, "Administrative session has expired. Start new session."

        if not session.can_perform(operation):
            return False, f"Current session does not authorize operation: {operation}"

        return True, f"Authorized by session {session.session_id}"

    def require_authorization(self, operation: str) -> AdminSession:
        """
        Require authorization for an operation.

        Args:
            operation: Operation to authorize

        Returns:
            Active AdminSession

        Raises:
            PermissionError: If operation is not authorized
        """
        authorized, reason = self.check_authorization(operation)

        if not authorized:
            raise PermissionError(
                f"Operation '{operation}' requires administrative authorization.\n"
                f"Reason: {reason}\n"
                f"Start session with: python senti_os/security/admin_session/start_session.py"
            )

        return self.get_active_session()

    def get_session_info(self) -> dict:
        """
        Get human-readable session information.

        Returns:
            Dictionary with session status and details
        """
        session = self.get_active_session()

        if session is None:
            return {
                "status": "NO_SESSION",
                "message": "No active administrative session",
                "session_file": str(self.session_file)
            }

        time_remaining = self._calculate_time_remaining(session)

        return {
            "status": "ACTIVE",
            "session_id": session.session_id,
            "identity": session.identity,
            "start_time": session.start_time,
            "expiry_time": session.expiry_time,
            "time_remaining": time_remaining,
            "authorized_operations": session.authorized_operations
        }

    def _calculate_time_remaining(self, session: AdminSession) -> str:
        """Calculate human-readable time remaining."""
        expiry = datetime.fromisoformat(session.expiry_time.replace('Z', '+00:00'))
        now = datetime.utcnow()
        remaining = expiry - now

        if remaining.total_seconds() <= 0:
            return "EXPIRED"

        minutes = int(remaining.total_seconds() / 60)
        seconds = int(remaining.total_seconds() % 60)

        return f"{minutes}m {seconds}s"

    def _log_event(self, event: dict) -> None:
        """Log event to audit trail."""
        with open(self.session_log, 'a') as f:
            f.write(json.dumps(event) + "\n")


def get_session_manager(repo_root: Optional[str] = None) -> AdminSessionManager:
    """
    Get singleton session manager.

    Args:
        repo_root: Repository root path (auto-detected if None)

    Returns:
        AdminSessionManager instance
    """
    if repo_root is None:
        # Auto-detect repo root
        repo_root = Path(__file__).parent.parent.parent.parent

    return AdminSessionManager(str(repo_root))
