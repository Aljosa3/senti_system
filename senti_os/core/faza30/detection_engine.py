"""
FAZA 30 – Enterprise Self-Healing Core
Detection Engine

Detects faults and anomalies from all FAZA layers (25/27/27.5/28/28.5/29).
Features:
- Anomaly aggregation
- Fault classification
- Health scoring
- Predictive failure analysis
- Multi-source fault detection
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class FaultSeverity(Enum):
    """Fault severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FaultSource(Enum):
    """Fault source layers"""
    FAZA25_ORCHESTRATOR = "faza25_orchestrator"
    FAZA27_TASKGRAPH = "faza27_taskgraph"
    FAZA27_5_OPTIMIZER = "faza27_5_optimizer"
    FAZA28_AGENT_LOOP = "faza28_agent_loop"
    FAZA28_5_META_LAYER = "faza28_5_meta_layer"
    FAZA29_GOVERNANCE = "faza29_governance"
    SYSTEM = "system"


@dataclass
class DetectedFault:
    """
    Detected fault record.
    
    Attributes:
        fault_id: Unique fault identifier
        source: Fault source layer
        severity: Fault severity
        fault_type: Type of fault
        description: Fault description
        metrics: Associated metrics
        timestamp: Detection timestamp
        predicted: Whether fault was predicted
    """
    fault_id: str
    source: FaultSource
    severity: FaultSeverity
    fault_type: str
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    predicted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "fault_id": self.fault_id,
            "source": self.source.value,
            "severity": self.severity.value,
            "fault_type": self.fault_type,
            "description": self.description,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat(),
            "predicted": self.predicted
        }


class AnomalyDetector:
    """Detects anomalies using statistical methods"""

    def __init__(self, window_size: int = 20, threshold: float = 3.0):
        """
        Initialize anomaly detector.
        
        Args:
            window_size: Size of sliding window
            threshold: Z-score threshold for anomaly
        """
        self.window_size = window_size
        self.threshold = threshold
        self.history: Dict[str, deque] = {}

    def detect_anomaly(self, metric_name: str, value: float) -> bool:
        """
        Detect if value is anomalous.
        
        Args:
            metric_name: Metric identifier
            value: Current value
            
        Returns:
            True if anomalous, False otherwise
        """
        if metric_name not in self.history:
            self.history[metric_name] = deque(maxlen=self.window_size)

        history = self.history[metric_name]
        
        # Need enough history
        if len(history) < self.window_size // 2:
            history.append(value)
            return False

        # Calculate z-score
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std = variance ** 0.5

        if std == 0:
            history.append(value)
            return False

        z_score = abs((value - mean) / std)
        is_anomaly = z_score > self.threshold

        history.append(value)

        return is_anomaly


