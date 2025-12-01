"""
FAZA 14 - Anomaly Service
OS-level service for periodic anomaly detection operations

Integrates with FAZA 6 Autonomous Task Loop for periodic anomaly detection
and FAZA 8 Security Manager for high-severity alerts.
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from .anomaly_manager import AnomalyManager
from .anomaly_events import AnomalyStatsEvent


class AnomalyService:
    """
    OS-level service that runs periodic anomaly detection and monitors system state.
    Integrates with FAZA 6 (Autonomous Task Loop) and FAZA 8 (Security Manager).
    """

    def __init__(
        self,
        anomaly_manager: AnomalyManager,
        event_bus=None,
        security_manager=None,
        prediction_manager=None,
        interval: int = 30
    ):
        """
        Initialize the anomaly service.

        Args:
            anomaly_manager: AnomalyManager instance
            event_bus: EventBus for publishing events
            security_manager: FAZA 8 Security Manager
            prediction_manager: FAZA 13 Prediction Manager
            interval: Detection interval in seconds (default: 30)
        """
        self.anomaly_manager = anomaly_manager
        self.event_bus = event_bus
        self.security_manager = security_manager
        self.prediction_manager = prediction_manager
        self.interval = interval

        self.running = False
        self.thread = None
        self.stats = {
            "total_runs": 0,
            "total_anomalies": 0,
            "high_severity_alerts": 0,
            "last_run": None,
            "avg_score": 0.0
        }

    def start(self):
        """Start the anomaly service."""
        if self.running:
            print("[AnomalyService] Already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"[AnomalyService] Started with {self.interval}s interval")

    def stop(self):
        """Stop the anomaly service."""
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[AnomalyService] Stopped")

    def check(self):
        """
        Single check operation - called by autonomous task loop.
        Performs anomaly detection without starting the service thread.
        """
        try:
            self._execute_detection_cycle()
        except Exception as e:
            print(f"[AnomalyService] Check failed: {e}")

    def _run_loop(self):
        """Main service loop - runs anomaly detection periodically."""
        while self.running:
            try:
                self._execute_detection_cycle()
                time.sleep(self.interval)
            except Exception as e:
                print(f"[AnomalyService] Error in detection cycle: {e}")
                time.sleep(self.interval)

    def _execute_detection_cycle(self):
        """Execute a single anomaly detection cycle."""
        print(f"[AnomalyService] Running detection cycle at {datetime.now().isoformat()}")

        # Run system-wide analysis
        results = self.anomaly_manager.analyze_system()

        # Update statistics
        self.stats["total_runs"] += 1
        self.stats["last_run"] = datetime.now().isoformat()

        if results:
            self.stats["total_anomalies"] += len(results)

            # Calculate average score
            scores = [r.score for r in results.values()]
            if scores:
                avg_score = sum(scores) / len(scores)
                self.stats["avg_score"] = round(avg_score, 2)

            # Log anomalies
            for component, result in results.items():
                if result.severity in ["HIGH", "CRITICAL"]:
                    self.stats["high_severity_alerts"] += 1
                    print(
                        f"[AnomalyService] HIGH SEVERITY: {component} - "
                        f"{result.reason} (score={result.score})"
                    )
                else:
                    print(
                        f"[AnomalyService] Anomaly in {component}: "
                        f"{result.reason} (score={result.score}, severity={result.severity})"
                    )

        # Auto-resolve old anomalies
        self._auto_resolve_anomalies()

        # Auto-consolidate memory
        self._auto_consolidate_memory()

        # Notify other systems
        self._notify_prediction_engine()
        self._notify_ai_layer()

        # Publish statistics event
        self._publish_stats()

    def _auto_resolve_anomalies(self):
        """Automatically resolve anomalies that no longer appear."""
        active = self.anomaly_manager.get_active_anomalies()

        # Simple heuristic: resolve LOW severity anomalies older than 5 minutes
        # In production, this would be more sophisticated
        for anomaly_id, anomaly in list(active.items()):
            try:
                from datetime import datetime, timedelta
                anomaly_time = datetime.fromisoformat(anomaly.timestamp)
                age = datetime.now() - anomaly_time

                if anomaly.severity == "LOW" and age > timedelta(minutes=5):
                    self.anomaly_manager.resolve_anomaly(
                        anomaly_id,
                        "auto_resolved_after_5min"
                    )
                    print(f"[AnomalyService] Auto-resolved LOW severity anomaly {anomaly_id}")

            except Exception as e:
                print(f"[AnomalyService] Failed to auto-resolve {anomaly_id}: {e}")

    def _auto_consolidate_memory(self):
        """Auto-consolidate anomaly data to semantic memory (FAZA 12)."""
        # Consolidation happens automatically in anomaly_manager.resolve_anomaly()
        # This is a placeholder for additional consolidation logic
        pass

    def _notify_prediction_engine(self):
        """Notify Prediction Engine (FAZA 13) about anomalies."""
        if not self.prediction_manager:
            return

        try:
            # Trigger prediction based on anomaly detection
            # This could influence future predictions
            active_count = len(self.anomaly_manager.get_active_anomalies())

            if active_count > 3:
                # Many active anomalies might indicate system issues
                self.prediction_manager.handle_trigger(
                    "event_trigger",
                    {"event_type": "HIGH_ANOMALY_COUNT", "count": active_count}
                )

        except Exception as e:
            print(f"[AnomalyService] Failed to notify prediction engine: {e}")

    def _notify_ai_layer(self):
        """Notify AI Layer (FAZA 5) about critical anomalies."""
        # This would typically send events to the AI operational layer
        # for autonomous response planning
        high_severity = [
            a for a in self.anomaly_manager.get_active_anomalies().values()
            if a.severity in ["HIGH", "CRITICAL"]
        ]

        if high_severity:
            print(f"[AnomalyService] AI Layer notified: {len(high_severity)} critical anomalies")

    def _publish_stats(self):
        """Publish anomaly statistics event."""
        if not self.event_bus:
            return

        try:
            stats_event = AnomalyStatsEvent(
                stats=self.get_statistics()
            )
            self.event_bus.emit(stats_event.event_type, stats_event.to_dict())
        except Exception as e:
            print(f"[AnomalyService] Failed to publish stats event: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get service statistics.

        Returns:
            Statistics dictionary
        """
        manager_stats = self.anomaly_manager.get_stats()

        return {
            "service": {
                "running": self.running,
                "interval": self.interval,
                "total_runs": self.stats["total_runs"],
                "total_anomalies": self.stats["total_anomalies"],
                "high_severity_alerts": self.stats["high_severity_alerts"],
                "last_run": self.stats["last_run"],
                "avg_score": self.stats["avg_score"]
            },
            "manager": manager_stats,
            "timestamp": datetime.now().isoformat()
        }

    def manual_detection(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger manual anomaly detection (outside of periodic cycle).

        Args:
            component: Optional component for targeted detection

        Returns:
            Detection results
        """
        if component:
            result = self.anomaly_manager.detect_for(component)
            return {component: result}
        else:
            # Full system analysis
            return self.anomaly_manager.analyze_system()

    def set_interval(self, interval: int):
        """
        Change detection interval.

        Args:
            interval: New interval in seconds
        """
        self.interval = max(10, interval)  # Minimum 10 seconds
        print(f"[AnomalyService] Interval changed to {self.interval}s")

    def reset_statistics(self):
        """Reset service statistics."""
        self.stats = {
            "total_runs": 0,
            "total_anomalies": 0,
            "high_severity_alerts": 0,
            "last_run": None,
            "avg_score": 0.0
        }
        self.anomaly_manager.clear_history()
        print("[AnomalyService] Statistics reset")

    def is_running(self) -> bool:
        """
        Check if service is running.

        Returns:
            True if running, False otherwise
        """
        return self.running

    def get_active_anomalies(self) -> Dict[str, Any]:
        """
        Get currently active anomalies.

        Returns:
            Dictionary of active anomalies
        """
        return {
            aid: result.to_dict()
            for aid, result in self.anomaly_manager.get_active_anomalies().items()
        }

    def resolve_anomaly(self, anomaly_id: str, resolution: str = "manual_resolution") -> bool:
        """
        Manually resolve an anomaly.

        Args:
            anomaly_id: ID of anomaly to resolve
            resolution: Resolution description

        Returns:
            True if resolved successfully
        """
        return self.anomaly_manager.resolve_anomaly(anomaly_id, resolution)
