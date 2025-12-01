"""
FAZA 14 - Anomaly Manager
High-level orchestration for anomaly detection operations

Manages anomaly engine, stores results in memory, and publishes events.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
from .anomaly_engine import AnomalyEngine, AnomalyResult
from .anomaly_events import (
    AnomalyEvent,
    HighSeverityEvent,
    AnomalyStatsEvent,
    AnomalyResolvedEvent,
    AnomalyPatternEvent
)


class AnomalyManager:
    """
    High-level orchestrator for anomaly detection operations.
    Manages the anomaly engine, stores results, and publishes events.
    """

    def __init__(
        self,
        memory_manager=None,
        prediction_manager=None,
        event_bus=None,
        security_manager=None
    ):
        """
        Initialize the anomaly manager.

        Args:
            memory_manager: FAZA 12 Memory Manager instance
            prediction_manager: FAZA 13 Prediction Manager instance
            event_bus: EventBus instance for publishing events
            security_manager: FAZA 8 Security Manager instance
        """
        self.memory_manager = memory_manager
        self.prediction_manager = prediction_manager
        self.event_bus = event_bus
        self.security_manager = security_manager

        self.engine = AnomalyEngine(memory_manager, prediction_manager)

        self.active_anomalies = {}  # anomaly_id -> anomaly_result
        self.resolved_anomalies = []
        self.anomaly_count = 0
        self.high_severity_count = 0
        self.enabled = True

    def analyze_system(self) -> Dict[str, AnomalyResult]:
        """
        Perform comprehensive system anomaly analysis.

        Returns:
            Dictionary of anomaly results by component
        """
        if not self.enabled:
            return {}

        results = {}

        # Analyze key components
        components = [
            "kernel",
            "memory",
            "services",
            "ai_layer",
            "prediction",
            "security"
        ]

        for component in components:
            try:
                result = self.engine.detect_for(
                    component_name=component,
                    context={"analysis_type": "system_wide"}
                )

                if result.score > 0:
                    results[component] = result
                    self._process_anomaly_result(component, result)

            except Exception as e:
                print(f"[AnomalyManager] Failed to analyze {component}: {e}")

        return results

    def detect_for(self, component: str, context: Optional[Dict[str, Any]] = None) -> AnomalyResult:
        """
        Detect anomalies for a specific component.

        Args:
            component: Component name
            context: Optional context data

        Returns:
            AnomalyResult for the component
        """
        if not self.enabled:
            return self._create_disabled_result()

        context = context or {}
        result = self.engine.detect_for(component, context)

        if result.score > 0:
            self._process_anomaly_result(component, result)

        return result

    def detect_statistical(self, data: List[float], component: str = "unknown") -> AnomalyResult:
        """
        Perform statistical anomaly detection.

        Args:
            data: Data points for analysis
            component: Component name

        Returns:
            AnomalyResult with statistical analysis
        """
        if not self.enabled:
            return self._create_disabled_result()

        result = self.engine.detect_statistical_anomaly(data)
        result.context["component"] = component

        if result.score > 0:
            self._process_anomaly_result(component, result)

        return result

    def detect_pattern(self, events: List[Dict[str, Any]], component: str = "unknown") -> AnomalyResult:
        """
        Perform pattern anomaly detection.

        Args:
            events: Events for pattern analysis
            component: Component name

        Returns:
            AnomalyResult with pattern analysis
        """
        if not self.enabled:
            return self._create_disabled_result()

        result = self.engine.detect_pattern_anomaly(events)
        result.context["component"] = component

        if result.score > 0:
            self._process_anomaly_result(component, result)

        return result

    def detect_rule(self, event: Dict[str, Any], component: str = "unknown") -> AnomalyResult:
        """
        Perform rule-based anomaly detection.

        Args:
            event: Event to check
            component: Component name

        Returns:
            AnomalyResult with rule check
        """
        if not self.enabled:
            return self._create_disabled_result()

        result = self.engine.detect_rule_anomaly(event)
        result.context["component"] = component

        if result.score > 0:
            self._process_anomaly_result(component, result)

        return result

    def resolve_anomaly(self, anomaly_id: str, resolution: str = "auto_resolved") -> bool:
        """
        Mark an anomaly as resolved.

        Args:
            anomaly_id: ID of the anomaly to resolve
            resolution: Resolution description

        Returns:
            True if resolved successfully, False otherwise
        """
        if anomaly_id not in self.active_anomalies:
            return False

        anomaly = self.active_anomalies.pop(anomaly_id)

        # Store in resolved list
        self.resolved_anomalies.append({
            "id": anomaly_id,
            "anomaly": anomaly,
            "resolution": resolution,
            "resolved_at": datetime.now().isoformat()
        })

        # Publish resolution event
        self._publish_resolution_event(anomaly_id, resolution, anomaly)

        # Store in semantic memory for long-term learning
        self._consolidate_to_semantic(anomaly, resolution)

        return True

    def escalate_if_needed(self, anomaly: AnomalyResult, component: str):
        """
        Escalate anomaly to Security Manager if severity is HIGH or CRITICAL.

        Args:
            anomaly: AnomalyResult to check
            component: Component where anomaly was detected
        """
        if anomaly.severity in ["HIGH", "CRITICAL"]:
            self.high_severity_count += 1

            # Alert Security Manager
            if self.security_manager:
                self._alert_security_manager(anomaly, component)

            # Publish high severity event
            self._publish_high_severity_event(anomaly, component)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get anomaly detection statistics.

        Returns:
            Statistics dictionary
        """
        engine_stats = self.engine.get_detection_stats()

        return {
            "total_anomalies": self.anomaly_count,
            "active_anomalies": len(self.active_anomalies),
            "resolved_anomalies": len(self.resolved_anomalies),
            "high_severity_count": self.high_severity_count,
            "enabled": self.enabled,
            "engine_stats": engine_stats,
            "timestamp": datetime.now().isoformat()
        }

    def get_active_anomalies(self) -> Dict[str, AnomalyResult]:
        """
        Get currently active anomalies.

        Returns:
            Dictionary of active anomalies
        """
        return self.active_anomalies.copy()

    def enable(self):
        """Enable anomaly detection."""
        self.enabled = True

    def disable(self):
        """Disable anomaly detection."""
        self.enabled = False

    def clear_history(self):
        """Clear anomaly history."""
        self.active_anomalies.clear()
        self.resolved_anomalies.clear()
        self.engine.clear_history()
        self.anomaly_count = 0
        self.high_severity_count = 0

    def _process_anomaly_result(self, component: str, result: AnomalyResult):
        """
        Process an anomaly result: store, publish events, escalate if needed.

        Args:
            component: Component name
            result: AnomalyResult to process
        """
        # Generate unique ID
        anomaly_id = str(uuid.uuid4())[:8]

        # Store as active anomaly
        self.active_anomalies[anomaly_id] = result
        self.anomaly_count += 1

        # Store in episodic memory
        self._store_in_episodic(anomaly_id, component, result)

        # Publish event
        self._publish_anomaly_event(result)

        # Escalate if needed
        self.escalate_if_needed(result, component)

    def _store_in_episodic(self, anomaly_id: str, component: str, result: AnomalyResult):
        """
        Store anomaly in episodic memory (FAZA 12).

        Args:
            anomaly_id: Unique anomaly ID
            component: Component name
            result: AnomalyResult to store
        """
        if not self.memory_manager:
            return

        try:
            memory_data = {
                "id": anomaly_id,
                "type": "anomaly",
                "component": component,
                "score": result.score,
                "severity": result.severity,
                "reason": result.reason,
                "context": result.context,
                "timestamp": result.timestamp
            }

            # Store in episodic memory with appropriate tags
            tags = ["anomaly", component, result.severity.lower()]

            self.memory_manager.episodic_memory.store(
                event_type="ANOMALY",
                data=memory_data,
                tags=tags
            )

        except Exception as e:
            print(f"[AnomalyManager] Failed to store in episodic memory: {e}")

    def _consolidate_to_semantic(self, anomaly: AnomalyResult, resolution: str):
        """
        Consolidate resolved anomaly to semantic memory for long-term learning.

        Args:
            anomaly: Resolved anomaly
            resolution: Resolution description
        """
        if not self.memory_manager:
            return

        try:
            # Store pattern for future reference
            knowledge = {
                "pattern": anomaly.reason,
                "severity": anomaly.severity,
                "resolution": resolution,
                "learned_from": "anomaly_resolution"
            }

            self.memory_manager.semantic_memory.store(
                key=f"anomaly_pattern_{anomaly.severity}",
                value=knowledge,
                metadata={"type": "anomaly_knowledge"}
            )

        except Exception as e:
            print(f"[AnomalyManager] Failed to consolidate to semantic memory: {e}")

    def _publish_anomaly_event(self, result: AnomalyResult):
        """
        Publish anomaly event to EventBus.

        Args:
            result: AnomalyResult to publish
        """
        if not self.event_bus:
            return

        try:
            event = AnomalyEvent(
                score=result.score,
                severity=result.severity,
                reason=result.reason,
                context=result.context
            )

            self.event_bus.emit(event.event_type, event.to_dict())

        except Exception as e:
            print(f"[AnomalyManager] Failed to publish anomaly event: {e}")

    def _publish_high_severity_event(self, result: AnomalyResult, component: str):
        """
        Publish high severity event.

        Args:
            result: AnomalyResult
            component: Component name
        """
        if not self.event_bus:
            return

        try:
            event = HighSeverityEvent(
                score=result.score,
                severity=result.severity,
                reason=result.reason,
                component=component,
                details=result.context
            )

            self.event_bus.emit(event.event_type, event.to_dict())

        except Exception as e:
            print(f"[AnomalyManager] Failed to publish high severity event: {e}")

    def _publish_resolution_event(self, anomaly_id: str, resolution: str, anomaly: AnomalyResult):
        """
        Publish anomaly resolution event.

        Args:
            anomaly_id: Anomaly ID
            resolution: Resolution description
            anomaly: AnomalyResult
        """
        if not self.event_bus:
            return

        try:
            event = AnomalyResolvedEvent(
                anomaly_id=anomaly_id,
                resolution=resolution,
                details={
                    "severity": anomaly.severity,
                    "score": anomaly.score,
                    "reason": anomaly.reason
                }
            )

            self.event_bus.emit(event.event_type, event.to_dict())

        except Exception as e:
            print(f"[AnomalyManager] Failed to publish resolution event: {e}")

    def _alert_security_manager(self, anomaly: AnomalyResult, component: str):
        """
        Alert Security Manager about high severity anomaly.

        Args:
            anomaly: AnomalyResult
            component: Component name
        """
        try:
            if hasattr(self.security_manager, "handle_alert"):
                self.security_manager.handle_alert({
                    "type": "high_severity_anomaly",
                    "component": component,
                    "severity": anomaly.severity,
                    "score": anomaly.score,
                    "reason": anomaly.reason,
                    "context": anomaly.context
                })
            else:
                print(f"[AnomalyManager] Security Manager notified: {component} - {anomaly.severity}")

        except Exception as e:
            print(f"[AnomalyManager] Failed to alert Security Manager: {e}")

    def _create_disabled_result(self) -> AnomalyResult:
        """Create a result for when anomaly detection is disabled."""
        return AnomalyResult(
            score=0,
            severity="LOW",
            reason="Anomaly detection disabled",
            context={"system": "disabled"}
        )
