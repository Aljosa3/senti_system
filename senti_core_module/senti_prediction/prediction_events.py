"""
FAZA 13 - Prediction Events
Event definitions for prediction system

Provides event classes for prediction-related notifications via EventBus.
"""

from datetime import datetime
from typing import Dict, Any, Optional


class PredictionEvent:
    """
    Event emitted when a prediction is generated.
    """

    def __init__(self, event_type: str, payload: Dict[str, Any], timestamp: Optional[str] = None):
        """
        Initialize a prediction event.

        Args:
            event_type: Type of event (e.g., "PREDICTION_GENERATED")
            payload: Event payload containing prediction details
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = event_type
        self.payload = payload
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        return f"PredictionEvent(type={self.event_type}, timestamp={self.timestamp})"


class PredictionTriggerEvent:
    """
    Event emitted when a prediction trigger occurs.
    """

    def __init__(self, trigger_type: str, data: Dict[str, Any], timestamp: Optional[str] = None):
        """
        Initialize a prediction trigger event.

        Args:
            trigger_type: Type of trigger (time_tick, event_trigger, ai_request)
            data: Trigger data
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "PREDICTION_TRIGGER"
        self.trigger_type = trigger_type
        self.data = data
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_type": self.event_type,
            "trigger_type": self.trigger_type,
            "data": self.data,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        return f"PredictionTriggerEvent(trigger={self.trigger_type}, timestamp={self.timestamp})"


class HighRiskPredictionEvent:
    """
    Event emitted when a high-risk prediction is generated.
    Requires immediate attention from Security Manager (FAZA 8).
    """

    def __init__(
        self,
        prediction: str,
        risk_score: int,
        category: str,
        details: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        """
        Initialize a high-risk prediction event.

        Args:
            prediction: The prediction text
            risk_score: Risk score (typically > 70)
            category: Prediction category
            details: Additional details about the prediction
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "HIGH_RISK_PREDICTION"
        self.prediction = prediction
        self.risk_score = risk_score
        self.category = category
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
            "prediction": self.prediction,
            "risk_score": self.risk_score,
            "category": self.category,
            "details": self.details,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        """String representation of event."""
        return f"HighRiskPredictionEvent(risk={self.risk_score}, category={self.category})"


class PredictionValidationEvent:
    """
    Event emitted when prediction validation occurs.
    """

    def __init__(
        self,
        validation_result: bool,
        violations: list,
        context: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        """
        Initialize a prediction validation event.

        Args:
            validation_result: True if validation passed, False otherwise
            violations: List of validation violations (if any)
            context: Validation context
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "PREDICTION_VALIDATION"
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
        return f"PredictionValidationEvent(result={result}, violations={len(self.violations)})"


class PredictionStatsEvent:
    """
    Event emitted when prediction statistics are generated.
    """

    def __init__(self, stats: Dict[str, Any], timestamp: Optional[str] = None):
        """
        Initialize a prediction statistics event.

        Args:
            stats: Statistics dictionary
            timestamp: Optional timestamp (auto-generated if None)
        """
        self.event_type = "PREDICTION_STATS"
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
        total = self.stats.get("total_predictions", 0)
        return f"PredictionStatsEvent(total_predictions={total})"


# Event type constants for easy reference
PREDICTION_GENERATED = "PREDICTION_GENERATED"
PREDICTION_TRIGGER = "PREDICTION_TRIGGER"
HIGH_RISK_PREDICTION = "HIGH_RISK_PREDICTION"
PREDICTION_VALIDATION = "PREDICTION_VALIDATION"
PREDICTION_STATS = "PREDICTION_STATS"
