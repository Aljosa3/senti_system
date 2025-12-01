"""
FAZA 14 - Anomaly Detection Rules
Security validation and rule enforcement for anomaly detection

Integrates with FAZA 8 Security Manager to ensure safe anomaly detection.
"""

from typing import Dict, List, Any
from .anomaly_engine import AnomalyResult


class AnomalyRules:
    """
    Security validation and rule enforcement for anomaly detection.
    Ensures anomaly detection complies with FAZA 8 security policies.
    """

    # Whitelisted detection modes
    ALLOWED_MODES = [
        "statistical",
        "pattern",
        "rule"
    ]

    # Sensitive keywords that should trigger alerts
    SENSITIVE_KEYWORDS = [
        "password",
        "secret",
        "key",
        "token",
        "credential",
        "private_key",
        "api_key",
        "auth_token",
        "access_key"
    ]

    # Size limits
    MAX_EVENT_SIZE = 2000  # characters
    MAX_CONTEXT_ITEMS = 50  # items in context dict
    MAX_DATA_POINTS = 1000  # maximum data points for analysis

    # Frequency limits
    MIN_DETECTION_INTERVAL = 1  # seconds between detections
    MAX_DETECTIONS_PER_MINUTE = 60

    def __init__(self, security_manager=None):
        """
        Initialize anomaly rules.

        Args:
            security_manager: Optional FAZA 8 Security Manager
        """
        self.security_manager = security_manager
        self.violations = []
        self.detection_timestamps = []

    def validate_event(self, event: Dict[str, Any]) -> bool:
        """
        Validate an event for anomaly detection.

        Args:
            event: Event dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        self.violations.clear()

        # Check event size
        event_str = str(event)
        if len(event_str) > self.MAX_EVENT_SIZE:
            self.violations.append(
                f"Event size {len(event_str)} exceeds maximum {self.MAX_EVENT_SIZE}"
            )
            return False

        # Check for sensitive keywords
        if self._contains_sensitive_data(event_str):
            self.violations.append("Event contains sensitive keywords")
            return False

        # Check event structure
        if not isinstance(event, dict):
            self.violations.append("Event must be a dictionary")
            return False

        return True

    def validate_context(self, ctx: Dict[str, Any]) -> bool:
        """
        Validate context data.

        Args:
            ctx: Context dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        self.violations.clear()

        # Check context size
        if len(ctx) > self.MAX_CONTEXT_ITEMS:
            self.violations.append(
                f"Context has {len(ctx)} items, exceeds maximum {self.MAX_CONTEXT_ITEMS}"
            )
            return False

        # Check for sensitive data
        ctx_str = str(ctx)
        if self._contains_sensitive_data(ctx_str):
            self.violations.append("Context contains sensitive keywords")
            return False

        # Check context string size
        if len(ctx_str) > self.MAX_EVENT_SIZE:
            self.violations.append(
                f"Context string size {len(ctx_str)} exceeds maximum {self.MAX_EVENT_SIZE}"
            )
            return False

        return True

    def validate_detection_mode(self, mode: str) -> bool:
        """
        Validate that detection mode is allowed.

        Args:
            mode: Detection mode to validate

        Returns:
            True if mode is allowed, False otherwise
        """
        if mode not in self.ALLOWED_MODES:
            self.violations.append(
                f"Detection mode '{mode}' not in whitelist {self.ALLOWED_MODES}"
            )
            return False
        return True

    def validate_data_points(self, data: List[Any]) -> bool:
        """
        Validate data points for statistical analysis.

        Args:
            data: List of data points

        Returns:
            True if valid, False otherwise
        """
        if len(data) > self.MAX_DATA_POINTS:
            self.violations.append(
                f"Data points {len(data)} exceeds maximum {self.MAX_DATA_POINTS}"
            )
            return False

        # Check for reasonable numeric values
        try:
            for item in data[:10]:  # Sample first 10
                if isinstance(item, (int, float)):
                    if abs(item) > 1e10:  # Unreasonably large number
                        self.violations.append("Data contains unreasonably large values")
                        return False
        except Exception:
            pass

        return True

    def validate_anomaly_result(self, result: AnomalyResult) -> bool:
        """
        Validate an anomaly detection result.

        Args:
            result: AnomalyResult to validate

        Returns:
            True if valid, False otherwise
        """
        valid = True

        # Check score range
        if not (0 <= result.score <= 100):
            self.violations.append(
                f"Anomaly score {result.score} not in range [0, 100]"
            )
            valid = False

        # Check severity level
        valid_severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if result.severity not in valid_severities:
            self.violations.append(
                f"Invalid severity '{result.severity}', must be one of {valid_severities}"
            )
            valid = False

        # Check reason length
        if len(result.reason) > 500:
            self.violations.append(
                f"Reason length {len(result.reason)} exceeds maximum 500"
            )
            valid = False

        # Check for sensitive content in reason
        if self._contains_sensitive_data(result.reason):
            self.violations.append("Anomaly reason contains sensitive keywords")
            valid = False

        return valid

    def validate_frequency(self, timestamp: str) -> bool:
        """
        Validate detection frequency to prevent abuse.

        Args:
            timestamp: Current detection timestamp

        Returns:
            True if within frequency limits, False otherwise
        """
        from datetime import datetime, timedelta

        try:
            current_time = datetime.fromisoformat(timestamp)
        except Exception:
            current_time = datetime.now()

        # Clean old timestamps (older than 1 minute)
        cutoff = current_time - timedelta(minutes=1)
        self.detection_timestamps = [
            ts for ts in self.detection_timestamps
            if datetime.fromisoformat(ts) > cutoff
        ]

        # Check frequency limit
        if len(self.detection_timestamps) >= self.MAX_DETECTIONS_PER_MINUTE:
            self.violations.append(
                f"Detection frequency exceeds {self.MAX_DETECTIONS_PER_MINUTE} per minute"
            )
            return False

        # Add current timestamp
        self.detection_timestamps.append(timestamp)
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
                operation=f"anomaly.{operation}",
                context=context
            )

            if not allowed:
                self.violations.append(
                    f"Operation 'anomaly.{operation}' denied by security policy"
                )

            return allowed

        except Exception as e:
            # Security check failed, deny by default
            self.violations.append(f"Security check failed: {e}")
            return False

    def validate_full_operation(
        self,
        mode: str,
        event: Dict[str, Any],
        context: Dict[str, Any],
        result: AnomalyResult = None
    ) -> bool:
        """
        Perform comprehensive validation of an anomaly detection operation.

        Args:
            mode: Detection mode
            event: Event being analyzed
            context: Operation context
            result: Optional anomaly result to validate

        Returns:
            True if all validations pass, False otherwise
        """
        self.violations.clear()

        # Validate mode
        if not self.validate_detection_mode(mode):
            return False

        # Validate event
        if not self.validate_event(event):
            return False

        # Validate context
        if not self.validate_context(context):
            return False

        # Validate result if provided
        if result and not self.validate_anomaly_result(result):
            return False

        # Check security policy
        if not self.check_security_policy(mode, context):
            return False

        return True

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
            "max_event_size": self.MAX_EVENT_SIZE,
            "max_context_items": self.MAX_CONTEXT_ITEMS,
            "max_data_points": self.MAX_DATA_POINTS,
            "max_detections_per_minute": self.MAX_DETECTIONS_PER_MINUTE
        }

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

    def create_alert_for_violation(self, violation: str) -> Dict[str, Any]:
        """
        Create a security alert for a rule violation.

        Args:
            violation: Violation description

        Returns:
            Alert dictionary
        """
        from datetime import datetime

        return {
            "type": "SECURITY_VIOLATION",
            "category": "anomaly_detection",
            "violation": violation,
            "timestamp": datetime.now().isoformat(),
            "severity": "HIGH"
        }
