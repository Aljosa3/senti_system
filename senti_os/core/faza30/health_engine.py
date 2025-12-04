"""
FAZA 30 – Health Engine

System health scoring and trend analysis.

Provides:
- Health score computation (0-100)
- Multi-layer health metrics
- Trend analysis (improving/declining/stable)
- Health history tracking
- Component-level health breakdown

Architecture:
    HealthScore - Health score with breakdown
    HealthTrend - Trend analysis result
    HealthEngine - Main health scorer

Usage:
    from senti_os.core.faza30.health_engine import HealthEngine

    engine = HealthEngine()
    score = engine.compute_health_score(faza25_metrics, faza27_metrics, ...)
    trend = engine.analyze_trend()
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import deque


class HealthLevel(Enum):
    """Health level classification."""
    EXCELLENT = "excellent"     # 90-100
    GOOD = "good"               # 75-89
    FAIR = "fair"               # 60-74
    POOR = "poor"               # 40-59
    CRITICAL = "critical"       # 0-39


class TrendDirection(Enum):
    """Health trend direction."""
    IMPROVING = "improving"     # Health increasing
    STABLE = "stable"           # Health stable
    DECLINING = "declining"     # Health decreasing
    VOLATILE = "volatile"       # Health fluctuating


@dataclass
class HealthComponent:
    """
    Health score component.

    Attributes:
        name: Component name
        score: Component score (0-100)
        weight: Component weight in overall score
        details: Additional component details
    """
    name: str
    score: float
    weight: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthScore:
    """
    Complete system health score.

    Attributes:
        overall_score: Overall health (0-100)
        level: Health level classification
        components: Health breakdown by component
        timestamp: When score was computed
        metadata: Additional scoring metadata
    """
    overall_score: float
    level: HealthLevel
    components: List[HealthComponent] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthTrend:
    """
    Health trend analysis.

    Attributes:
        direction: Trend direction
        slope: Rate of change
        confidence: Trend confidence (0-1)
        window_size: Analysis window size
        recent_scores: Recent health scores
        prediction: Predicted next score
    """
    direction: TrendDirection
    slope: float
    confidence: float
    window_size: int
    recent_scores: List[float] = field(default_factory=list)
    prediction: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class HealthEngine:
    """
    System health scoring and trend analysis engine.

    Computes health score (0-100) from multiple layers:
    - FAZA 25 (Orchestrator)
    - FAZA 27/27.5 (Task Graph)
    - FAZA 28 (Agent Loop)
    - FAZA 28.5 (Meta Layer)
    - FAZA 29 (Governance)
    - FAZA 30 (Self-Healing)

    Features:
    - Multi-component health scoring
    - Weighted aggregation
    - Trend analysis with prediction
    - Health history tracking
    - Component-level breakdown
    """

    def __init__(self, history_size: int = 100):
        """
        Initialize health engine.

        Args:
            history_size: Number of health scores to keep in history
        """
        self.history_size = history_size
        self._health_history: deque = deque(maxlen=history_size)

        # Component weights (must sum to 1.0)
        self._component_weights = {
            "faza25_orchestrator": 0.20,
            "faza27_taskgraph": 0.20,
            "faza28_agent_loop": 0.20,
            "faza28_5_meta_layer": 0.15,
            "faza29_governance": 0.15,
            "faza30_self_healing": 0.10
        }

        self._stats = {
            "total_scores_computed": 0,
            "avg_health": 0.0,
            "min_health": 100.0,
            "max_health": 0.0
        }

    def compute_health_score(
        self,
        faza25_metrics: Optional[Dict] = None,
        faza27_metrics: Optional[Dict] = None,
        faza28_metrics: Optional[Dict] = None,
        faza28_5_metrics: Optional[Dict] = None,
        faza29_metrics: Optional[Dict] = None,
        faza30_metrics: Optional[Dict] = None
    ) -> HealthScore:
        """
        Compute overall system health score.

        Args:
            faza25_metrics: FAZA 25 metrics
            faza27_metrics: FAZA 27 metrics
            faza28_metrics: FAZA 28 metrics
            faza28_5_metrics: FAZA 28.5 metrics
            faza29_metrics: FAZA 29 metrics
            faza30_metrics: FAZA 30 metrics

        Returns:
            HealthScore with overall score and component breakdown
        """
        components: List[HealthComponent] = []

        # Compute component scores
        faza25_score = self._compute_faza25_health(faza25_metrics or {})
        components.append(HealthComponent(
            name="faza25_orchestrator",
            score=faza25_score,
            weight=self._component_weights["faza25_orchestrator"],
            details={"metrics": faza25_metrics or {}}
        ))

        faza27_score = self._compute_faza27_health(faza27_metrics or {})
        components.append(HealthComponent(
            name="faza27_taskgraph",
            score=faza27_score,
            weight=self._component_weights["faza27_taskgraph"],
            details={"metrics": faza27_metrics or {}}
        ))

        faza28_score = self._compute_faza28_health(faza28_metrics or {})
        components.append(HealthComponent(
            name="faza28_agent_loop",
            score=faza28_score,
            weight=self._component_weights["faza28_agent_loop"],
            details={"metrics": faza28_metrics or {}}
        ))

        faza28_5_score = self._compute_faza28_5_health(faza28_5_metrics or {})
        components.append(HealthComponent(
            name="faza28_5_meta_layer",
            score=faza28_5_score,
            weight=self._component_weights["faza28_5_meta_layer"],
            details={"metrics": faza28_5_metrics or {}}
        ))

        faza29_score = self._compute_faza29_health(faza29_metrics or {})
        components.append(HealthComponent(
            name="faza29_governance",
            score=faza29_score,
            weight=self._component_weights["faza29_governance"],
            details={"metrics": faza29_metrics or {}}
        ))

        faza30_score = self._compute_faza30_health(faza30_metrics or {})
        components.append(HealthComponent(
            name="faza30_self_healing",
            score=faza30_score,
            weight=self._component_weights["faza30_self_healing"],
            details={"metrics": faza30_metrics or {}}
        ))

        # Compute weighted overall score
        overall_score = sum(c.score * c.weight for c in components)
        overall_score = max(0.0, min(100.0, overall_score))

        # Classify health level
        level = self._classify_health_level(overall_score)

        # Create health score
        health_score = HealthScore(
            overall_score=overall_score,
            level=level,
            components=components,
            metadata={
                "component_count": len(components),
                "lowest_component": min(components, key=lambda c: c.score).name,
                "highest_component": max(components, key=lambda c: c.score).name
            }
        )

        # Update history and stats
        self._health_history.append(overall_score)
        self._update_statistics(overall_score)

        return health_score

    def _compute_faza25_health(self, metrics: Dict[str, Any]) -> float:
        """Compute FAZA 25 orchestrator health."""
        score = 100.0

        # Queue health
        queue_size = metrics.get('queue_size', 0)
        if queue_size > 100:
            score -= 20
        elif queue_size > 50:
            score -= 10

        # Task success rate
        success_rate = metrics.get('task_success_rate', 1.0)
        score -= (1.0 - success_rate) * 30

        # Scheduler efficiency
        scheduler_efficiency = metrics.get('scheduler_efficiency', 1.0)
        score -= (1.0 - scheduler_efficiency) * 20

        # Resource usage
        cpu_usage = metrics.get('cpu_usage', 0.0)
        if cpu_usage > 0.9:
            score -= 15

        return max(0.0, min(100.0, score))

    def _compute_faza27_health(self, metrics: Dict[str, Any]) -> float:
        """Compute FAZA 27 task graph health."""
        score = 100.0

        # Graph complexity
        complexity = metrics.get('graph_complexity', 0)
        if complexity > 200:
            score -= 25
        elif complexity > 100:
            score -= 10

        # Cycle count
        cycle_count = metrics.get('cycle_count', 0)
        score -= min(cycle_count * 10, 30)

        # Bottlenecks
        if metrics.get('bottleneck_detected', False):
            score -= 20

        # Optimization health
        optimization_score = metrics.get('optimization_score', 1.0)
        score -= (1.0 - optimization_score) * 15

        return max(0.0, min(100.0, score))

    def _compute_faza28_health(self, metrics: Dict[str, Any]) -> float:
        """Compute FAZA 28 agent loop health."""
        score = 100.0

        # Agent failure rate
        failure_rate = metrics.get('agent_failure_rate', 0.0)
        score -= failure_rate * 40

        # Cooperation score
        cooperation = metrics.get('cooperation_score', 1.0)
        score -= (1.0 - cooperation) * 25

        # Agent performance
        performance = metrics.get('agent_performance', 1.0)
        score -= (1.0 - performance) * 20

        # Communication health
        comm_health = metrics.get('communication_health', 1.0)
        score -= (1.0 - comm_health) * 15

        return max(0.0, min(100.0, score))

    def _compute_faza28_5_health(self, metrics: Dict[str, Any]) -> float:
        """Compute FAZA 28.5 meta layer health."""
        score = 100.0

        # Meta stability
        stability = metrics.get('stability_score', 1.0)
        score -= (1.0 - stability) * 35

        # Policy effectiveness
        policy_effectiveness = metrics.get('policy_effectiveness', 1.0)
        score -= (1.0 - policy_effectiveness) * 25

        # Anomaly count
        anomaly_count = metrics.get('anomaly_count', 0)
        score -= min(anomaly_count * 5, 20)

        # Feedback health
        feedback_health = metrics.get('feedback_health', 1.0)
        score -= (1.0 - feedback_health) * 20

        return max(0.0, min(100.0, score))

    def _compute_faza29_health(self, metrics: Dict[str, Any]) -> float:
        """Compute FAZA 29 governance health."""
        score = 100.0

        # Governance violations
        violations = metrics.get('governance_violations', 0)
        score -= min(violations * 5, 30)

        # Takeover state
        if metrics.get('takeover_active', False):
            score -= 25

        # Override abuse
        override_count = metrics.get('override_count', 0)
        if override_count > 10:
            score -= 15

        # Risk score (FAZA 29 computes 0-100 risk, invert for health)
        risk_score = metrics.get('risk_score', 0)
        score -= risk_score * 0.3

        return max(0.0, min(100.0, score))

    def _compute_faza30_health(self, metrics: Dict[str, Any]) -> float:
        """Compute FAZA 30 self-healing health."""
        score = 100.0

        # Active faults
        active_faults = metrics.get('active_faults', 0)
        score -= min(active_faults * 5, 30)

        # Repair success rate
        repair_success_rate = metrics.get('repair_success_rate', 1.0)
        score -= (1.0 - repair_success_rate) * 25

        # Critical faults
        critical_faults = metrics.get('critical_faults', 0)
        score -= critical_faults * 10

        # Healing cycles
        failed_cycles = metrics.get('failed_healing_cycles', 0)
        score -= min(failed_cycles * 5, 15)

        return max(0.0, min(100.0, score))

    def _classify_health_level(self, score: float) -> HealthLevel:
        """Classify health score into level."""
        if score >= 90:
            return HealthLevel.EXCELLENT
        elif score >= 75:
            return HealthLevel.GOOD
        elif score >= 60:
            return HealthLevel.FAIR
        elif score >= 40:
            return HealthLevel.POOR
        else:
            return HealthLevel.CRITICAL

    def analyze_trend(self, window_size: int = 10) -> HealthTrend:
        """
        Analyze health trend over recent history.

        Args:
            window_size: Number of recent scores to analyze

        Returns:
            HealthTrend with direction and prediction
        """
        if len(self._health_history) < 2:
            return HealthTrend(
                direction=TrendDirection.STABLE,
                slope=0.0,
                confidence=0.0,
                window_size=0,
                recent_scores=list(self._health_history)
            )

        # Get recent scores
        recent = list(self._health_history)[-window_size:]

        # Compute simple linear regression
        slope, confidence = self._compute_trend_slope(recent)

        # Determine direction
        direction = self._determine_trend_direction(slope, recent)

        # Predict next score
        prediction = recent[-1] + slope if recent else 50.0
        prediction = max(0.0, min(100.0, prediction))

        return HealthTrend(
            direction=direction,
            slope=slope,
            confidence=confidence,
            window_size=len(recent),
            recent_scores=recent,
            prediction=prediction
        )

    def _compute_trend_slope(self, scores: List[float]) -> Tuple[float, float]:
        """
        Compute trend slope using linear regression.

        Returns:
            Tuple of (slope, confidence)
        """
        n = len(scores)
        if n < 2:
            return 0.0, 0.0

        # Simple linear regression
        x = list(range(n))
        y = scores

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0, 0.0

        slope = numerator / denominator

        # Confidence based on R-squared
        y_pred = [slope * (i - x_mean) + y_mean for i in x]
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        confidence = max(0.0, min(1.0, r_squared))

        return slope, confidence

    def _determine_trend_direction(self, slope: float, scores: List[float]) -> TrendDirection:
        """Determine trend direction from slope."""
        # Check volatility
        if len(scores) >= 3:
            variance = sum((s - sum(scores) / len(scores)) ** 2 for s in scores) / len(scores)
            if variance > 100:  # High variance
                return TrendDirection.VOLATILE

        # Determine direction from slope
        if abs(slope) < 0.5:
            return TrendDirection.STABLE
        elif slope > 0:
            return TrendDirection.IMPROVING
        else:
            return TrendDirection.DECLINING

    def _update_statistics(self, score: float) -> None:
        """Update health statistics."""
        self._stats["total_scores_computed"] += 1

        # Update average
        total = self._stats["total_scores_computed"]
        current_avg = self._stats["avg_health"]
        new_avg = (current_avg * (total - 1) + score) / total
        self._stats["avg_health"] = new_avg

        # Update min/max
        self._stats["min_health"] = min(self._stats["min_health"], score)
        self._stats["max_health"] = max(self._stats["max_health"], score)

    def get_statistics(self) -> Dict[str, Any]:
        """Get health engine statistics."""
        trend = self.analyze_trend()

        return {
            **self._stats,
            "history_size": len(self._health_history),
            "current_trend": trend.direction.value,
            "trend_slope": trend.slope
        }

    def get_health_history(self, limit: int = 50) -> List[float]:
        """Get recent health history."""
        return list(self._health_history)[-limit:]


def create_health_engine(history_size: int = 100) -> HealthEngine:
    """
    Factory function to create HealthEngine.

    Args:
        history_size: Number of health scores to track

    Returns:
        Initialized HealthEngine instance
    """
    return HealthEngine(history_size=history_size)
