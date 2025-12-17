"""
Runtime CORE Lock State Management
-----------------------------------
Manages CORE lock state and enforces immutability.

This module provides:
- CORE_LOCK_STATE flag management
- Runtime enforcement of CORE immutability
- Write protection for CORE files
- Mutation detection and prevention

FAZA 59.5: All violations are logged to audit trail.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import sys

from senti_os.security.violation_logger import get_violation_logger


@dataclass
class CoreLockStatus:
    """CORE lock status information."""
    is_locked: bool
    lock_timestamp: Optional[str]
    lock_confirmation_id: Optional[str]
    protected_paths: List[str]


class CoreLockStateManager:
    """
    Manages CORE lock state and enforces immutability.

    When CORE is locked:
    - Write operations to CORE paths are blocked
    - Mutation engines are disabled
    - Only CORE UPGRADE procedure can modify CORE
    """

    # Define CORE protected paths
    CORE_PATHS = [
        "senti_os/",
        "senti_core_module/senti_core/control_layer/",
        "senti_core_module/senti_core/execution/",
        "docs/governance/",
        "docs/semantics/",
    ]

    def __init__(self, repo_root: str):
        """
        Initialize CORE lock state manager.

        Args:
            repo_root: Absolute path to repository root
        """
        self.repo_root = Path(repo_root)
        self.lock_state_file = self.repo_root / ".core_lock_state.json"

    def is_locked(self) -> bool:
        """
        Check if CORE is currently locked.

        Returns:
            True if CORE is locked, False otherwise
        """
        if not self.lock_state_file.exists():
            return False

        try:
            with open(self.lock_state_file, 'r') as f:
                state = json.load(f)
            return state.get("is_locked", False)
        except (json.JSONDecodeError, IOError):
            return False

    def get_lock_status(self) -> CoreLockStatus:
        """
        Get current CORE lock status.

        Returns:
            CoreLockStatus with current state
        """
        if not self.lock_state_file.exists():
            return CoreLockStatus(
                is_locked=False,
                lock_timestamp=None,
                lock_confirmation_id=None,
                protected_paths=self.CORE_PATHS
            )

        try:
            with open(self.lock_state_file, 'r') as f:
                state = json.load(f)

            return CoreLockStatus(
                is_locked=state.get("is_locked", False),
                lock_timestamp=state.get("lock_timestamp"),
                lock_confirmation_id=state.get("lock_confirmation_id"),
                protected_paths=state.get("protected_paths", self.CORE_PATHS)
            )
        except (json.JSONDecodeError, IOError):
            return CoreLockStatus(
                is_locked=False,
                lock_timestamp=None,
                lock_confirmation_id=None,
                protected_paths=self.CORE_PATHS
            )

    def activate_lock(self, confirmation_id: str) -> None:
        """
        Activate CORE lock.

        Args:
            confirmation_id: FAZA 59 confirmation ID authorizing lock

        Raises:
            RuntimeError: If CORE is already locked
        """
        if self.is_locked():
            raise RuntimeError("CORE is already locked. Cannot lock twice.")

        state = {
            "is_locked": True,
            "lock_timestamp": datetime.utcnow().isoformat() + "Z",
            "lock_confirmation_id": confirmation_id,
            "protected_paths": self.CORE_PATHS
        }

        with open(self.lock_state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def is_core_path(self, file_path: str) -> bool:
        """
        Check if path is within CORE protected paths.

        Args:
            file_path: Relative or absolute path to check

        Returns:
            True if path is CORE protected, False otherwise
        """
        # Convert to relative path if absolute
        path = Path(file_path)
        if path.is_absolute():
            try:
                path = path.relative_to(self.repo_root)
            except ValueError:
                # Path is outside repo
                return False

        path_str = str(path)

        for core_path in self.CORE_PATHS:
            if path_str.startswith(core_path):
                return True

        return False

    def check_write_permission(self, file_path: str) -> tuple[bool, str]:
        """
        Check if write operation is permitted to file.

        Args:
            file_path: Path to file for write operation

        Returns:
            Tuple of (permitted, reason)
            permitted: True if write is allowed, False if blocked
            reason: Explanation of decision
        """
        # If CORE is not locked, all writes are permitted
        if not self.is_locked():
            return True, "CORE is not locked - write permitted"

        # Check if path is CORE protected
        if not self.is_core_path(file_path):
            return True, "Path is not CORE protected - write permitted"

        # CORE is locked and path is protected
        return False, f"CORE is locked - write to CORE path '{file_path}' is prohibited"

    def assert_write_permission(self, file_path: str) -> None:
        """
        Assert that write operation is permitted.

        Args:
            file_path: Path to file for write operation

        Raises:
            PermissionError: If write is not permitted
        """
        permitted, reason = self.check_write_permission(file_path)

        if not permitted:
            status = self.get_lock_status()

            # Log violation to audit trail
            logger = get_violation_logger(str(self.repo_root))
            logger.log_core_mutation_attempt(
                file_path=file_path,
                operation="write",
                lock_timestamp=status.lock_timestamp,
                confirmation_id=status.lock_confirmation_id
            )

            raise PermissionError(
                f"CORE LOCK VIOLATION: {reason}\n"
                f"CORE was locked at: {status.lock_timestamp}\n"
                f"Authorization: {status.lock_confirmation_id}\n"
                f"Modifications require CORE UPGRADE procedure.\n"
                f"Violation logged to audit trail."
            )


class CoreLockError(Exception):
    """Base exception for CORE lock violations."""
    pass


class CoreMutationError(CoreLockError):
    """Exception raised when attempting to mutate locked CORE."""
    pass


def get_core_lock_manager(repo_root: Optional[str] = None) -> CoreLockStateManager:
    """
    Get singleton CORE lock state manager.

    Args:
        repo_root: Repository root path (auto-detected if None)

    Returns:
        CoreLockStateManager instance
    """
    if repo_root is None:
        # Auto-detect repo root
        repo_root = Path(__file__).parent.parent.parent

    return CoreLockStateManager(str(repo_root))
