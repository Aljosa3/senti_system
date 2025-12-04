"""
FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise Edition)
Anomaly Detector

Detects anomalies in agent behavior using:
- Rule-based detection (explicit rules and thresholds)
- Statistical detection (outlier detection, Z-scores)
- Threshold detection (simple boundary checks)

Anomalies detected:
- Sudden score changes
- Unexpected behavior patterns
- Timing anomalies
- Event anomalies
- Missing ticks
- High error ratio
- Deviation from expected trace
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies"""
    SCORE_DROP = "score_drop"
    SCORE_SPIKE = "score_spike"
    TIMING_ANOMALY = "timing_anomaly"
    EVENT_ANOMALY = "event_anomaly"
    MISSING_TICK = "missing_tick"
    HIGH_ERROR_RATE = "high_error_rate"
    BEHAVIOR_DEVIATION = "behavior_deviation"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    STATISTICAL_OUTLIER = "statistical_outlier"


class AnomalySeverity(Enum):
    """Severity levels for anomalies"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Anomaly:
    """
    Detected anomaly.

    Attributes:
        anomaly_type: Type of anomaly
        severity: Severity level
        agent_name: Name of affected agent
        description: Human-readable description
        value: Anomalous value
        expected: Expected value (if applicable)
        confidence: Detection confidence (0.0 - 1.0)
        timestamp: When anomaly was detected
        metadata: Additional anomaly data
    """
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    agent_name: str
    description: str
    value: Any
    expected: Optional[Any] = None
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"<Anomaly: {self.anomaly_type.value} ({self.severity.name}) - {self.agent_name}>"


class AnomalyDetector:
    """
    Enterprise anomaly detection engine.

    Supports three detection methods:
    1. Rule-based: Explicit rules and thresholds
    2. Statistical: Outlier detection using Z-scores
    3. Threshold: Simple boundary checks

    Maintains history for statistical analysis.
    """

    def __init__(
        self,
        score_drop_threshold: float = 0.3,
        score_spike_threshold: float = 0.3,
        error_rate_threshold: float = 0.1,
        missing_tick_window: float = 60.0,
        outlier_z_score: float = 3.0,
        history_size: int = 100
    ):
        """
        Initialize anomaly detector.

        Args:
            score_drop_threshold: Threshold for sudden score drops
            score_spike_threshold: Threshold for sudden score spikes
            error_rate_threshold: Maximum acceptable error rate
            missing_tick_window: Time window for missing tick detection (seconds)
            outlier_z_score: Z-score threshold for statistical outliers
            history_size: Number of historical data points to keep
        """
        self.score_drop_threshold = score_drop_threshold
        self.score_spike_threshold = score_spike_threshold
        self.error_rate_threshold = error_rate_threshold
        self.missing_tick_window = missing_tick_window
        self.outlier_z_score = outlier_z_score
        self.history_size = history_size

        # Historical data for agents
        self.score_history: Dict[str, List[float]] = {}
        self.tick_history: Dict[str, List[datetime]] = {}
        self.error_history: Dict[str, List[datetime]] = {}

        # Detected anomalies
        self.anomalies: List[Anomaly] = []
        self.max_anomaly_history = 1000

        logger.info("AnomalyDetector initialized")

    def detect_all(
        self,
        agent_name: str,
        current_score: Optional[float] = None,
        tick_time: Optional[datetime] = None,
        had_error: bool = False,
        metrics: Optional[Dict[str, Any]] = None
    ) -> List[Anomaly]:
        """
        Run all anomaly detection methods.

        Args:
            agent_name: Name of agent to check
            current_score: Current meta-score
            tick_time: Timestamp of last tick
            had_error: Whether agent had an error
            metrics: Additional metrics for detection

        Returns:
            List of detected Anomaly objects

        TODO: Add detection timeout
        TODO: Add parallel detection
        """
        anomalies = []

        # Update history
        if current_score is not None:
            self._update_score_history(agent_name, current_score)

        if tick_time is not None:
            self._update_tick_history(agent_name, tick_time)

        if had_error:
            self._update_error_history(agent_name)

        # Run detection methods
        anomalies.extend(self._detect_score_anomalies(agent_name, current_score))
        anomalies.extend(self._detect_timing_anomalies(agent_name, tick_time))
        anomalies.extend(self._detect_error_anomalies(agent_name))
        anomalies.extend(self._detect_statistical_anomalies(agent_name, current_score))

        if metrics:
            anomalies.extend(self._detect_threshold_anomalies(agent_name, metrics))

        # Store detected anomalies
        for anomaly in anomalies:
            self.anomalies.append(anomaly)
            logger.warning(f"Anomaly detected: {anomaly}")

        # Limit anomaly history
        if len(self.anomalies) > self.max_anomaly_history:
            self.anomalies = self.anomalies[-self.max_anomaly_history:]

        return anomalies

    def _detect_score_anomalies(
        self,
        agent_name: str,
        current_score: Optional[float]
    ) -> List[Anomaly]:
        """
        Detect sudden score changes (rule-based).

        Args:
            agent_name: Name of agent
            current_score: Current score

        Returns:
            List of detected anomalies
        """
        if current_score is None:
            return []

        history = self.score_history.get(agent_name, [])
        if len(history) < 2:
            return []

        anomalies = []
        previous_score = history[-2]
        score_change = current_score - previous_score

        # Sudden score drop
        if score_change < -self.score_drop_threshold:
            severity = AnomalySeverity.CRITICAL if abs(score_change) > 0.5 else AnomalySeverity.HIGH
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.SCORE_DROP,
                severity=severity,
                agent_name=agent_name,
                description=f"Sudden score drop: {previous_score:.3f} -> {current_score:.3f}",
                value=current_score,
                expected=previous_score,
                confidence=min(1.0, abs(score_change) / self.score_drop_threshold)
            ))

        # Sudden score spike (may indicate manipulation)
        elif score_change > self.score_spike_threshold:
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.SCORE_SPIKE,
                severity=AnomalySeverity.MEDIUM,
                agent_name=agent_name,
                description=f"Unexpected score spike: {previous_score:.3f} -> {current_score:.3f}",
                value=current_score,
                expected=previous_score,
                confidence=min(1.0, score_change / self.score_spike_threshold)
            ))

        return anomalies

    def _detect_timing_anomalies(
        self,
        agent_name: str,
        tick_time: Optional[datetime]
    ) -> List[Anomaly]:
        """
        Detect timing anomalies (rule-based).

        Args:
            agent_name: Name of agent
            tick_time: Timestamp of tick

        Returns:
            List of detected anomalies
        """
        if tick_time is None:
            return []

        history = self.tick_history.get(agent_name, [])
        if len(history) < 2:
            return []

        anomalies = []
        last_tick = history[-2]
        time_since_tick = (tick_time - last_tick).total_seconds()

        # Missing tick detection
        if time_since_tick > self.missing_tick_window:
            severity = AnomalySeverity.HIGH if time_since_tick > 300 else AnomalySeverity.MEDIUM
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.MISSING_TICK,
                severity=severity,
                agent_name=agent_name,
                description=f"No tick for {time_since_tick:.1f}s (threshold: {self.missing_tick_window}s)",
                value=time_since_tick,
                expected=self.missing_tick_window,
                confidence=min(1.0, time_since_tick / self.missing_tick_window)
            ))

        # Calculate average tick interval
        if len(history) >= 10:
            intervals = [(history[i] - history[i-1]).total_seconds() for i in range(-10, 0)]
            avg_interval = statistics.mean(intervals)
            stdev_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

            # Detect significant deviation from average
            if stdev_interval > 0:
                deviation = abs(time_since_tick - avg_interval) / stdev_interval
                if deviation > 3.0:  # 3 standard deviations
                    anomalies.append(Anomaly(
                        anomaly_type=AnomalyType.TIMING_ANOMALY,
                        severity=AnomalySeverity.MEDIUM,
                        agent_name=agent_name,
                        description=f"Irregular tick interval: {time_since_tick:.2f}s (avg: {avg_interval:.2f}s)",
                        value=time_since_tick,
                        expected=avg_interval,
                        confidence=min(1.0, deviation / 3.0),
                        metadata={"stdev": stdev_interval, "z_score": deviation}
                    ))

        return anomalies

    def _detect_error_anomalies(self, agent_name: str) -> List[Anomaly]:
        """
        Detect error rate anomalies (rule-based).

        Args:
            agent_name: Name of agent

        Returns:
            List of detected anomalies
        """
        error_history = self.error_history.get(agent_name, [])
        tick_history = self.tick_history.get(agent_name, [])

        if not tick_history:
            return []

        anomalies = []

        # Calculate error rate over recent window
        recent_window = datetime.now() - timedelta(minutes=5)
        recent_errors = [e for e in error_history if e > recent_window]
        recent_ticks = [t for t in tick_history if t > recent_window]

        if recent_ticks:
            error_rate = len(recent_errors) / len(recent_ticks)

            if error_rate > self.error_rate_threshold:
                severity = AnomalySeverity.CRITICAL if error_rate > 0.5 else AnomalySeverity.HIGH
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.HIGH_ERROR_RATE,
                    severity=severity,
                    agent_name=agent_name,
                    description=f"High error rate: {error_rate:.1%} (threshold: {self.error_rate_threshold:.1%})",
                    value=error_rate,
                    expected=self.error_rate_threshold,
                    confidence=min(1.0, error_rate / self.error_rate_threshold)
                ))

        return anomalies

    def _detect_statistical_anomalies(
        self,
        agent_name: str,
        current_score: Optional[float]
    ) -> List[Anomaly]:
        """
        Detect statistical outliers (statistical detection).

        Uses Z-score to identify outliers in score distribution.

        Args:
            agent_name: Name of agent
            current_score: Current score

        Returns:
            List of detected anomalies
        """
        if current_score is None:
            return []

        history = self.score_history.get(agent_name, [])
        if len(history) < 30:  # Need sufficient data for statistics
            return []

        anomalies = []

        try:
            mean = statistics.mean(history)
            stdev = statistics.stdev(history)

            if stdev > 0:
                z_score = abs(current_score - mean) / stdev

                if z_score > self.outlier_z_score:
                    severity = AnomalySeverity.HIGH if z_score > 5.0 else AnomalySeverity.MEDIUM
                    anomalies.append(Anomaly(
                        anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                        severity=severity,
                        agent_name=agent_name,
                        description=f"Statistical outlier detected: Z-score={z_score:.2f}",
                        value=current_score,
                        expected=mean,
                        confidence=min(1.0, z_score / self.outlier_z_score),
                        metadata={"z_score": z_score, "mean": mean, "stdev": stdev}
                    ))

        except statistics.StatisticsError as e:
            logger.debug(f"Statistical calculation failed for {agent_name}: {e}")

        return anomalies

    def _detect_threshold_anomalies(
        self,
        agent_name: str,
        metrics: Dict[str, Any]
    ) -> List[Anomaly]:
        """
        Detect threshold violations (threshold detection).

        Args:
            agent_name: Name of agent
            metrics: Metrics to check

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Check execution time threshold
        avg_exec_time = metrics.get("avg_execution_time", 0)
        if avg_exec_time > 1.0:  # 1 second threshold
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                severity=AnomalySeverity.MEDIUM,
                agent_name=agent_name,
                description=f"Slow execution time: {avg_exec_time:.3f}s",
                value=avg_exec_time,
                expected=1.0,
                confidence=min(1.0, avg_exec_time)
            ))

        # Check event anomalies (too few or too many)
        events_total = metrics.get("events_total", 0)
        tick_count = metrics.get("tick_count", 1)
        events_per_tick = events_total / max(1, tick_count)

        if events_per_tick > 100:  # Excessive events
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.EVENT_ANOMALY,
                severity=AnomalySeverity.MEDIUM,
                agent_name=agent_name,
                description=f"Excessive event activity: {events_per_tick:.1f} events/tick",
                value=events_per_tick,
                expected=10.0,
                confidence=min(1.0, events_per_tick / 100.0)
            ))

        return anomalies

    def _update_score_history(self, agent_name: str, score: float) -> None:
        """Update score history for an agent"""
        if agent_name not in self.score_history:
            self.score_history[agent_name] = []

        self.score_history[agent_name].append(score)

        # Limit history size
        if len(self.score_history[agent_name]) > self.history_size:
            self.score_history[agent_name] = self.score_history[agent_name][-self.history_size:]

    def _update_tick_history(self, agent_name: str, tick_time: datetime) -> None:
        """Update tick history for an agent"""
        if agent_name not in self.tick_history:
            self.tick_history[agent_name] = []

        self.tick_history[agent_name].append(tick_time)

        # Limit history size
        if len(self.tick_history[agent_name]) > self.history_size:
            self.tick_history[agent_name] = self.tick_history[agent_name][-self.history_size:]

    def _update_error_history(self, agent_name: str) -> None:
        """Update error history for an agent"""
        if agent_name not in self.error_history:
            self.error_history[agent_name] = []

        self.error_history[agent_name].append(datetime.now())

        # Limit history size
        if len(self.error_history[agent_name]) > self.history_size:
            self.error_history[agent_name] = self.error_history[agent_name][-self.history_size:]

    def get_recent_anomalies(
        self,
        agent_name: Optional[str] = None,
        time_window: int = 300,
        severity: Optional[AnomalySeverity] = None
    ) -> List[Anomaly]:
        """
        Get recent anomalies.

        Args:
            agent_name: Filter by agent name (None = all agents)
            time_window: Time window in seconds
            severity: Filter by severity (None = all severities)

        Returns:
            List of Anomaly objects
        """
        cutoff_time = datetime.now() - timedelta(seconds=time_window)

        anomalies = [a for a in self.anomalies if a.timestamp > cutoff_time]

        if agent_name:
            anomalies = [a for a in anomalies if a.agent_name == agent_name]

        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]

        return anomalies

    def get_anomaly_summary(self) -> Dict[str, Any]:
        """
        Get anomaly detection summary.

        Returns:
            Dictionary with summary statistics
        """
        recent_anomalies = self.get_recent_anomalies(time_window=300)

        return {
            "total_anomalies": len(self.anomalies),
            "recent_anomalies": len(recent_anomalies),
            "anomalies_by_type": {
                at.value: len([a for a in recent_anomalies if a.anomaly_type == at])
                for at in AnomalyType
            },
            "anomalies_by_severity": {
                s.name: len([a for a in recent_anomalies if a.severity == s])
                for s in AnomalySeverity
            },
            "agents_with_anomalies": len(set(a.agent_name for a in recent_anomalies))
        }

    def clear_history(self, agent_name: Optional[str] = None) -> None:
        """
        Clear history for an agent or all agents.

        Args:
            agent_name: Agent name (None = clear all)
        """
        if agent_name:
            self.score_history.pop(agent_name, None)
            self.tick_history.pop(agent_name, None)
            self.error_history.pop(agent_name, None)
            logger.info(f"Cleared history for agent: {agent_name}")
        else:
            self.score_history.clear()
            self.tick_history.clear()
            self.error_history.clear()
            self.anomalies.clear()
            logger.info("Cleared all history")

    def __repr__(self) -> str:
        return f"<AnomalyDetector: {len(self.anomalies)} total anomalies>"


# Singleton instance
_anomaly_detector_instance: Optional[AnomalyDetector] = None


def get_anomaly_detector() -> AnomalyDetector:
    """
    Get singleton AnomalyDetector instance.

    Returns:
        Global AnomalyDetector instance
    """
    global _anomaly_detector_instance
    if _anomaly_detector_instance is None:
        _anomaly_detector_instance = AnomalyDetector()
    return _anomaly_detector_instance


def create_anomaly_detector(**kwargs) -> AnomalyDetector:
    """
    Factory function: create new AnomalyDetector instance.

    Args:
        **kwargs: Arguments passed to AnomalyDetector constructor

    Returns:
        New AnomalyDetector instance
    """
    return AnomalyDetector(**kwargs)
