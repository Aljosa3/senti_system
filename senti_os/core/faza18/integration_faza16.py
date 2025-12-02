"""
FAZA 18 - Integration with FAZA 16 (LLM Control Layer)

This module provides integration between FAZA 18 Biometric-Flow Handling
and FAZA 16 LLM Control Layer, allowing LLM-driven authentication flows.

CRITICAL PRIVACY RULE:
    LLM integration NEVER exposes biometric data or passwords.
    Only high-level authentication commands and status are shared.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

# Import FAZA 18 components
from senti_os.core.faza18.platform_detector import (
    PlatformDetector, PlatformInfo, AuthMethod
)
from senti_os.core.faza18.auth_request_manager import (
    AuthRequestManager, AuthRequest
)
from senti_os.core.faza18.auth_waiter import AuthWaiter, WaitReason, WaitResult
from senti_os.core.faza18.auth_result_validator import (
    AuthResultValidator, AuthResult, AuthResultStatus, ValidationResult
)
from senti_os.core.faza18.secure_session_manager import (
    SecureSessionManager, Session
)
from senti_os.core.faza18.policy_enforcer import PolicyEnforcer


class LLMAuthCommand(Enum):
    """Commands that LLM can issue for authentication."""
    DETECT_PLATFORM = "detect_platform"
    PREPARE_AUTH_REQUEST = "prepare_auth_request"
    WAIT_FOR_EXTERNAL_AUTH = "wait_for_external_auth"
    VALIDATE_AUTH_RESULT = "validate_auth_result"
    GET_SESSION_STATUS = "get_session_status"
    REVOKE_SESSION = "revoke_session"


@dataclass
class LLMAuthResponse:
    """Response to LLM authentication command."""
    command: LLMAuthCommand
    success: bool
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    requires_user_action: bool = False
    user_action_description: Optional[str] = None


class FAZA16Integration:
    """
    Integration layer between FAZA 18 and FAZA 16 LLM Control Layer.

    This allows LLMs to orchestrate authentication flows through
    high-level commands while maintaining strict privacy boundaries.

    PRIVACY GUARANTEE:
        - LLM NEVER receives passwords or biometric data
        - LLM only receives high-level status and commands
        - All sensitive operations logged and audited
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize FAZA 16 integration.

        Args:
            logger: Optional logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)

        # Initialize FAZA 18 components
        self.platform_detector = PlatformDetector()
        self.auth_request_manager = AuthRequestManager()
        self.auth_waiter = AuthWaiter(logger=self.logger)
        self.auth_validator = AuthResultValidator()
        self.session_manager = SecureSessionManager()
        self.policy_enforcer = PolicyEnforcer(logger=self.logger)

        self.logger.info("FAZA 16 Integration initialized")

    def execute_llm_command(
        self,
        command: LLMAuthCommand,
        parameters: Dict[str, Any]
    ) -> LLMAuthResponse:
        """
        Execute an LLM authentication command.

        Args:
            command: The command to execute.
            parameters: Command parameters.

        Returns:
            LLMAuthResponse with result.
        """
        # Log the command
        self.policy_enforcer.log_operation(
            operation=f"llm_command_{command.value}",
            operation_type="llm_integration",
            success=True,
            details={"command": command.value}
        )

        # Route to appropriate handler
        handlers = {
            LLMAuthCommand.DETECT_PLATFORM: self._handle_detect_platform,
            LLMAuthCommand.PREPARE_AUTH_REQUEST: self._handle_prepare_auth_request,
            LLMAuthCommand.WAIT_FOR_EXTERNAL_AUTH: self._handle_wait_for_external_auth,
            LLMAuthCommand.VALIDATE_AUTH_RESULT: self._handle_validate_auth_result,
            LLMAuthCommand.GET_SESSION_STATUS: self._handle_get_session_status,
            LLMAuthCommand.REVOKE_SESSION: self._handle_revoke_session
        }

        handler = handlers.get(command)

        if not handler:
            return LLMAuthResponse(
                command=command,
                success=False,
                message=f"Unknown command: {command.value}",
                data={},
                timestamp=datetime.utcnow()
            )

        try:
            return handler(parameters)
        except Exception as e:
            self.logger.error(f"Error executing LLM command {command.value}: {e}")
            return LLMAuthResponse(
                command=command,
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow()
            )

    def _handle_detect_platform(
        self,
        parameters: Dict[str, Any]
    ) -> LLMAuthResponse:
        """
        Handle DETECT_PLATFORM command.

        Args:
            parameters: Must contain 'url' and optionally 'page_content'.

        Returns:
            LLMAuthResponse with platform info.
        """
        url = parameters.get("url")

        if not url:
            return LLMAuthResponse(
                command=LLMAuthCommand.DETECT_PLATFORM,
                success=False,
                message="Missing required parameter: url",
                data={},
                timestamp=datetime.utcnow()
            )

        page_content = parameters.get("page_content")

        # Detect platform
        platform_info = self.platform_detector.detect_platform(url, page_content)

        # Prepare LLM-safe response
        llm_data = {
            "platform_type": platform_info.platform_type.value,
            "platform_name": platform_info.platform_name,
            "url": platform_info.url,
            "required_auth_methods": [m.value for m in platform_info.required_auth_methods],
            "requires_biometric": platform_info.requires_biometric,
            "supports_password_only": platform_info.supports_password_only,
            "estimated_wait_time": platform_info.estimated_wait_time,
            "notes": platform_info.notes
        }

        message = f"Platform detected: {platform_info.platform_name}"

        if platform_info.requires_biometric:
            message += " (BIOMETRIC REQUIRED - external handling needed)"

        return LLMAuthResponse(
            command=LLMAuthCommand.DETECT_PLATFORM,
            success=True,
            message=message,
            data=llm_data,
            timestamp=datetime.utcnow(),
            requires_user_action=platform_info.requires_biometric,
            user_action_description=(
                "Biometric authentication required on external platform"
                if platform_info.requires_biometric else None
            )
        )

    def _handle_prepare_auth_request(
        self,
        parameters: Dict[str, Any]
    ) -> LLMAuthResponse:
        """
        Handle PREPARE_AUTH_REQUEST command.

        Args:
            parameters: Must contain 'url', 'username', 'password'.

        Returns:
            LLMAuthResponse with request ID.
        """
        url = parameters.get("url")
        username = parameters.get("username")
        password = parameters.get("password")

        if not all([url, username, password]):
            return LLMAuthResponse(
                command=LLMAuthCommand.PREPARE_AUTH_REQUEST,
                success=False,
                message="Missing required parameters: url, username, password",
                data={},
                timestamp=datetime.utcnow()
            )

        # Create auth request
        auth_request = self.auth_request_manager.create_auth_request(
            url=url,
            username=username,
            password=password,
            template=parameters.get("template", "standard_form")
        )

        # Return only request ID to LLM (NOT credentials)
        return LLMAuthResponse(
            command=LLMAuthCommand.PREPARE_AUTH_REQUEST,
            success=True,
            message="Authentication request prepared",
            data={
                "request_id": auth_request.request_id,
                "url": auth_request.url,
                "method": auth_request.method.value
            },
            timestamp=datetime.utcnow()
        )

    def _handle_wait_for_external_auth(
        self,
        parameters: Dict[str, Any]
    ) -> LLMAuthResponse:
        """
        Handle WAIT_FOR_EXTERNAL_AUTH command.

        Args:
            parameters: Must contain 'reason', optionally 'timeout_seconds'.

        Returns:
            LLMAuthResponse with wait ID.
        """
        reason_str = parameters.get("reason", "biometric_external")

        try:
            reason = WaitReason(reason_str)
        except ValueError:
            reason = WaitReason.OTHER

        timeout = parameters.get("timeout_seconds", 120)

        # Start wait
        wait_id = self.auth_waiter.start_wait(
            reason=reason,
            timeout_seconds=timeout
        )

        return LLMAuthResponse(
            command=LLMAuthCommand.WAIT_FOR_EXTERNAL_AUTH,
            success=True,
            message=f"Waiting for external authentication ({reason.value})",
            data={
                "wait_id": wait_id,
                "reason": reason.value,
                "timeout_seconds": timeout,
                "wait_message": self.auth_waiter.get_wait_message(wait_id)
            },
            timestamp=datetime.utcnow(),
            requires_user_action=True,
            user_action_description=(
                "Please complete authentication on the external platform"
            )
        )

    def _handle_validate_auth_result(
        self,
        parameters: Dict[str, Any]
    ) -> LLMAuthResponse:
        """
        Handle VALIDATE_AUTH_RESULT command.

        Args:
            parameters: Must contain 'result_id', 'status', optionally 'session_token'.

        Returns:
            LLMAuthResponse with validation result.
        """
        result_id = parameters.get("result_id")
        status_str = parameters.get("status")

        if not result_id or not status_str:
            return LLMAuthResponse(
                command=LLMAuthCommand.VALIDATE_AUTH_RESULT,
                success=False,
                message="Missing required parameters: result_id, status",
                data={},
                timestamp=datetime.utcnow()
            )

        try:
            status = AuthResultStatus(status_str)
        except ValueError:
            status = AuthResultStatus.UNKNOWN

        # Create auth result
        auth_result = AuthResult(
            result_id=result_id,
            status=status,
            timestamp=datetime.utcnow(),
            session_token=parameters.get("session_token")
        )

        # Validate
        validation = self.auth_validator.validate_result(auth_result)

        # Create session if successful
        session_id = None
        if validation.is_valid and status == AuthResultStatus.SUCCESS:
            if auth_result.session_token:
                session = self.session_manager.create_session(
                    platform_url=parameters.get("platform_url", "unknown"),
                    session_token=auth_result.session_token,
                    user_identifier=parameters.get("user_identifier")
                )
                session_id = session.session_id

        return LLMAuthResponse(
            command=LLMAuthCommand.VALIDATE_AUTH_RESULT,
            success=validation.is_valid,
            message=validation.message,
            data={
                "result_id": result_id,
                "is_valid": validation.is_valid,
                "status": status.value,
                "session_id": session_id,
                "warnings": validation.warnings,
                "errors": validation.errors
            },
            timestamp=datetime.utcnow()
        )

    def _handle_get_session_status(
        self,
        parameters: Dict[str, Any]
    ) -> LLMAuthResponse:
        """
        Handle GET_SESSION_STATUS command.

        Args:
            parameters: Must contain 'session_id'.

        Returns:
            LLMAuthResponse with session status.
        """
        session_id = parameters.get("session_id")

        if not session_id:
            return LLMAuthResponse(
                command=LLMAuthCommand.GET_SESSION_STATUS,
                success=False,
                message="Missing required parameter: session_id",
                data={},
                timestamp=datetime.utcnow()
            )

        # Get session info (safe for LLM)
        session_info = self.session_manager.get_session_info(session_id)

        if not session_info:
            return LLMAuthResponse(
                command=LLMAuthCommand.GET_SESSION_STATUS,
                success=False,
                message="Session not found",
                data={},
                timestamp=datetime.utcnow()
            )

        return LLMAuthResponse(
            command=LLMAuthCommand.GET_SESSION_STATUS,
            success=True,
            message="Session status retrieved",
            data=session_info,
            timestamp=datetime.utcnow()
        )

    def _handle_revoke_session(
        self,
        parameters: Dict[str, Any]
    ) -> LLMAuthResponse:
        """
        Handle REVOKE_SESSION command.

        Args:
            parameters: Must contain 'session_id'.

        Returns:
            LLMAuthResponse with revocation result.
        """
        session_id = parameters.get("session_id")

        if not session_id:
            return LLMAuthResponse(
                command=LLMAuthCommand.REVOKE_SESSION,
                success=False,
                message="Missing required parameter: session_id",
                data={},
                timestamp=datetime.utcnow()
            )

        # Revoke session
        success = self.session_manager.revoke_session(session_id)

        return LLMAuthResponse(
            command=LLMAuthCommand.REVOKE_SESSION,
            success=success,
            message="Session revoked" if success else "Session not found",
            data={"session_id": session_id, "revoked": success},
            timestamp=datetime.utcnow()
        )

    def get_llm_capabilities(self) -> Dict[str, Any]:
        """
        Get capabilities available to LLM.

        Returns:
            Dictionary describing LLM capabilities.
        """
        return {
            "available_commands": [cmd.value for cmd in LLMAuthCommand],
            "privacy_guarantees": {
                "llm_sees_passwords": False,
                "llm_sees_biometrics": False,
                "llm_sees_session_tokens": False,
                "llm_can_orchestrate_flows": True
            },
            "supported_platforms": [
                "banks", "government_portals", "payment_gateways",
                "healthcare", "education", "generic_web"
            ]
        }


def get_info() -> Dict[str, str]:
    """
    Get module information.

    Returns:
        Dictionary with module metadata.
    """
    return {
        "module": "integration_faza16",
        "faza": "18",
        "version": "1.0.0",
        "description": "Integration with FAZA 16 LLM Control Layer",
        "privacy_compliant": "true",
        "llm_access_level": "high_level_commands_only"
    }
