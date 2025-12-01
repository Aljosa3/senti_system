"""
FAZA 14 - Anomaly Detection Events
Event definitions for anomaly detection system

Provides event classes for anomaly-related notifications via EventBus.
"""

from datetime import datetime
from typing import Dict, Any, Optional


class AnomalyEvent:
    """
    Event emitted when an anomaly is detected.
    """

    def __init__(
        self,
        score: int,
        severity: str,
        reason: str,
        context: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        """
        Initialize an anomaly event.

        Args:
            score: Anomaly score (0-100)
            severity: Severity level (LOW|MEDIUM|HIGH|CRITICAL)
            reason: Description of the anomaly
            context: Additional context data
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "ANOMALY_DETECTED"
        self.score = score
        self.severity = severity
        self.reason = reason
        self.context = context
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_type": self.event_type,
            "score": self.score,
            "severity": self.severity,
            "reason": self.reason,
            "context": self.context,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        return f"AnomalyEvent(severity={self.severity}, score={self.score})"


class HighSeverityEvent:
    """
    Event emitted when a high or critical severity anomaly is detected.
    Requires immediate attention from Security Manager (FAZA 8).
    """

    def __init__(
        self,
        score: int,
        severity: str,
        reason: str,
        component: str,
        details: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        """
        Initialize a high severity anomaly event.

        Args:
            score: Anomaly score (typically >= 60)
            severity: Severity level (HIGH|CRITICAL)
            reason: Description of the anomaly
            component: Component where anomaly was detected
            details: Additional details about the anomaly
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "HIGH_SEVERITY_ANOMALY"
        self.score = score
        self.severity = severity
        self.reason = reason
        self.component = component
        self.details = details
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_type": self.event_type,
            "score": self.score,
            "severity": self.severity,
            "reason": self.reason,
            "component": self.component,
            "details": self.details,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        return f"HighSeverityEvent(severity={self.severity}, component={self.component})"


class AnomalyStatsEvent:
    """
    Event emitted when anomaly statistics are generated.
    """

    def __init__(self, stats: Dict[str, Any], timestamp: Optional[str] = None):
        """
        Initialize an anomaly statistics event.

        Args:
            stats: Statistics dictionary
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "ANOMALY_STATS_UPDATE"
        self.stats = stats
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_type": self.event_type,
            "stats": self.stats,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        total = self.stats.get("total_anomalies", 0)
        return f"AnomalyStatsEvent(total_anomalies={total})"


class AnomalyResolvedEvent:
    """
    Event emitted when an anomaly is resolved.
    """

    def __init__(
        self,
        anomaly_id: str,
        resolution: str,
        details: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        """
        Initialize an anomaly resolved event.

        Args:
            anomaly_id: ID of the resolved anomaly
            resolution: How the anomaly was resolved
            details: Additional resolution details
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "ANOMALY_RESOLVED"
        self.anomaly_id = anomaly_id
        self.resolution = resolution
        self.details = details
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_type": self.event_type,
            "anomaly_id": self.anomaly_id,
            "resolution": self.resolution,
            "details": self.details,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        return f"AnomalyResolvedEvent(id={self.anomaly_id})"


class AnomalyPatternEvent:
    """
    Event emitted when a pattern of anomalies is detected.
    """

    def __init__(
        self,
        pattern_type: str,
        anomaly_count: int,
        timespan: str,
        details: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        """
        Initialize an anomaly pattern event.

        Args:
            pattern_type: Type of pattern detected
            anomaly_count: Number of anomalies in the pattern
            timespan: Timespan over which pattern was detected
            details: Additional pattern details
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "ANOMALY_PATTERN_DETECTED"
        self.pattern_type = pattern_type
        self.anomaly_count = anomaly_count
        self.timespan = timespan
        self.details = details
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_type": self.event_type,
            "pattern_type": self.pattern_type,
            "anomaly_count": self.anomaly_count,
            "timespan": self.timespan,
            "details": self.details,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        return f"AnomalyPatternEvent(type={self.pattern_type}, count={self.anomaly_count})"


class AnomalyValidationEvent:
    """
    Event emitted when anomaly validation occurs.
    """

    def __init__(
        self,
        validation_result: bool,
        violations: list,
        context: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        """
        Initialize an anomaly validation event.

        Args:
            validation_result: True if validation passed, False otherwise
            violations: List of validation violations (if any)
            context: Validation context
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "ANOMALY_VALIDATION"
        self.validation_result = validation_result
        self.violations = violations
        self.context = context
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_type": self.event_type,
            "validation_result": self.validation_result,
            "violations": self.violations,
            "context": self.context,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        result = "passed" if self.validation_result else "failed"
        return f"AnomalyValidationEvent(result={result}, violations={len(self.violations)})"


# Event type constants for easy reference
ANOMALY_DETECTED = "ANOMALY_DETECTED"
HIGH_SEVERITY_ANOMALY = "HIGH_SEVERITY_ANOMALY"
ANOMALY_STATS_UPDATE = "ANOMALY_STATS_UPDATE"
ANOMALY_RESOLVED = "ANOMALY_RESOLVED"
ANOMALY_PATTERN_DETECTED = "ANOMALY_PATTERN_DETECTED"
ANOMALY_VALIDATION = "ANOMALY_VALIDATION"