class DetectionEngine:
    """
    Main fault detection engine.
    
    Aggregates faults from all FAZA layers and performs
    comprehensive health analysis.
    """

    def __init__(self):
        """Initialize detection engine"""
        # Anomaly detector
        self.anomaly_detector = AnomalyDetector()

        # Detected faults
        self.detected_faults: List[DetectedFault] = []
        self.fault_history: deque = deque(maxlen=1000)

        # Detection rules
        self.detection_rules: Dict[str, Callable] = {}
        self._init_detection_rules()

        # Statistics
        self.stats = {
            "faults_detected": 0,
            "critical_faults": 0,
            "high_faults": 0,
            "medium_faults": 0,
            "low_faults": 0,
            "anomalies_detected": 0,
            "predictions_made": 0
        }

    def _init_detection_rules(self) -> None:
        """Initialize detection rules"""
        self.detection_rules = {
            "high_error_rate": self._detect_high_error_rate,
            "agent_failure": self._detect_agent_failure,
            "graph_cycle": self._detect_graph_cycle,
            "scheduler_deadlock": self._detect_scheduler_deadlock,
            "governance_violation": self._detect_governance_violation,
            "resource_exhaustion": self._detect_resource_exhaustion,
            "stability_degradation": self._detect_stability_degradation
        }

    def detect_faults(
        self,
        faza25_metrics: Optional[Dict[str, Any]] = None,
        faza27_metrics: Optional[Dict[str, Any]] = None,
        faza28_metrics: Optional[Dict[str, Any]] = None,
        faza28_5_metrics: Optional[Dict[str, Any]] = None,
        faza29_metrics: Optional[Dict[str, Any]] = None
    ) -> List[DetectedFault]:
        """
        Detect faults from all FAZA layers.
        
        Args:
            faza25_metrics: FAZA 25 orchestrator metrics
            faza27_metrics: FAZA 27 graph metrics
            faza28_metrics: FAZA 28 agent metrics
            faza28_5_metrics: FAZA 28.5 meta-layer metrics
            faza29_metrics: FAZA 29 governance metrics
            
        Returns:
            List of detected faults
        """
        faults = []

        # Detect from each layer
        if faza25_metrics:
            faults.extend(self._detect_faza25_faults(faza25_metrics))
        if faza27_metrics:
            faults.extend(self._detect_faza27_faults(faza27_metrics))
        if faza28_metrics:
            faults.extend(self._detect_faza28_faults(faza28_metrics))
        if faza28_5_metrics:
            faults.extend(self._detect_faza28_5_faults(faza28_5_metrics))
        if faza29_metrics:
            faults.extend(self._detect_faza29_faults(faza29_metrics))

        # Store faults
        self.detected_faults.extend(faults)
        self.fault_history.extend(faults)

        # Update statistics
        self.stats["faults_detected"] += len(faults)
        for fault in faults:
            if fault.severity == FaultSeverity.CRITICAL:
                self.stats["critical_faults"] += 1
            elif fault.severity == FaultSeverity.HIGH:
                self.stats["high_faults"] += 1
            elif fault.severity == FaultSeverity.MEDIUM:
                self.stats["medium_faults"] += 1
            elif fault.severity == FaultSeverity.LOW:
                self.stats["low_faults"] += 1

        logger.info(f"Detected {len(faults)} faults across all layers")

        return faults

    def _detect_faza25_faults(self, metrics: Dict[str, Any]) -> List[DetectedFault]:
        """Detect FAZA 25 orchestrator faults"""
        faults = []

        # High error rate
        error_rate = metrics.get("error_rate", 0.0)
        if error_rate > 0.3:
            faults.append(DetectedFault(
                fault_id=f"f25_err_{datetime.now().timestamp()}",
                source=FaultSource.FAZA25_ORCHESTRATOR,
                severity=FaultSeverity.HIGH if error_rate > 0.5 else FaultSeverity.MEDIUM,
                fault_type="high_error_rate",
                description=f"High orchestrator error rate: {error_rate:.2%}",
                metrics={"error_rate": error_rate}
            ))

        # Queue overload
        queue_size = metrics.get("queue_size", 0)
        if queue_size > 100:
            faults.append(DetectedFault(
                fault_id=f"f25_queue_{datetime.now().timestamp()}",
                source=FaultSource.FAZA25_ORCHESTRATOR,
                severity=FaultSeverity.MEDIUM,
                fault_type="queue_overload",
                description=f"Task queue overloaded: {queue_size} tasks",
                metrics={"queue_size": queue_size}
            ))

        return faults

    def _detect_faza27_faults(self, metrics: Dict[str, Any]) -> List[DetectedFault]:
        """Detect FAZA 27 task graph faults"""
        faults = []

        # Cycle detection
        cycle_count = metrics.get("cycle_count", 0)
        if cycle_count > 0:
            faults.append(DetectedFault(
                fault_id=f"f27_cycle_{datetime.now().timestamp()}",
                source=FaultSource.FAZA27_TASKGRAPH,
                severity=FaultSeverity.CRITICAL,
                fault_type="graph_cycle",
                description=f"Graph contains {cycle_count} cycle(s)",
                metrics={"cycle_count": cycle_count}
            ))

        # Bottleneck detection
        bottleneck_count = metrics.get("bottleneck_count", 0)
        if bottleneck_count > 5:
            faults.append(DetectedFault(
                fault_id=f"f27_bottleneck_{datetime.now().timestamp()}",
                source=FaultSource.FAZA27_TASKGRAPH,
                severity=FaultSeverity.MEDIUM,
                fault_type="graph_bottleneck",
                description=f"Graph has {bottleneck_count} bottlenecks",
                metrics={"bottleneck_count": bottleneck_count}
            ))

        return faults

    def _detect_faza28_faults(self, metrics: Dict[str, Any]) -> List[DetectedFault]:
        """Detect FAZA 28 agent execution faults"""
        faults = []

        # Agent failure
        agent_failure_rate = metrics.get("agent_failure_rate", 0.0)
        if agent_failure_rate > 0.2:
            faults.append(DetectedFault(
                fault_id=f"f28_agent_{datetime.now().timestamp()}",
                source=FaultSource.FAZA28_AGENT_LOOP,
                severity=FaultSeverity.HIGH,
                fault_type="agent_failure",
                description=f"High agent failure rate: {agent_failure_rate:.2%}",
                metrics={"failure_rate": agent_failure_rate}
            ))

        # Scheduler deadlock
        scheduler_stuck = metrics.get("scheduler_stuck", False)
        if scheduler_stuck:
            faults.append(DetectedFault(
                fault_id=f"f28_deadlock_{datetime.now().timestamp()}",
                source=FaultSource.FAZA28_AGENT_LOOP,
                severity=FaultSeverity.CRITICAL,
                fault_type="scheduler_deadlock",
                description="Scheduler deadlock detected",
                metrics={"stuck": True}
            ))

        return faults

    def _detect_faza28_5_faults(self, metrics: Dict[str, Any]) -> List[DetectedFault]:
        """Detect FAZA 28.5 meta-layer faults"""
        faults = []

        # Stability degradation
        stability_score = metrics.get("stability_score", 1.0)
        if stability_score < 0.5:
            faults.append(DetectedFault(
                fault_id=f"f285_stability_{datetime.now().timestamp()}",
                source=FaultSource.FAZA28_5_META_LAYER,
                severity=FaultSeverity.HIGH,
                fault_type="stability_degradation",
                description=f"Low stability score: {stability_score:.2f}",
                metrics={"stability_score": stability_score}
            ))

        # Anomaly detection
        anomaly_rate = metrics.get("anomaly_rate", 0.0)
        if anomaly_rate > 0.4:
            faults.append(DetectedFault(
                fault_id=f"f285_anomaly_{datetime.now().timestamp()}",
                source=FaultSource.FAZA28_5_META_LAYER,
                severity=FaultSeverity.MEDIUM,
                fault_type="high_anomaly_rate",
                description=f"High anomaly rate: {anomaly_rate:.2%}",
                metrics={"anomaly_rate": anomaly_rate}
            ))

        return faults

    def _detect_faza29_faults(self, metrics: Dict[str, Any]) -> List[DetectedFault]:
        """Detect FAZA 29 governance faults"""
        faults = []

        # Governance violations
        violation_count = metrics.get("violation_count", 0)
        if violation_count > 0:
            faults.append(DetectedFault(
                fault_id=f"f29_violation_{datetime.now().timestamp()}",
                source=FaultSource.FAZA29_GOVERNANCE,
                severity=FaultSeverity.HIGH,
                fault_type="governance_violation",
                description=f"Governance violations detected: {violation_count}",
                metrics={"violation_count": violation_count}
            ))

        # Takeover active
        takeover_active = metrics.get("takeover_active", False)
        if takeover_active:
            faults.append(DetectedFault(
                fault_id=f"f29_takeover_{datetime.now().timestamp()}",
                source=FaultSource.FAZA29_GOVERNANCE,
                severity=FaultSeverity.CRITICAL,
                fault_type="system_takeover",
                description="System takeover active",
                metrics={"takeover": True}
            ))

        return faults

    # Detection rule implementations
    def _detect_high_error_rate(self, metrics: Dict[str, Any]) -> Optional[DetectedFault]:
        """Detect high error rate"""
        error_rate = metrics.get("error_rate", 0.0)
        if error_rate > 0.3:
            return DetectedFault(
                fault_id=f"rule_err_{datetime.now().timestamp()}",
                source=FaultSource.SYSTEM,
                severity=FaultSeverity.HIGH,
                fault_type="high_error_rate",
                description=f"System error rate: {error_rate:.2%}",
                metrics={"error_rate": error_rate}
            )
        return None

    def _detect_agent_failure(self, metrics: Dict[str, Any]) -> Optional[DetectedFault]:
        """Detect agent failures"""
        return None  # Implemented in _detect_faza28_faults

    def _detect_graph_cycle(self, metrics: Dict[str, Any]) -> Optional[DetectedFault]:
        """Detect graph cycles"""
        return None  # Implemented in _detect_faza27_faults

    def _detect_scheduler_deadlock(self, metrics: Dict[str, Any]) -> Optional[DetectedFault]:
        """Detect scheduler deadlock"""
        return None  # Implemented in _detect_faza28_faults

    def _detect_governance_violation(self, metrics: Dict[str, Any]) -> Optional[DetectedFault]:
        """Detect governance violations"""
        return None  # Implemented in _detect_faza29_faults

    def _detect_resource_exhaustion(self, metrics: Dict[str, Any]) -> Optional[DetectedFault]:
        """Detect resource exhaustion"""
        cpu_usage = metrics.get("cpu_usage", 0.0)
        memory_usage = metrics.get("memory_usage", 0.0)
        
        if cpu_usage > 0.95 or memory_usage > 0.95:
            return DetectedFault(
                fault_id=f"resource_{datetime.now().timestamp()}",
                source=FaultSource.SYSTEM,
                severity=FaultSeverity.CRITICAL,
                fault_type="resource_exhaustion",
                description="System resources exhausted",
                metrics={"cpu": cpu_usage, "memory": memory_usage}
            )
        return None

    def _detect_stability_degradation(self, metrics: Dict[str, Any]) -> Optional[DetectedFault]:
        """Detect stability degradation"""
        return None  # Implemented in _detect_faza28_5_faults

    def predict_failures(
        self,
        metrics_history: List[Dict[str, Any]]
    ) -> List[DetectedFault]:
        """
        Predict future failures based on trends.
        
        Args:
            metrics_history: Historical metrics
            
        Returns:
            List of predicted faults
        """
        if len(metrics_history) < 10:
            return []

        predictions = []

        # Analyze trends
        error_rates = [m.get("error_rate", 0.0) for m in metrics_history[-10:]]
        if len(error_rates) >= 5:
            # Check if error rate is increasing
            recent_avg = sum(error_rates[-5:]) / 5
            older_avg = sum(error_rates[:5]) / 5
            
            if recent_avg > older_avg * 1.5 and recent_avg > 0.1:
                predictions.append(DetectedFault(
                    fault_id=f"pred_err_{datetime.now().timestamp()}",
                    source=FaultSource.SYSTEM,
                    severity=FaultSeverity.MEDIUM,
                    fault_type="predicted_error_spike",
                    description="Error rate trend suggests upcoming spike",
                    metrics={"trend": "increasing", "rate": recent_avg},
                    predicted=True
                ))
                self.stats["predictions_made"] += 1

        return predictions

    def get_active_faults(self) -> List[DetectedFault]:
        """Get currently active faults"""
        # Return faults from last 5 minutes
        cutoff = datetime.now() - timedelta(minutes=5)
        return [f for f in self.detected_faults if f.timestamp >= cutoff]

    def get_critical_faults(self) -> List[DetectedFault]:
        """Get critical faults"""
        return [f for f in self.get_active_faults() if f.severity == FaultSeverity.CRITICAL]

    def clear_resolved_faults(self, fault_ids: List[str]) -> int:
        """
        Clear resolved faults.
        
        Args:
            fault_ids: List of resolved fault IDs
            
        Returns:
            Number of faults cleared
        """
        original_count = len(self.detected_faults)
        self.detected_faults = [f for f in self.detected_faults if f.fault_id not in fault_ids]
        cleared = original_count - len(self.detected_faults)
        
        logger.info(f"Cleared {cleared} resolved faults")
        return cleared

    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return {
            "faults_detected": self.stats["faults_detected"],
            "critical_faults": self.stats["critical_faults"],
            "high_faults": self.stats["high_faults"],
            "medium_faults": self.stats["medium_faults"],
            "low_faults": self.stats["low_faults"],
            "anomalies_detected": self.stats["anomalies_detected"],
            "predictions_made": self.stats["predictions_made"],
            "active_faults": len(self.get_active_faults()),
            "critical_active": len(self.get_critical_faults())
        }


def create_detection_engine() -> DetectionEngine:
    """
    Factory function to create DetectionEngine.
    
    Returns:
        DetectionEngine instance
    """
    return DetectionEngine()
