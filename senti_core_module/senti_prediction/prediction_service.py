"""
FAZA 13 - Prediction Service
OS-level service for periodic prediction operations

Integrates with FAZA 6 Autonomous Task Loop for periodic predictions
and FAZA 8 Security Manager for high-risk alerts.
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from .prediction_manager import PredictionManager
from .prediction_events import HighRiskPredictionEvent, PredictionStatsEvent


class PredictionService:
    """
    OS-level service that runs periodic predictions and monitors system state.
    Integrates with FAZA 6 (Autonomous Task Loop) and FAZA 8 (Security Manager).
    """

    def __init__(
        self,
        prediction_manager: PredictionManager,
        event_bus=None,
        security_manager=None,
        interval: int = 60
    ):
        """
        Initialize the prediction service.

        Args:
            prediction_manager: PredictionManager instance
            event_bus: EventBus for publishing events
            security_manager: FAZA 8 Security Manager
            interval: Prediction interval in seconds (default: 60)
        """
        self.prediction_manager = prediction_manager
        self.event_bus = event_bus
        self.security_manager = security_manager
        self.interval = interval

        self.running = False
        self.thread = None
        self.stats = {
            "total_runs": 0,
            "high_risk_alerts": 0,
            "last_run": None,
            "avg_risk_score": 0.0
        }

    def start(self):
        """Start the prediction service."""
        if self.running:
            print("[PredictionService] Already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"[PredictionService] Started with {self.interval}s interval")

    def stop(self):
        """Stop the prediction service."""
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[PredictionService] Stopped")

    def _run_loop(self):
        """Main service loop - runs predictions periodically."""
        while self.running:
            try:
                self._execute_prediction_cycle()
                time.sleep(self.interval)
            except Exception as e:
                print(f"[PredictionService] Error in prediction cycle: {e}")
                time.sleep(self.interval)

    def _execute_prediction_cycle(self):
        """Execute a single prediction cycle."""
        print(f"[PredictionService] Running prediction cycle at {datetime.now().isoformat()}")

        # Run full system prediction
        results = self.prediction_manager.full_system_prediction()

        # Update statistics
        self.stats["total_runs"] += 1
        self.stats["last_run"] = datetime.now().isoformat()

        # Calculate average risk score
        risk_scores = [r.risk_score for r in results.values()]
        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            self.stats["avg_risk_score"] = round(avg_risk, 2)

        # Check for high-risk predictions
        for category, result in results.items():
            if result.risk_score > 70:
                self._handle_high_risk(category, result)

        # Publish statistics event
        self._publish_stats()

    def _handle_high_risk(self, category: str, result):
        """
        Handle high-risk prediction.

        Args:
            category: Prediction category
            result: PredictionResult with high risk score
        """
        print(f"[PredictionService] HIGH RISK ALERT: {category} - {result.prediction}")

        self.stats["high_risk_alerts"] += 1

        # Create high-risk event
        event = HighRiskPredictionEvent(
            prediction=result.prediction,
            risk_score=result.risk_score,
            category=category,
            details={
                "confidence": result.confidence,
                "source": result.source,
                "timestamp": result.timestamp
            }
        )

        # Publish to EventBus
        if self.event_bus:
            try:
                self.event_bus.emit(event.event_type, event.to_dict())
            except Exception as e:
                print(f"[PredictionService] Failed to publish high-risk event: {e}")

        # Alert Security Manager (FAZA 8)
        if self.security_manager:
            self._alert_security_manager(event)

    def _alert_security_manager(self, event: HighRiskPredictionEvent):
        """
        Alert Security Manager about high-risk prediction.

        Args:
            event: HighRiskPredictionEvent
        """
        try:
            # Check if security manager has alert method
            if hasattr(self.security_manager, "handle_alert"):
                self.security_manager.handle_alert({
                    "type": "high_risk_prediction",
                    "risk_score": event.risk_score,
                    "category": event.category,
                    "prediction": event.prediction,
                    "details": event.details
                })
            else:
                print(f"[PredictionService] Security Manager notified: Risk={event.risk_score}")

        except Exception as e:
            print(f"[PredictionService] Failed to alert Security Manager: {e}")

    def _publish_stats(self):
        """Publish prediction statistics event."""
        if not self.event_bus:
            return

        try:
            stats_event = PredictionStatsEvent(
                stats=self.get_statistics()
            )
            self.event_bus.emit(stats_event.event_type, stats_event.to_dict())
        except Exception as e:
            print(f"[PredictionService] Failed to publish stats event: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get service statistics.

        Returns:
            Statistics dictionary
        """
        manager_stats = self.prediction_manager.get_statistics()

        return {
            "service": {
                "running": self.running,
                "interval": self.interval,
                "total_runs": self.stats["total_runs"],
                "high_risk_alerts": self.stats["high_risk_alerts"],
                "last_run": self.stats["last_run"],
                "avg_risk_score": self.stats["avg_risk_score"]
            },
            "manager": manager_stats,
            "timestamp": datetime.now().isoformat()
        }

    def manual_prediction(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger manual prediction (outside of periodic cycle).

        Args:
            category: Optional category for targeted prediction

        Returns:
            Prediction results
        """
        if category == "failure":
            result = self.prediction_manager.predict_failures()
            return {"failure": result}
        elif category == "action":
            result = self.prediction_manager.predict_actions()
            return {"action": result}
        elif category == "context":
            result = self.prediction_manager.predict_context()
            return {"context": result}
        elif category == "user":
            result = self.prediction_manager.predict_user_behavior()
            return {"user": result}
        else:
            # Full system prediction
            return self.prediction_manager.full_system_prediction()

    def set_interval(self, interval: int):
        """
        Change prediction interval.

        Args:
            interval: New interval in seconds
        """
        self.interval = max(10, interval)  # Minimum 10 seconds
        print(f"[PredictionService] Interval changed to {self.interval}s")

    def reset_statistics(self):
        """Reset service statistics."""
        self.stats = {
            "total_runs": 0,
            "high_risk_alerts": 0,
            "last_run": None,
            "avg_risk_score": 0.0
        }
        self.prediction_manager.clear_history()
        print("[PredictionService] Statistics reset")

    def is_running(self) -> bool:
        """
        Check if service is running.

        Returns:
            True if running, False otherwise
        """
        return self.running

    def get_last_predictions(self) -> Dict[str, Any]:
        """
        Get last predictions from manager.

        Returns:
            Dictionary of last predictions by category
        """
        return {
            category: result.to_dict()
            for category, result in self.prediction_manager.last_predictions.items()
        }
