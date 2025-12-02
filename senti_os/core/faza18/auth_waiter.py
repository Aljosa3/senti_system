"""
FAZA 18 - Authentication Waiter Module

This module waits for external biometric verification or other authentication
steps to complete. It provides timeout management, retry logic, and safe abort
mechanisms.

CRITICAL PRIVACY RULE:
    This module NEVER processes biometric data.
    It only WAITS for external authentication to complete.
    All biometric processing happens externally.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import time
import logging


class WaitState(Enum):
    """States of the authentication wait process."""
    IDLE = "idle"
    WAITING = "waiting"
    CHECKING = "checking"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    ABORTED = "aborted"
    ERROR = "error"


class WaitReason(Enum):
    """Reasons why we are waiting."""
    BIOMETRIC_EXTERNAL = "biometric_external"  # External biometric auth
    OTP_ENTRY = "otp_entry"  # User entering OTP
    EMAIL_VERIFICATION = "email_verification"  # Email code verification
    SMS_VERIFICATION = "sms_verification"  # SMS code verification
    TWO_FACTOR = "two_factor"  # Two-factor authentication
    MANUAL_APPROVAL = "manual_approval"  # Manual approval step
    OTHER = "other"


@dataclass
class WaitResult:
    """Result of an authentication wait operation."""
    wait_id: str
    state: WaitState
    reason: WaitReason
    success: bool
    message: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: float
    retry_count: int
    additional_data: Dict[str, Any]


class AuthWaiter:
    """
    Manages waiting for external authentication steps to complete.

    This class provides a state machine for waiting on external authentication
    processes (like biometric verification) that SENTI OS cannot and will not
    process internally.

    PRIVACY GUARANTEE:
        This waiter NEVER processes biometric data.
        It only monitors the completion state of external processes.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the authentication waiter.

        Args:
            logger: Optional logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)
        self._active_waits: Dict[str, Dict[str, Any]] = {}
        self._wait_counter = 0

    def start_wait(
        self,
        reason: WaitReason,
        timeout_seconds: int = 120,
        check_interval: float = 1.0,
        max_retries: int = 3,
        wait_message: Optional[str] = None
    ) -> str:
        """
        Start waiting for an authentication step to complete.

        Args:
            reason: Why we are waiting.
            timeout_seconds: Maximum time to wait before timeout.
            check_interval: How often to check completion (seconds).
            max_retries: Maximum number of retry attempts.
            wait_message: Optional message to display to user.

        Returns:
            Wait ID for tracking this wait operation.
        """
        wait_id = self._generate_wait_id()

        wait_data = {
            "wait_id": wait_id,
            "reason": reason,
            "state": WaitState.WAITING,
            "timeout_seconds": timeout_seconds,
            "check_interval": check_interval,
            "max_retries": max_retries,
            "retry_count": 0,
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "message": wait_message or self._get_default_message(reason),
            "checker_function": None,
            "additional_data": {}
        }

        self._active_waits[wait_id] = wait_data

        self.logger.info(
            f"Started wait {wait_id} for {reason.value} "
            f"(timeout: {timeout_seconds}s)"
        )

        return wait_id

    def register_completion_checker(
        self,
        wait_id: str,
        checker_function: Callable[[], bool]
    ) -> bool:
        """
        Register a function to check if authentication is complete.

        Args:
            wait_id: The wait operation ID.
            checker_function: Function that returns True when auth is complete.

        Returns:
            True if registered successfully, False if wait_id not found.
        """
        if wait_id not in self._active_waits:
            return False

        self._active_waits[wait_id]["checker_function"] = checker_function
        return True

    def wait_for_completion(self, wait_id: str) -> WaitResult:
        """
        Block and wait for authentication to complete.

        Args:
            wait_id: The wait operation ID.

        Returns:
            WaitResult with the outcome.
        """
        if wait_id not in self._active_waits:
            return self._create_error_result(
                wait_id,
                "Wait ID not found"
            )

        wait_data = self._active_waits[wait_id]
        start_time = wait_data["started_at"]
        timeout = timedelta(seconds=wait_data["timeout_seconds"])
        check_interval = wait_data["check_interval"]
        checker = wait_data["checker_function"]

        while True:
            # Check timeout
            elapsed = datetime.utcnow() - start_time
            if elapsed > timeout:
                return self._handle_timeout(wait_id)

            # Update state
            wait_data["state"] = WaitState.CHECKING

            # Check if complete
            if checker and checker():
                return self._handle_completion(wait_id, True, "Authentication completed")

            # Check for abort signal
            if wait_data.get("abort_requested", False):
                return self._handle_abort(wait_id)

            # Wait before next check
            time.sleep(check_interval)

    def check_status(self, wait_id: str) -> Optional[WaitState]:
        """
        Check the current status of a wait operation (non-blocking).

        Args:
            wait_id: The wait operation ID.

        Returns:
            Current WaitState, or None if not found.
        """
        if wait_id not in self._active_waits:
            return None

        return self._active_waits[wait_id]["state"]

    def abort_wait(self, wait_id: str, reason: str = "User requested abort") -> bool:
        """
        Request abortion of a wait operation.

        Args:
            wait_id: The wait operation ID.
            reason: Reason for aborting.

        Returns:
            True if abort requested, False if wait_id not found.
        """
        if wait_id not in self._active_waits:
            return False

        self._active_waits[wait_id]["abort_requested"] = True
        self._active_waits[wait_id]["abort_reason"] = reason

        self.logger.info(f"Abort requested for wait {wait_id}: {reason}")

        return True

    def retry_wait(self, wait_id: str) -> bool:
        """
        Retry a timed-out or failed wait operation.

        Args:
            wait_id: The wait operation ID.

        Returns:
            True if retry initiated, False if max retries exceeded or not found.
        """
        if wait_id not in self._active_waits:
            return False

        wait_data = self._active_waits[wait_id]

        if wait_data["retry_count"] >= wait_data["max_retries"]:
            self.logger.warning(
                f"Cannot retry wait {wait_id}: max retries exceeded"
            )
            return False

        # Increment retry count
        wait_data["retry_count"] += 1

        # Reset state and timing
        wait_data["state"] = WaitState.WAITING
        wait_data["started_at"] = datetime.utcnow()
        wait_data["completed_at"] = None

        self.logger.info(
            f"Retrying wait {wait_id} (attempt {wait_data['retry_count']})"
        )

        return True

    def set_additional_data(self, wait_id: str, key: str, value: Any) -> bool:
        """
        Set additional data for a wait operation.

        Args:
            wait_id: The wait operation ID.
            key: Data key.
            value: Data value.

        Returns:
            True if set successfully, False if wait_id not found.
        """
        if wait_id not in self._active_waits:
            return False

        self._active_waits[wait_id]["additional_data"][key] = value
        return True

    def get_wait_message(self, wait_id: str) -> Optional[str]:
        """
        Get the current wait message for display to user.

        Args:
            wait_id: The wait operation ID.

        Returns:
            Wait message string, or None if not found.
        """
        if wait_id not in self._active_waits:
            return None

        wait_data = self._active_waits[wait_id]
        return wait_data["message"]

    def update_wait_message(self, wait_id: str, message: str) -> bool:
        """
        Update the wait message.

        Args:
            wait_id: The wait operation ID.
            message: New message to display.

        Returns:
            True if updated, False if wait_id not found.
        """
        if wait_id not in self._active_waits:
            return False

        self._active_waits[wait_id]["message"] = message
        return True

    def cleanup_wait(self, wait_id: str):
        """
        Clean up a completed wait operation.

        Args:
            wait_id: The wait operation ID to clean up.
        """
        if wait_id in self._active_waits:
            del self._active_waits[wait_id]
            self.logger.debug(f"Cleaned up wait {wait_id}")

    def cleanup_old_waits(self, max_age_minutes: int = 30):
        """
        Clean up old completed or timed-out wait operations.

        Args:
            max_age_minutes: Maximum age in minutes before cleanup.
        """
        now = datetime.utcnow()
        to_cleanup = []

        for wait_id, wait_data in self._active_waits.items():
            age = now - wait_data["started_at"]
            if age > timedelta(minutes=max_age_minutes):
                to_cleanup.append(wait_id)

        for wait_id in to_cleanup:
            self.cleanup_wait(wait_id)

    def get_active_wait_count(self) -> int:
        """
        Get the number of active wait operations.

        Returns:
            Count of active waits.
        """
        return len(self._active_waits)

    def _generate_wait_id(self) -> str:
        """
        Generate a unique wait ID.

        Returns:
            Unique wait ID string.
        """
        self._wait_counter += 1
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        return f"wait_{timestamp}_{self._wait_counter}"

    def _get_default_message(self, reason: WaitReason) -> str:
        """
        Get default wait message based on reason.

        Args:
            reason: The wait reason.

        Returns:
            Default message string.
        """
        messages = {
            WaitReason.BIOMETRIC_EXTERNAL: (
                "Waiting for external biometric authentication... "
                "Please complete biometric verification on the external platform."
            ),
            WaitReason.OTP_ENTRY: (
                "Waiting for OTP entry... "
                "Please enter the code from your authenticator app."
            ),
            WaitReason.EMAIL_VERIFICATION: (
                "Waiting for email verification... "
                "Please check your email and enter the verification code."
            ),
            WaitReason.SMS_VERIFICATION: (
                "Waiting for SMS verification... "
                "Please enter the code sent to your phone."
            ),
            WaitReason.TWO_FACTOR: (
                "Waiting for two-factor authentication... "
                "Please complete the second factor."
            ),
            WaitReason.MANUAL_APPROVAL: (
                "Waiting for manual approval... "
                "Please complete the required approval step."
            )
        }

        return messages.get(reason, "Waiting for authentication to complete...")

    def _handle_completion(
        self,
        wait_id: str,
        success: bool,
        message: str
    ) -> WaitResult:
        """
        Handle successful completion of wait.

        Args:
            wait_id: The wait operation ID.
            success: Whether authentication was successful.
            message: Completion message.

        Returns:
            WaitResult with completion details.
        """
        wait_data = self._active_waits[wait_id]
        wait_data["state"] = WaitState.COMPLETED
        wait_data["completed_at"] = datetime.utcnow()

        duration = (wait_data["completed_at"] - wait_data["started_at"]).total_seconds()

        self.logger.info(
            f"Wait {wait_id} completed: {message} (duration: {duration:.2f}s)"
        )

        return WaitResult(
            wait_id=wait_id,
            state=WaitState.COMPLETED,
            reason=wait_data["reason"],
            success=success,
            message=message,
            started_at=wait_data["started_at"],
            completed_at=wait_data["completed_at"],
            duration_seconds=duration,
            retry_count=wait_data["retry_count"],
            additional_data=wait_data["additional_data"]
        )

    def _handle_timeout(self, wait_id: str) -> WaitResult:
        """
        Handle wait timeout.

        Args:
            wait_id: The wait operation ID.

        Returns:
            WaitResult with timeout details.
        """
        wait_data = self._active_waits[wait_id]
        wait_data["state"] = WaitState.TIMEOUT
        wait_data["completed_at"] = datetime.utcnow()

        duration = (wait_data["completed_at"] - wait_data["started_at"]).total_seconds()

        self.logger.warning(
            f"Wait {wait_id} timed out after {duration:.2f}s"
        )

        return WaitResult(
            wait_id=wait_id,
            state=WaitState.TIMEOUT,
            reason=wait_data["reason"],
            success=False,
            message="Authentication wait timed out",
            started_at=wait_data["started_at"],
            completed_at=wait_data["completed_at"],
            duration_seconds=duration,
            retry_count=wait_data["retry_count"],
            additional_data=wait_data["additional_data"]
        )

    def _handle_abort(self, wait_id: str) -> WaitResult:
        """
        Handle wait abortion.

        Args:
            wait_id: The wait operation ID.

        Returns:
            WaitResult with abort details.
        """
        wait_data = self._active_waits[wait_id]
        wait_data["state"] = WaitState.ABORTED
        wait_data["completed_at"] = datetime.utcnow()

        duration = (wait_data["completed_at"] - wait_data["started_at"]).total_seconds()

        abort_reason = wait_data.get("abort_reason", "Unknown reason")

        self.logger.info(
            f"Wait {wait_id} aborted: {abort_reason}"
        )

        return WaitResult(
            wait_id=wait_id,
            state=WaitState.ABORTED,
            reason=wait_data["reason"],
            success=False,
            message=f"Authentication wait aborted: {abort_reason}",
            started_at=wait_data["started_at"],
            completed_at=wait_data["completed_at"],
            duration_seconds=duration,
            retry_count=wait_data["retry_count"],
            additional_data=wait_data["additional_data"]
        )

    def _create_error_result(self, wait_id: str, error_message: str) -> WaitResult:
        """
        Create an error result.

        Args:
            wait_id: The wait operation ID.
            error_message: Error message.

        Returns:
            WaitResult with error details.
        """
        now = datetime.utcnow()

        return WaitResult(
            wait_id=wait_id,
            state=WaitState.ERROR,
            reason=WaitReason.OTHER,
            success=False,
            message=error_message,
            started_at=now,
            completed_at=now,
            duration_seconds=0.0,
            retry_count=0,
            additional_data={}
        )


def get_info() -> Dict[str, str]:
    """
    Get module information.

    Returns:
        Dictionary with module metadata.
    """
    return {
        "module": "auth_waiter",
        "faza": "18",
        "version": "1.0.0",
        "description": "Waits for external authentication to complete (no biometric processing)",
        "privacy_compliant": "true",
        "processes_biometrics": "false"
    }
