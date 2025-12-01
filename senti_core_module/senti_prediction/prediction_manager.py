"""
FAZA 13 - Prediction Manager
High-level orchestrator for prediction operations

Manages prediction engine, stores results in memory, and publishes events.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from .prediction_engine import PredictionEngine, PredictionResult
from .prediction_events import PredictionEvent


class PredictionManager:
    """
    High-level orchestrator for prediction operations.
    Manages the prediction engine, stores results, and publishes events.
    """

    def __init__(self, memory_manager=None, event_bus=None):
        """
        Initialize the prediction manager.

        Args:
            memory_manager: FAZA 12 Memory Manager instance
            event_bus: EventBus instance for publishing events
        """
        self.memory_manager = memory_manager
        self.event_bus = event_bus
        self.engine = PredictionEngine(memory_manager)

        self.last_predictions = {}
        self.prediction_count = 0
        self.enabled = True

    def predict_context(self, context: Optional[Dict[str, Any]] = None) -> PredictionResult:
        """
        Predict based on current context.

        Args:
            context: Optional context dictionary

        Returns:
            PredictionResult
        """
        if not self.enabled:
            return self._create_disabled_result()

        context = context or {}
        result = self.engine.predict_state(context)

        self._store_prediction(result, "context")
        self._publish_event(result, "context")

        self.last_predictions["context"] = result
        self.prediction_count += 1

        return result

    def predict_failures(self) -> PredictionResult:
        """
        Predict potential system failures.

        Returns:
            PredictionResult with failure prediction
        """
        if not self.enabled:
            return self._create_disabled_result()

        result = self.engine.predict_failure()

        self._store_prediction(result, "failure")
        self._publish_event(result, "failure")

        self.last_predictions["failure"] = result
        self.prediction_count += 1

        return result

    def predict_actions(self, context: Optional[Dict[str, Any]] = None) -> PredictionResult:
        """
        Predict recommended actions.

        Args:
            context: Optional context for action prediction

        Returns:
            PredictionResult with action recommendations
        """
        if not self.enabled:
            return self._create_disabled_result()

        context = context or {"task": "general_prediction"}
        result = self.engine.predict_action(context)

        self._store_prediction(result, "action")
        self._publish_event(result, "action")

        self.last_predictions["action"] = result
        self.prediction_count += 1

        return result

    def predict_user_behavior(self, recent_actions: Optional[List[str]] = None) -> PredictionResult:
        """
        Predict user behavior based on recent actions.

        Args:
            recent_actions: List of recent user actions

        Returns:
            PredictionResult with user behavior prediction
        """
        if not self.enabled:
            return self._create_disabled_result()

        recent_actions = recent_actions or []
        result = self.engine.predict_user_behavior(recent_actions)

        self._store_prediction(result, "user_behavior")
        self._publish_event(result, "user_behavior")

        self.last_predictions["user_behavior"] = result
        self.prediction_count += 1

        return result

    def full_system_prediction(self) -> Dict[str, PredictionResult]:
        """
        Perform comprehensive system prediction across all categories.

        Returns:
            Dictionary of prediction results
        """
        if not self.enabled:
            return {
                "state": self._create_disabled_result(),
                "failure": self._create_disabled_result(),
                "action": self._create_disabled_result(),
                "user": self._create_disabled_result()
            }

        results = self.engine.full_system_assessment()

        # Store and publish each result
        for category, result in results.items():
            self._store_prediction(result, category)
            self._publish_event(result, category)

        self.last_predictions.update(results)
        self.prediction_count += len(results)

        return results

    def handle_trigger(self, trigger_type: str, data: Optional[Dict[str, Any]] = None):
        """
        Handle prediction trigger.

        Args:
            trigger_type: Type of trigger (time_tick, event_trigger, ai_request)
            data: Optional trigger data
        """
        if not self.enabled:
            return

        data = data or {}

        if trigger_type == "time_tick":
            # Periodic prediction
            self.full_system_prediction()

        elif trigger_type == "event_trigger":
            # Event-based prediction
            event_type = data.get("event_type", "unknown")
            if "error" in event_type.lower() or "failure" in event_type.lower():
                self.predict_failures()
            else:
                self.predict_context(data)

        elif trigger_type == "ai_request":
            # AI-requested prediction
            request_type = data.get("request_type", "full")
            if request_type == "full":
                self.full_system_prediction()
            elif request_type == "failure":
                self.predict_failures()
            elif request_type == "action":
                self.predict_actions(data)
            else:
                self.predict_context(data)

    def get_last_prediction(self, category: Optional[str] = None) -> Optional[PredictionResult]:
        """
        Get last prediction for a category.

        Args:
            category: Prediction category (context, failure, action, user_behavior)

        Returns:
            Last PredictionResult or None
        """
        if category:
            return self.last_predictions.get(category)
        else:
            # Return most recent prediction
            if self.last_predictions:
                return list(self.last_predictions.values())[-1]
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get prediction statistics.

        Returns:
            Statistics dictionary
        """
        engine_stats = self.engine.get_prediction_stats()

        return {
            "total_predictions": self.prediction_count,
            "enabled": self.enabled,
            "categories": list(self.last_predictions.keys()),
            "engine_stats": engine_stats,
            "timestamp": datetime.now().isoformat()
        }

    def enable(self):
        """Enable prediction system."""
        self.enabled = True

    def disable(self):
        """Disable prediction system."""
        self.enabled = False

    def clear_history(self):
        """Clear prediction history."""
        self.last_predictions.clear()
        self.engine.prediction_history.clear()
        self.prediction_count = 0

    def _store_prediction(self, result: PredictionResult, category: str):
        """
        Store prediction in episodic memory (FAZA 12).

        Args:
            result: PredictionResult to store
            category: Prediction category
        """
        if not self.memory_manager:
            return

        try:
            memory_data = {
                "type": "prediction",
                "category": category,
                "prediction": result.prediction,
                "confidence": result.confidence,
                "risk_score": result.risk_score,
                "source": result.source,
                "timestamp": result.timestamp
            }

            # Store in episodic memory with appropriate tags
            tags = ["prediction", category]
            if result.risk_score > 70:
                tags.append("high_risk")

            self.memory_manager.episodic_memory.store(
                event_type="PREDICTION",
                data=memory_data,
                tags=tags
            )

        except Exception as e:
            print(f"[PredictionManager] Failed to store prediction: {e}")

    def _publish_event(self, result: PredictionResult, category: str):
        """
        Publish prediction event to EventBus.

        Args:
            result: PredictionResult to publish
            category: Prediction category
        """
        if not self.event_bus:
            return

        try:
            event = PredictionEvent(
                event_type="PREDICTION_GENERATED",
                payload={
                    "category": category,
                    "prediction": result.prediction,
                    "confidence": result.confidence,
                    "risk_score": result.risk_score,
                    "source": result.source,
                    "timestamp": result.timestamp
                }
            )

            self.event_bus.emit(event.event_type, event.payload)

        except Exception as e:
            print(f"[PredictionManager] Failed to publish event: {e}")

    def _create_disabled_result(self) -> PredictionResult:
        """Create a result for when prediction is disabled."""
        return PredictionResult(
            prediction="Prediction system disabled",
            confidence=0.0,
            risk_score=0,
            source="system"
        )
