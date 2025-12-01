"""
FAZA 13 - Prediction Engine
Low-level prediction mechanism for Senti OS

Provides state forecasting, failure prediction, and action recommendations
based on Working, Episodic, and Semantic memory.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics


class PredictionResult:
    """
    Represents a prediction result with confidence and risk scoring.
    """

    def __init__(
        self,
        prediction: str,
        confidence: float,
        risk_score: int,
        source: str,
        timestamp: Optional[str] = None
    ):
        """
        Initialize a prediction result.

        Args:
            prediction: The prediction text
            confidence: Confidence level (0.0 to 1.0)
            risk_score: Risk score (0 to 100)
            source: Source of prediction (working|episodic|semantic|hybrid)
            timestamp: ISO format timestamp (auto-generated if None)
        """
        self.prediction = prediction
        self.confidence = confidence
        self.risk_score = risk_score
        self.source = source
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "prediction": self.prediction,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "source": self.source,
            "timestamp": self.timestamp
        }


class PredictionEngine:
    """
    Low-level prediction mechanism that analyzes memory data to forecast
    system behavior, failures, and recommended actions.
    """

    def __init__(self, memory_manager=None):
        """
        Initialize the prediction engine.

        Args:
            memory_manager: FAZA 12 Memory Manager instance
        """
        self.memory_manager = memory_manager
        self.prediction_history = []

    def predict_state(self, context: Dict[str, Any]) -> PredictionResult:
        """
        Predict future system state based on current context.

        Args:
            context: Current system context

        Returns:
            PredictionResult with state forecast
        """
        # Analyze working memory
        working_data = []
        if self.memory_manager:
            working_data = self.memory_manager.working_memory.get_all()

        # Calculate trend from working memory
        trend = self._calculate_trend(working_data)

        # Generate prediction
        prediction = f"System state trending {trend}"
        confidence = self._calculate_confidence(working_data)
        risk_score = self._calculate_risk(trend, working_data)

        result = PredictionResult(
            prediction=prediction,
            confidence=confidence,
            risk_score=risk_score,
            source="working"
        )

        self.prediction_history.append(result)
        return result

    def predict_failure(self) -> PredictionResult:
        """
        Predict potential system failures based on episodic memory.

        Returns:
            PredictionResult with failure prediction
        """
        # Analyze episodic memory for patterns
        failure_patterns = []
        if self.memory_manager:
            episodes = self.memory_manager.episodic_memory.recall_by_tags(["error", "failure"])
            failure_patterns = episodes

        # Calculate failure probability
        failure_count = len(failure_patterns)

        if failure_count == 0:
            prediction = "No failure patterns detected"
            confidence = 0.8
            risk_score = 10
        elif failure_count < 3:
            prediction = "Low risk of failure detected"
            confidence = 0.6
            risk_score = 30
        elif failure_count < 7:
            prediction = "Moderate risk of failure - monitoring recommended"
            confidence = 0.75
            risk_score = 60
        else:
            prediction = "High risk of failure - immediate attention required"
            confidence = 0.9
            risk_score = 90

        result = PredictionResult(
            prediction=prediction,
            confidence=confidence,
            risk_score=risk_score,
            source="episodic"
        )

        self.prediction_history.append(result)
        return result

    def predict_action(self, context: Dict[str, Any]) -> PredictionResult:
        """
        Predict recommended actions based on semantic knowledge.

        Args:
            context: Current context for action prediction

        Returns:
            PredictionResult with action recommendation
        """
        # Query semantic memory for related actions
        actions = []
        if self.memory_manager and context.get("task"):
            task = context["task"]
            related = self.memory_manager.semantic_memory.query(task)
            actions = related

        # Determine recommended action
        if not actions:
            prediction = "Continue normal operations"
            confidence = 0.5
            risk_score = 20
        else:
            # Use most relevant action
            prediction = f"Recommended action: {self._extract_action(actions)}"
            confidence = 0.8
            risk_score = self._calculate_action_risk(actions)

        result = PredictionResult(
            prediction=prediction,
            confidence=confidence,
            risk_score=risk_score,
            source="semantic"
        )

        self.prediction_history.append(result)
        return result

    def predict_user_behavior(self, recent_actions: List[str]) -> PredictionResult:
        """
        Predict likely user actions based on recent behavior.

        Args:
            recent_actions: List of recent user actions

        Returns:
            PredictionResult with user behavior prediction
        """
        if not recent_actions:
            prediction = "No user action patterns detected"
            confidence = 0.3
            risk_score = 15
        else:
            # Analyze action frequency
            action_freq = self._calculate_frequency(recent_actions)
            most_common = max(action_freq.items(), key=lambda x: x[1])[0] if action_freq else "unknown"

            prediction = f"User likely to perform: {most_common}"
            confidence = min(0.9, action_freq.get(most_common, 1) / len(recent_actions))
            risk_score = 25

        result = PredictionResult(
            prediction=prediction,
            confidence=confidence,
            risk_score=risk_score,
            source="hybrid"
        )

        self.prediction_history.append(result)
        return result

    def full_system_assessment(self) -> Dict[str, PredictionResult]:
        """
        Perform comprehensive system assessment with multiple predictions.

        Returns:
            Dictionary of prediction results by category
        """
        return {
            "state": self.predict_state({}),
            "failure": self.predict_failure(),
            "action": self.predict_action({"task": "system_check"}),
            "user": self.predict_user_behavior([])
        }

    def _calculate_trend(self, data: List[Any]) -> str:
        """Calculate trend from data points."""
        if len(data) < 2:
            return "stable"

        # Simple trend detection
        recent_count = len([d for d in data[-5:] if d])
        if recent_count > 3:
            return "increasing"
        elif recent_count < 2:
            return "decreasing"
        return "stable"

    def _calculate_confidence(self, data: List[Any]) -> float:
        """Calculate confidence based on data quality."""
        if not data:
            return 0.3

        # More data = higher confidence (up to 0.95)
        confidence = min(0.95, 0.5 + (len(data) * 0.05))
        return round(confidence, 2)

    def _calculate_risk(self, trend: str, data: List[Any]) -> int:
        """Calculate risk score based on trend and data."""
        base_risk = 20

        if trend == "increasing":
            base_risk += 30
        elif trend == "decreasing":
            base_risk += 10

        # Add risk based on data volume
        if len(data) > 10:
            base_risk += 20

        return min(100, base_risk)

    def _calculate_frequency(self, items: List[str]) -> Dict[str, int]:
        """Calculate frequency distribution of items."""
        freq = {}
        for item in items:
            freq[item] = freq.get(item, 0) + 1
        return freq

    def _extract_action(self, actions: List[Any]) -> str:
        """Extract recommended action from semantic results."""
        if not actions:
            return "monitor_system"

        # If actions contain metadata, extract first recommendation
        if isinstance(actions[0], dict) and "action" in actions[0]:
            return actions[0]["action"]

        return "review_system_logs"

    def _calculate_action_risk(self, actions: List[Any]) -> int:
        """Calculate risk score for recommended actions."""
        # More actions = potentially higher complexity/risk
        base_risk = 30
        if len(actions) > 3:
            base_risk += 20
        return min(100, base_risk)

    def get_prediction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about recent predictions.

        Returns:
            Statistics dictionary
        """
        if not self.prediction_history:
            return {
                "total_predictions": 0,
                "avg_confidence": 0.0,
                "avg_risk_score": 0
            }

        confidences = [p.confidence for p in self.prediction_history]
        risk_scores = [p.risk_score for p in self.prediction_history]

        return {
            "total_predictions": len(self.prediction_history),
            "avg_confidence": round(statistics.mean(confidences), 2),
            "avg_risk_score": round(statistics.mean(risk_scores)),
            "sources": self._count_sources()
        }

    def _count_sources(self) -> Dict[str, int]:
        """Count predictions by source."""
        sources = {}
        for pred in self.prediction_history:
            sources[pred.source] = sources.get(pred.source, 0) + 1
        return sources
