"""
FAZA 13 - Prediction Rules
Validation and security rules for prediction operations

Integrates with FAZA 8 Security Manager to ensure safe prediction operations.
"""

from typing import Dict, Any, List
from .prediction_engine import PredictionResult


class PredictionRules:
    """
    Validation and security rules for prediction operations.
    Ensures predictions comply with FAZA 8 security policies.
    """

    # Whitelisted prediction modes
    ALLOWED_MODES = [
        "state",
        "failure",
        "action",
        "user_behavior",
        "context",
        "full_system"
    ]

    # Sensitive keywords that should not be predicted
    SENSITIVE_KEYWORDS = [
        "password",
        "secret",
        "key",
        "token",
        "credential",
        "private_key",
        "api_key",
        "auth_token"
    ]

    # Maximum data size limits (in items/characters)
    MAX_CONTEXT_SIZE = 1000
    MAX_ACTION_LIST_SIZE = 50
    MAX_PREDICTION_LENGTH = 500

    def __init__(self, security_manager=None):
        """
        Initialize prediction rules.

        Args:
            security_manager: Optional FAZA 8 Security Manager
        """
        self.security_manager = security_manager
        self.violations = []

    def validate_prediction_mode(self, mode: str) -> bool:
        """
        Validate that prediction mode is allowed.

        Args:
            mode: Prediction mode to validate

        Returns:
            True if mode is allowed, False otherwise
        """
        if mode not in self.ALLOWED_MODES:
            self.violations.append(f"Prediction mode '{mode}' not in whitelist")
            return False
        return True

    def validate_context_data(self, context: Dict[str, Any]) -> bool:
        """
        Validate context data size and content.

        Args:
            context: Context dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        # Check size
        context_str = str(context)
        if len(context_str) > self.MAX_CONTEXT_SIZE:
            self.violations.append(
                f"Context size {len(context_str)} exceeds maximum {self.MAX_CONTEXT_SIZE}"
            )
            return False

        # Check for sensitive keywords
        if self._contains_sensitive_data(context_str):
            self.violations.append("Context contains sensitive keywords")
            return False

        return True

    def validate_action_list(self, actions: List[str]) -> bool:
        """
        Validate action list size.

        Args:
            actions: List of actions to validate

        Returns:
            True if valid, False otherwise
        """
        if len(actions) > self.MAX_ACTION_LIST_SIZE:
            self.violations.append(
                f"Action list size {len(actions)} exceeds maximum {self.MAX_ACTION_LIST_SIZE}"
            )
            return False
        return True

    def validate_prediction_result(self, result: PredictionResult) -> bool:
        """
        Validate a prediction result.

        Args:
            result: PredictionResult to validate

        Returns:
            True if valid, False otherwise
        """
        valid = True

        # Check confidence range
        if not (0.0 <= result.confidence <= 1.0):
            self.violations.append(
                f"Confidence {result.confidence} not in range [0.0, 1.0]"
            )
            valid = False

        # Check risk score range
        if not (0 <= result.risk_score <= 100):
            self.violations.append(
                f"Risk score {result.risk_score} not in range [0, 100]"
            )
            valid = False

        # Check prediction length
        if len(result.prediction) > self.MAX_PREDICTION_LENGTH:
            self.violations.append(
                f"Prediction length {len(result.prediction)} exceeds maximum {self.MAX_PREDICTION_LENGTH}"
            )
            valid = False

        # Check for sensitive content
        if self._contains_sensitive_data(result.prediction):
            self.violations.append("Prediction contains sensitive keywords")
            valid = False

        # Check valid source
        valid_sources = ["working", "episodic", "semantic", "hybrid", "system"]
        if result.source not in valid_sources:
            self.violations.append(
                f"Invalid source '{result.source}', must be one of {valid_sources}"
            )
            valid = False

        return valid

    def validate_trigger(self, trigger_type: str, data: Dict[str, Any]) -> bool:
        """
        Validate prediction trigger.

        Args:
            trigger_type: Type of trigger
            data: Trigger data

        Returns:
            True if valid, False otherwise
        """
        valid_triggers = ["time_tick", "event_trigger", "ai_request"]

        if trigger_type not in valid_triggers:
            self.violations.append(
                f"Invalid trigger type '{trigger_type}', must be one of {valid_triggers}"
            )
            return False

        # Validate trigger data
        if not self.validate_context_data(data):
            return False

        return True

    def check_security_policy(self, operation: str, context: Dict[str, Any]) -> bool:
        """
        Check operation against FAZA 8 security policies.

        Args:
            operation: Operation name
            context: Operation context

        Returns:
            True if allowed by security policy, False otherwise
        """
        if not self.security_manager:
            # No security manager, allow operation
            return True

        try:
            # Check with security manager
            allowed = self.security_manager.check_permission(
                operation=f"prediction.{operation}",
                context=context
            )

            if not allowed:
                self.violations.append(
                    f"Operation 'prediction.{operation}' denied by security policy"
                )

            return allowed

        except Exception as e:
            # Security check failed, deny by default
            self.violations.append(f"Security check failed: {e}")
            return False

    def get_violations(self) -> List[str]:
        """
        Get list of validation violations.

        Returns:
            List of violation messages
        """
        return self.violations.copy()

    def clear_violations(self):
        """Clear violation history."""
        self.violations.clear()

    def _contains_sensitive_data(self, text: str) -> bool:
        """
        Check if text contains sensitive keywords.

        Args:
            text: Text to check

        Returns:
            True if sensitive data found, False otherwise
        """
        text_lower = text.lower()
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

    def validate_full_operation(
        self,
        mode: str,
        context: Dict[str, Any],
        result: PredictionResult = None
    ) -> bool:
        """
        Perform comprehensive validation of a prediction operation.

        Args:
            mode: Prediction mode
            context: Operation context
            result: Optional prediction result to validate

        Returns:
            True if all validations pass, False otherwise
        """
        self.clear_violations()

        # Validate mode
        if not self.validate_prediction_mode(mode):
            return False

        # Validate context
        if not self.validate_context_data(context):
            return False

        # Validate result if provided
        if result and not self.validate_prediction_result(result):
            return False

        # Check security policy
        if not self.check_security_policy(mode, context):
            return False

        return True

    def get_validation_report(self) -> Dict[str, Any]:
        """
        Get detailed validation report.

        Returns:
            Report dictionary
        """
        return {
            "has_violations": len(self.violations) > 0,
            "violation_count": len(self.violations),
            "violations": self.violations.copy(),
            "allowed_modes": self.ALLOWED_MODES,
            "max_context_size": self.MAX_CONTEXT_SIZE,
            "max_action_list_size": self.MAX_ACTION_LIST_SIZE,
            "max_prediction_length": self.MAX_PREDICTION_LENGTH
        }
