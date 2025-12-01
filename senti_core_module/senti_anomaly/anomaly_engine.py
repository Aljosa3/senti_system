"""
FAZA 14 - Anomaly Detection Engine
Core anomaly detection mechanism for Senti OS

Provides statistical, pattern, and rule-based anomaly detection
with integration to FAZA 5, 8, 12, and 13.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics
import math


class AnomalyResult:
    """
    Represents an anomaly detection result.
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
        Initialize anomaly result.

        Args:
            score: Anomaly score (0-100)
            severity: Severity level (LOW|MEDIUM|HIGH|CRITICAL)
            reason: Description of the anomaly
            context: Additional context data
            timestamp: ISO format timestamp (auto-generated if None)
        """
        self.score = score
        self.severity = severity
        self.reason = reason
        self.context = context
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "score": self.score,
            "severity": self.severity,
            "reason": self.reason,
            "context": self.context,
            "timestamp": self.timestamp
        }


class AnomalyEngine:
    """
    Core anomaly detection engine.
    Provides statistical, pattern, and rule-based detection.
    """

    def __init__(self, memory_manager=None, prediction_manager=None):
        """
        Initialize the anomaly detection engine.

        Args:
            memory_manager: FAZA 12 Memory Manager instance
            prediction_manager: FAZA 13 Prediction Manager instance
        """
        self.memory_manager = memory_manager
        self.prediction_manager = prediction_manager
        self.detection_history = []
        self.baseline_stats = {}

    def detect_statistical_anomaly(self, data: List[float]) -> AnomalyResult:
        """
        Detect statistical anomalies using Z-score analysis.

        Args:
            data: Numerical data points for analysis

        Returns:
            AnomalyResult with statistical anomaly detection
        """
        if not data or len(data) < 2:
            return AnomalyResult(
                score=0,
                severity="LOW",
                reason="Insufficient data for statistical analysis",
                context={"data_points": len(data) if data else 0}
            )

        try:
            mean = statistics.mean(data)
            stdev = statistics.stdev(data) if len(data) > 1 else 0

            if stdev == 0:
                return AnomalyResult(
                    score=0,
                    severity="LOW",
                    reason="No variance in data",
                    context={"mean": mean, "stdev": 0}
                )

            # Calculate Z-scores for recent values
            recent_values = data[-5:] if len(data) >= 5 else data
            z_scores = [(x - mean) / stdev for x in recent_values]
            max_z = max(abs(z) for z in z_scores)

            # Determine anomaly score based on Z-score
            score = min(100, int(max_z * 20))  # Z-score of 5 = score 100

            # Classify severity
            severity = self.classify_severity(score)

            reason = f"Statistical deviation detected (Z-score: {max_z:.2f})"
            if max_z > 3:
                reason = f"Extreme statistical deviation (Z-score: {max_z:.2f})"

            result = AnomalyResult(
                score=score,
                severity=severity,
                reason=reason,
                context={
                    "mean": round(mean, 2),
                    "stdev": round(stdev, 2),
                    "max_z_score": round(max_z, 2),
                    "data_points": len(data)
                }
            )

            self.detection_history.append(result)
            return result

        except Exception as e:
            return AnomalyResult(
                score=0,
                severity="LOW",
                reason=f"Statistical analysis failed: {str(e)}",
                context={"error": str(e)}
            )

    def detect_pattern_anomaly(self, events: List[Dict[str, Any]]) -> AnomalyResult:
        """
        Detect pattern anomalies through event frequency analysis.

        Args:
            events: List of event dictionaries

        Returns:
            AnomalyResult with pattern anomaly detection
        """
        if not events:
            return AnomalyResult(
                score=0,
                severity="LOW",
                reason="No events to analyze",
                context={"event_count": 0}
            )

        try:
            # Analyze event frequency
            event_types = [e.get("event_type", "unknown") for e in events]
            type_freq = {}
            for et in event_types:
                type_freq[et] = type_freq.get(et, 0) + 1

            # Calculate baseline frequency
            avg_freq = len(events) / len(type_freq) if type_freq else 0

            # Find anomalous frequencies
            anomalies = []
            for event_type, freq in type_freq.items():
                if avg_freq > 0 and freq > avg_freq * 2:
                    anomalies.append((event_type, freq))

            if not anomalies:
                return AnomalyResult(
                    score=10,
                    severity="LOW",
                    reason="Normal event pattern",
                    context={
                        "event_count": len(events),
                        "unique_types": len(type_freq)
                    }
                )

            # Calculate anomaly score
            max_freq = max(freq for _, freq in anomalies)
            score = min(100, int((max_freq / avg_freq) * 15))

            severity = self.classify_severity(score)

            anomaly_types = [et for et, _ in anomalies]
            reason = f"Pattern drift detected in event types: {', '.join(anomaly_types[:3])}"

            result = AnomalyResult(
                score=score,
                severity=severity,
                reason=reason,
                context={
                    "event_count": len(events),
                    "anomalous_types": anomaly_types,
                    "frequencies": {et: freq for et, freq in anomalies}
                }
            )

            self.detection_history.append(result)
            return result

        except Exception as e:
            return AnomalyResult(
                score=0,
                severity="LOW",
                reason=f"Pattern analysis failed: {str(e)}",
                context={"error": str(e)}
            )

    def detect_rule_anomaly(self, event: Dict[str, Any], rules=None) -> AnomalyResult:
        """
        Detect rule-based anomalies (security violations, policy breaches).

        Args:
            event: Event to check against rules
            rules: Optional AnomalyRules instance

        Returns:
            AnomalyResult with rule violation detection
        """
        violations = []

        # Check for sensitive data patterns
        event_str = str(event).lower()
        sensitive_patterns = [
            "password", "secret", "api_key", "token",
            "credential", "private_key"
        ]

        for pattern in sensitive_patterns:
            if pattern in event_str:
                violations.append(f"Sensitive data pattern: {pattern}")

        # Check event size
        if len(str(event)) > 2000:
            violations.append("Event size exceeds limit")

        # Check for rapid event generation (if we have history)
        recent_events = [e for e in self.detection_history[-10:] if e]
        if len(recent_events) > 8:
            # More than 8 anomalies in last 10 detections
            violations.append("Abnormally high anomaly frequency")

        if not violations:
            return AnomalyResult(
                score=0,
                severity="LOW",
                reason="No rule violations detected",
                context={"event_type": event.get("type", "unknown")}
            )

        # Calculate score based on violations
        score = min(100, len(violations) * 30)
        severity = self.classify_severity(score)

        reason = f"Rule violations: {'; '.join(violations)}"

        result = AnomalyResult(
            score=score,
            severity=severity,
            reason=reason,
            context={
                "violations": violations,
                "event_type": event.get("type", "unknown")
            }
        )

        self.detection_history.append(result)
        return result

    def detect_for(self, component_name: str, context: Dict[str, Any]) -> AnomalyResult:
        """
        Detect anomalies for a specific component.

        Args:
            component_name: Name of component to analyze
            context: Component context data

        Returns:
            AnomalyResult for the component
        """
        # Gather data from memory systems
        data_points = []
        events = []

        if self.memory_manager:
            try:
                # Get working memory data
                working_data = self.memory_manager.working_memory.get_all()
                if working_data:
                    data_points.extend([len(str(d)) for d in working_data[:10]])

                # Get episodic events
                episodic_data = self.memory_manager.episodic_memory.recall_by_tags(
                    [component_name, "anomaly"]
                )
                if episodic_data:
                    events.extend(episodic_data[:20])

            except Exception as e:
                pass  # Continue with available data

        # Combine predictions if available
        if self.prediction_manager:
            try:
                prediction = self.prediction_manager.get_last_prediction()
                if prediction and prediction.risk_score > 50:
                    data_points.append(prediction.risk_score)
            except Exception as e:
                pass

        # Perform multi-method detection
        results = []

        if data_points:
            results.append(self.detect_statistical_anomaly(data_points))

        if events:
            results.append(self.detect_pattern_anomaly(events))

        # Always check rules
        results.append(self.detect_rule_anomaly(context))

        # Return highest severity result
        if results:
            highest = max(results, key=lambda r: r.score)
            highest.context["component"] = component_name
            return highest

        return AnomalyResult(
            score=0,
            severity="LOW",
            reason="No anomalies detected",
            context={"component": component_name}
        )

    def compute_anomaly_score(
        self,
        statistical_score: int = 0,
        pattern_score: int = 0,
        rule_score: int = 0,
        weights: Optional[Dict[str, float]] = None
    ) -> int:
        """
        Compute weighted anomaly score from multiple detection methods.

        Args:
            statistical_score: Score from statistical detection
            pattern_score: Score from pattern detection
            rule_score: Score from rule detection
            weights: Optional weight dictionary

        Returns:
            Weighted anomaly score (0-100)
        """
        if weights is None:
            weights = {
                "statistical": 0.3,
                "pattern": 0.3,
                "rule": 0.4
            }

        weighted_score = (
            statistical_score * weights.get("statistical", 0.3) +
            pattern_score * weights.get("pattern", 0.3) +
            rule_score * weights.get("rule", 0.4)
        )

        return min(100, int(weighted_score))

    def classify_severity(self, score: int) -> str:
        """
        Classify anomaly severity based on score.

        Args:
            score: Anomaly score (0-100)

        Returns:
            Severity level: LOW, MEDIUM, HIGH, or CRITICAL
        """
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 30:
            return "MEDIUM"
        else:
            return "LOW"

    def update_baseline(self, component: str, data: List[float]):
        """
        Update baseline statistics for a component.

        Args:
            component: Component name
            data: Data points for baseline calculation
        """
        if not data or len(data) < 2:
            return

        try:
            self.baseline_stats[component] = {
                "mean": statistics.mean(data),
                "stdev": statistics.stdev(data) if len(data) > 1 else 0,
                "count": len(data),
                "updated": datetime.now().isoformat()
            }
        except Exception as e:
            pass

    def get_baseline(self, component: str) -> Optional[Dict[str, Any]]:
        """
        Get baseline statistics for a component.

        Args:
            component: Component name

        Returns:
            Baseline statistics or None
        """
        return self.baseline_stats.get(component)

    def get_detection_stats(self) -> Dict[str, Any]:
        """
        Get detection statistics.

        Returns:
            Statistics dictionary
        """
        if not self.detection_history:
            return {
                "total_detections": 0,
                "avg_score": 0,
                "severity_counts": {}
            }

        severity_counts = {}
        total_score = 0

        for result in self.detection_history:
            severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1
            total_score += result.score

        return {
            "total_detections": len(self.detection_history),
            "avg_score": round(total_score / len(self.detection_history), 2),
            "severity_counts": severity_counts
        }

    def clear_history(self):
        """Clear detection history."""
        self.detection_history.clear()
