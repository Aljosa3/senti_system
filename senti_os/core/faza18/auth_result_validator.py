"""
FAZA 18 - Authentication Result Validator

This module validates authentication results (success/failure only) and ensures
the authentication flow is complete before returning control to the system.

CRITICAL PRIVACY RULE:
    This module validates ONLY non-biometric results.
    It checks success/failure states, NOT biometric data.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re


class AuthResultStatus(Enum):
    """Status of authentication result."""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    REQUIRES_ADDITIONAL_STEP = "requires_additional_step"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class ValidationLevel(Enum):
    """Level of validation to perform."""
    BASIC = "basic"  # Just check success/failure
    STANDARD = "standard"  # Check success, session info, expiry
    STRICT = "strict"  # Full validation including security checks


@dataclass
class AuthResult:
    """Container for authentication result data."""
    result_id: str
    status: AuthResultStatus
    timestamp: datetime
    session_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    user_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata if None."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ValidationResult:
    """Result of validation process."""
    is_valid: bool
    status: AuthResultStatus
    message: str
    warnings: List[str]
    errors: List[str]
    validated_at: datetime


class AuthResultValidator:
    """
    Validates authentication results to ensure they are complete and valid.

    This validator checks that authentication flows have completed successfully
    and that all necessary data is present before returning control.

    PRIVACY GUARANTEE:
        Validates ONLY success/failure states and session data.
        NEVER processes biometric data.
    """

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        Initialize the authentication result validator.

        Args:
            validation_level: Level of validation to perform.
        """
        self.validation_level = validation_level
        self._validation_rules = self._initialize_validation_rules()

    def _initialize_validation_rules(self) -> Dict[ValidationLevel, List[str]]:
        """
        Initialize validation rules for each level.

        Returns:
            Dictionary mapping validation levels to required checks.
        """
        return {
            ValidationLevel.BASIC: [
                "check_status_present",
                "check_status_valid"
            ],
            ValidationLevel.STANDARD: [
                "check_status_present",
                "check_status_valid",
                "check_session_token",
                "check_timestamp"
            ],
            ValidationLevel.STRICT: [
                "check_status_present",
                "check_status_valid",
                "check_session_token",
                "check_timestamp",
                "check_expiry",
                "check_security_indicators",
                "check_token_format"
            ]
        }

    def validate_result(
        self,
        auth_result: AuthResult,
        expected_status: Optional[AuthResultStatus] = None
    ) -> ValidationResult:
        """
        Validate an authentication result.

        Args:
            auth_result: The authentication result to validate.
            expected_status: Optional expected status to check against.

        Returns:
            ValidationResult with validation outcome.
        """
        warnings = []
        errors = []

        # Get validation rules for current level
        rules = self._validation_rules.get(
            self.validation_level,
            self._validation_rules[ValidationLevel.BASIC]
        )

        # Run each validation check
        for rule_name in rules:
            rule_method = getattr(self, f"_{rule_name}", None)
            if rule_method:
                rule_result = rule_method(auth_result)
                if not rule_result["valid"]:
                    if rule_result.get("is_error", True):
                        errors.append(rule_result["message"])
                    else:
                        warnings.append(rule_result["message"])

        # Check expected status if provided
        if expected_status and auth_result.status != expected_status:
            errors.append(
                f"Expected status {expected_status.value}, "
                f"got {auth_result.status.value}"
            )

        # Determine overall validity
        is_valid = len(errors) == 0

        # Generate summary message
        if is_valid:
            message = "Authentication result is valid"
        else:
            message = f"Authentication result validation failed: {len(errors)} error(s)"

        return ValidationResult(
            is_valid=is_valid,
            status=auth_result.status,
            message=message,
            warnings=warnings,
            errors=errors,
            validated_at=datetime.utcnow()
        )

    def validate_success(self, auth_result: AuthResult) -> ValidationResult:
        """
        Validate that authentication was successful and complete.

        Args:
            auth_result: The authentication result to validate.

        Returns:
            ValidationResult indicating if success is valid.
        """
        return self.validate_result(auth_result, AuthResultStatus.SUCCESS)

    def validate_failure(self, auth_result: AuthResult) -> ValidationResult:
        """
        Validate that authentication failure is properly documented.

        Args:
            auth_result: The authentication result to validate.

        Returns:
            ValidationResult indicating if failure is properly documented.
        """
        result = self.validate_result(auth_result, AuthResultStatus.FAILURE)

        # For failures, check that error message is present
        if not auth_result.error_message:
            result.warnings.append("Failure result missing error message")

        return result

    def is_flow_complete(self, auth_result: AuthResult) -> bool:
        """
        Check if authentication flow is complete.

        Args:
            auth_result: The authentication result to check.

        Returns:
            True if flow is complete, False if additional steps needed.
        """
        # Flow is complete if status is SUCCESS or FAILURE
        complete_statuses = {
            AuthResultStatus.SUCCESS,
            AuthResultStatus.FAILURE,
            AuthResultStatus.INVALID
        }

        return auth_result.status in complete_statuses

    def requires_additional_step(self, auth_result: AuthResult) -> bool:
        """
        Check if authentication requires an additional step.

        Args:
            auth_result: The authentication result to check.

        Returns:
            True if additional step is required.
        """
        return auth_result.status == AuthResultStatus.REQUIRES_ADDITIONAL_STEP

    def extract_session_info(self, auth_result: AuthResult) -> Optional[Dict[str, Any]]:
        """
        Extract session information from a successful authentication result.

        Args:
            auth_result: The authentication result.

        Returns:
            Dictionary with session info, or None if not available.
        """
        if auth_result.status != AuthResultStatus.SUCCESS:
            return None

        session_info = {}

        if auth_result.session_token:
            session_info["session_token"] = auth_result.session_token

        if auth_result.refresh_token:
            session_info["refresh_token"] = auth_result.refresh_token

        if auth_result.expires_at:
            session_info["expires_at"] = auth_result.expires_at.isoformat()

        if auth_result.user_info:
            session_info["user_info"] = auth_result.user_info

        return session_info if session_info else None

    # Validation rule methods

    def _check_status_present(self, auth_result: AuthResult) -> Dict[str, Any]:
        """Check that status field is present."""
        if auth_result.status is None:
            return {
                "valid": False,
                "is_error": True,
                "message": "Authentication result missing status field"
            }
        return {"valid": True}

    def _check_status_valid(self, auth_result: AuthResult) -> Dict[str, Any]:
        """Check that status is a valid enum value."""
        if not isinstance(auth_result.status, AuthResultStatus):
            return {
                "valid": False,
                "is_error": True,
                "message": "Invalid authentication status"
            }
        return {"valid": True}

    def _check_session_token(self, auth_result: AuthResult) -> Dict[str, Any]:
        """Check that session token is present for successful auth."""
        if auth_result.status == AuthResultStatus.SUCCESS:
            if not auth_result.session_token:
                return {
                    "valid": False,
                    "is_error": False,
                    "message": "Successful authentication missing session token"
                }
        return {"valid": True}

    def _check_timestamp(self, auth_result: AuthResult) -> Dict[str, Any]:
        """Check that timestamp is present and valid."""
        if not auth_result.timestamp:
            return {
                "valid": False,
                "is_error": True,
                "message": "Authentication result missing timestamp"
            }

        if not isinstance(auth_result.timestamp, datetime):
            return {
                "valid": False,
                "is_error": True,
                "message": "Invalid timestamp format"
            }

        # Check if timestamp is in the future (suspicious)
        if auth_result.timestamp > datetime.utcnow():
            return {
                "valid": False,
                "is_error": False,
                "message": "Authentication timestamp is in the future"
            }

        return {"valid": True}

    def _check_expiry(self, auth_result: AuthResult) -> Dict[str, Any]:
        """Check that expiry information is present and valid."""
        if auth_result.status == AuthResultStatus.SUCCESS:
            if auth_result.expires_at:
                # Check if already expired
                if auth_result.expires_at < datetime.utcnow():
                    return {
                        "valid": False,
                        "is_error": True,
                        "message": "Session token already expired"
                    }
            else:
                return {
                    "valid": False,
                    "is_error": False,
                    "message": "Session missing expiration time"
                }

        return {"valid": True}

    def _check_security_indicators(self, auth_result: AuthResult) -> Dict[str, Any]:
        """Check for security indicators in the result."""
        warnings = []

        # Check if metadata has security flags
        if auth_result.metadata:
            if not auth_result.metadata.get("secure_connection", True):
                warnings.append("Authentication may not have used secure connection")

            if auth_result.metadata.get("weak_encryption", False):
                warnings.append("Weak encryption detected")

        if warnings:
            return {
                "valid": False,
                "is_error": False,
                "message": "; ".join(warnings)
            }

        return {"valid": True}

    def _check_token_format(self, auth_result: AuthResult) -> Dict[str, Any]:
        """Check that token format looks valid."""
        if auth_result.status == AuthResultStatus.SUCCESS and auth_result.session_token:
            token = auth_result.session_token

            # Basic format checks
            if len(token) < 20:
                return {
                    "valid": False,
                    "is_error": False,
                    "message": "Session token appears too short"
                }

            # Check for suspicious patterns
            if token.count(" ") > 0:
                return {
                    "valid": False,
                    "is_error": False,
                    "message": "Session token contains spaces (suspicious)"
                }

        return {"valid": True}

    def get_validation_summary(self, auth_result: AuthResult) -> Dict[str, Any]:
        """
        Get a comprehensive validation summary.

        Args:
            auth_result: The authentication result to summarize.

        Returns:
            Dictionary with validation summary.
        """
        validation_result = self.validate_result(auth_result)

        return {
            "result_id": auth_result.result_id,
            "status": auth_result.status.value,
            "is_valid": validation_result.is_valid,
            "is_complete": self.is_flow_complete(auth_result),
            "requires_additional_step": self.requires_additional_step(auth_result),
            "validation_level": self.validation_level.value,
            "error_count": len(validation_result.errors),
            "warning_count": len(validation_result.warnings),
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "validated_at": validation_result.validated_at.isoformat()
        }


def create_auth_result(
    result_id: str,
    status: AuthResultStatus,
    session_token: Optional[str] = None,
    error_message: Optional[str] = None,
    **kwargs
) -> AuthResult:
    """
    Helper function to create an AuthResult object.

    Args:
        result_id: Unique identifier for this result.
        status: Authentication status.
        session_token: Optional session token.
        error_message: Optional error message.
        **kwargs: Additional fields.

    Returns:
        AuthResult object.
    """
    return AuthResult(
        result_id=result_id,
        status=status,
        timestamp=datetime.utcnow(),
        session_token=session_token,
        error_message=error_message,
        **kwargs
    )


def get_info() -> Dict[str, str]:
    """
    Get module information.

    Returns:
        Dictionary with module metadata.
    """
    return {
        "module": "auth_result_validator",
        "faza": "18",
        "version": "1.0.0",
        "description": "Validates authentication results (non-biometric only)",
        "privacy_compliant": "true",
        "processes_biometrics": "false"
    }
