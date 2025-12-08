"""
LLM Health Monitor for SENTI OS FAZA 16

Tracks model health metrics including:
- Latency and response times
- Error rates and failure patterns
- Hallucination detection scores
- SPEC consistency scores
- Code quality scores
- Overall health scoring (0-100)
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"            # 70-89
    FAIR = "fair"            # 50-69
    POOR = "poor"            # 30-49
    CRITICAL = "critical"    # 0-29


@dataclass
class InteractionMetrics:
    """Metrics for a single LLM interaction."""
    model_id: str
    timestamp: str
    latency_ms: float
    success: bool
    error_type: Optional[str] = None
    hallucination_score: float = 0.0
    spec_consistency_score: float = 1.0
    code_quality_score: float = 1.0
    tokens_used: int = 0


@dataclass
class ModelHealthReport:
    """Health report for a single model."""
    model_id: str
    health_score: float
    health_status: HealthStatus
    avg_latency_ms: float
    error_rate: float
    avg_hallucination_score: float
    avg_spec_consistency: float
    avg_code_quality: float
    total_interactions: int
    recent_errors: List[str]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class LLMHealthMonitor:
    """
    Monitors health and performance of LLM models.

    Tracks:
    - Response latency
    - Error rates
    - Hallucination detection
    - SPEC consistency
    - Code quality
    - Overall health scores
    """

    def __init__(self, history_size: int = 1000, window_hours: int = 24):
        """
        Initialize health monitor.

        Args:
            history_size: Max number of interactions to keep per model
            window_hours: Time window for health calculations
        """
        self.history_size = history_size
        self.window_hours = window_hours

        # Model ID -> deque of InteractionMetrics
        self.interaction_history: Dict[str, deque] = {}

        # Model ID -> list of error messages
        self.error_log: Dict[str, List[Tuple[str, str]]] = {}

        logger.info(
            f"LLM Health Monitor initialized "
            f"(history={history_size}, window={window_hours}h)"
        )

    def record_interaction(
        self,
        model_id: str,
        latency_ms: float,
        success: bool,
        error_type: Optional[str] = None,
        hallucination_score: float = 0.0,
        spec_consistency_score: float = 1.0,
        code_quality_score: float = 1.0,
        tokens_used: int = 0,
    ) -> None:
        """
        Record a single model interaction.

        Args:
            model_id: Model identifier
            latency_ms: Response latency in milliseconds
            success: Whether interaction succeeded
            error_type: Type of error if failed
            hallucination_score: Hallucination detection score (0-1, lower is better)
            spec_consistency_score: SPEC consistency score (0-1, higher is better)
            code_quality_score: Code quality score (0-1, higher is better)
            tokens_used: Number of tokens consumed
        """
        if model_id not in self.interaction_history:
            self.interaction_history[model_id] = deque(maxlen=self.history_size)
            self.error_log[model_id] = []

        metrics = InteractionMetrics(
            model_id=model_id,
            timestamp=datetime.now().isoformat(),
            latency_ms=latency_ms,
            success=success,
            error_type=error_type,
            hallucination_score=hallucination_score,
            spec_consistency_score=spec_consistency_score,
            code_quality_score=code_quality_score,
            tokens_used=tokens_used,
        )

        self.interaction_history[model_id].append(metrics)

        if not success and error_type:
            self.error_log[model_id].append((datetime.now().isoformat(), error_type))
            # Keep only recent 100 errors
            if len(self.error_log[model_id]) > 100:
                self.error_log[model_id] = self.error_log[model_id][-100:]

        logger.debug(f"Recorded interaction for {model_id}: success={success}, latency={latency_ms}ms")

    def compute_health_score(self, model_id: str) -> float:
        """
        Compute overall health score (0-100) for a model.

        Args:
            model_id: Model identifier

        Returns:
            Health score (0-100)
        """
        if model_id not in self.interaction_history:
            return 50.0  # Default neutral score

        recent_metrics = self._get_recent_metrics(model_id)

        if not recent_metrics:
            return 50.0

        # Component scores (0-100)
        latency_score = self._compute_latency_score(recent_metrics)
        error_score = self._compute_error_score(recent_metrics)
        hallucination_score = self._compute_hallucination_score(recent_metrics)
        spec_score = self._compute_spec_score(recent_metrics)
        code_score = self._compute_code_score(recent_metrics)

        # Weighted combination
        weights = {
            "latency": 0.15,
            "error": 0.30,
            "hallucination": 0.25,
            "spec": 0.15,
            "code": 0.15,
        }

        total_score = (
            weights["latency"] * latency_score +
            weights["error"] * error_score +
            weights["hallucination"] * hallucination_score +
            weights["spec"] * spec_score +
            weights["code"] * code_score
        )

        return max(0.0, min(100.0, total_score))

    def get_health_report(self, model_id: str) -> ModelHealthReport:
        """
        Generate comprehensive health report for a model.

        Args:
            model_id: Model identifier

        Returns:
            ModelHealthReport instance
        """
        if model_id not in self.interaction_history:
            return ModelHealthReport(
                model_id=model_id,
                health_score=50.0,
                health_status=HealthStatus.FAIR,
                avg_latency_ms=0.0,
                error_rate=0.0,
                avg_hallucination_score=0.0,
                avg_spec_consistency=1.0,
                avg_code_quality=1.0,
                total_interactions=0,
                recent_errors=[],
                recommendations=["No interaction data available"],
            )

        recent_metrics = self._get_recent_metrics(model_id)

        if not recent_metrics:
            return ModelHealthReport(
                model_id=model_id,
                health_score=50.0,
                health_status=HealthStatus.FAIR,
                avg_latency_ms=0.0,
                error_rate=0.0,
                avg_hallucination_score=0.0,
                avg_spec_consistency=1.0,
                avg_code_quality=1.0,
                total_interactions=0,
                recent_errors=[],
                recommendations=["No recent interaction data"],
            )

        health_score = self.compute_health_score(model_id)
        health_status = self._score_to_status(health_score)

        avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)
        error_rate = sum(1 for m in recent_metrics if not m.success) / len(recent_metrics)
        avg_hallucination = sum(m.hallucination_score for m in recent_metrics) / len(recent_metrics)
        avg_spec = sum(m.spec_consistency_score for m in recent_metrics) / len(recent_metrics)
        avg_code = sum(m.code_quality_score for m in recent_metrics) / len(recent_metrics)

        recent_errors = self._get_recent_errors(model_id, limit=5)
        recommendations = self._generate_recommendations(
            health_score, avg_latency, error_rate, avg_hallucination
        )

        return ModelHealthReport(
            model_id=model_id,
            health_score=round(health_score, 2),
            health_status=health_status,
            avg_latency_ms=round(avg_latency, 2),
            error_rate=round(error_rate, 3),
            avg_hallucination_score=round(avg_hallucination, 3),
            avg_spec_consistency=round(avg_spec, 3),
            avg_code_quality=round(avg_code, 3),
            total_interactions=len(recent_metrics),
            recent_errors=recent_errors,
            recommendations=recommendations,
        )

    def get_all_health_reports(self) -> List[ModelHealthReport]:
        """
        Get health reports for all monitored models.

        Returns:
            List of ModelHealthReport instances
        """
        reports = []
        for model_id in self.interaction_history.keys():
            report = self.get_health_report(model_id)
            reports.append(report)

        # Sort by health score descending
        reports.sort(key=lambda r: r.health_score, reverse=True)
        return reports

    def _get_recent_metrics(self, model_id: str) -> List[InteractionMetrics]:
        """Get metrics within the time window."""
        if model_id not in self.interaction_history:
            return []

        cutoff = datetime.now() - timedelta(hours=self.window_hours)

        recent = []
        for metric in self.interaction_history[model_id]:
            try:
                metric_time = datetime.fromisoformat(metric.timestamp)
                if metric_time >= cutoff:
                    recent.append(metric)
            except (ValueError, TypeError):
                continue

        return recent

    def _compute_latency_score(self, metrics: List[InteractionMetrics]) -> float:
        """Compute latency score (0-100, higher is better)."""
        if not metrics:
            return 50.0

        avg_latency = sum(m.latency_ms for m in metrics) / len(metrics)

        # Scoring: <500ms=100, 500-2000ms=linear, >2000ms=0
        if avg_latency < 500:
            return 100.0
        elif avg_latency < 2000:
            return 100.0 - ((avg_latency - 500) / 1500 * 100)
        else:
            return 0.0

    def _compute_error_score(self, metrics: List[InteractionMetrics]) -> float:
        """Compute error score (0-100, higher is better)."""
        if not metrics:
            return 50.0

        error_rate = sum(1 for m in metrics if not m.success) / len(metrics)

        # 0% error = 100, 10% error = 50, 20%+ error = 0
        if error_rate == 0:
            return 100.0
        elif error_rate < 0.1:
            return 100.0 - (error_rate * 500)
        elif error_rate < 0.2:
            return 50.0 - ((error_rate - 0.1) * 500)
        else:
            return 0.0

    def _compute_hallucination_score(self, metrics: List[InteractionMetrics]) -> float:
        """Compute hallucination score (0-100, higher is better)."""
        if not metrics:
            return 50.0

        avg_hallucination = sum(m.hallucination_score for m in metrics) / len(metrics)

        # Hallucination score is 0-1, lower is better
        # Convert to 0-100 where higher is better
        return (1.0 - avg_hallucination) * 100.0

    def _compute_spec_score(self, metrics: List[InteractionMetrics]) -> float:
        """Compute SPEC consistency score (0-100, higher is better)."""
        if not metrics:
            return 50.0

        avg_spec = sum(m.spec_consistency_score for m in metrics) / len(metrics)

        # SPEC consistency is 0-1, higher is better
        return avg_spec * 100.0

    def _compute_code_score(self, metrics: List[InteractionMetrics]) -> float:
        """Compute code quality score (0-100, higher is better)."""
        if not metrics:
            return 50.0

        avg_code = sum(m.code_quality_score for m in metrics) / len(metrics)

        # Code quality is 0-1, higher is better
        return avg_code * 100.0

    def _score_to_status(self, score: float) -> HealthStatus:
        """Convert numeric score to health status."""
        if score >= 90:
            return HealthStatus.EXCELLENT
        elif score >= 70:
            return HealthStatus.GOOD
        elif score >= 50:
            return HealthStatus.FAIR
        elif score >= 30:
            return HealthStatus.POOR
        else:
            return HealthStatus.CRITICAL

    def _get_recent_errors(self, model_id: str, limit: int = 5) -> List[str]:
        """Get recent error messages."""
        if model_id not in self.error_log:
            return []

        recent = self.error_log[model_id][-limit:]
        return [error_type for _, error_type in recent]

    def _generate_recommendations(
        self,
        health_score: float,
        avg_latency: float,
        error_rate: float,
        avg_hallucination: float,
    ) -> List[str]:
        """Generate health improvement recommendations."""
        recommendations = []

        if health_score < 50:
            recommendations.append("Critical: Consider disabling this model temporarily")
        elif health_score < 70:
            recommendations.append("Warning: Model health is below acceptable threshold")

        if avg_latency > 2000:
            recommendations.append("High latency detected: Consider using faster model")
        elif avg_latency > 1000:
            recommendations.append("Moderate latency: Monitor performance")

        if error_rate > 0.2:
            recommendations.append("High error rate: Check API keys and connectivity")
        elif error_rate > 0.1:
            recommendations.append("Elevated error rate: Monitor for issues")

        if avg_hallucination > 0.3:
            recommendations.append("High hallucination score: Review output validation")
        elif avg_hallucination > 0.15:
            recommendations.append("Moderate hallucination: Consider stricter rules")

        if not recommendations:
            recommendations.append("Model performing within acceptable parameters")

        return recommendations

    def get_statistics(self) -> Dict:
        """
        Get overall health monitoring statistics.

        Returns:
            Dictionary with statistics
        """
        total_models = len(self.interaction_history)

        if total_models == 0:
            return {
                "total_models": 0,
                "total_interactions": 0,
                "average_health_score": 0.0,
                "healthy_models": 0,
                "unhealthy_models": 0,
            }

        total_interactions = sum(
            len(metrics) for metrics in self.interaction_history.values()
        )

        health_scores = [
            self.compute_health_score(model_id)
            for model_id in self.interaction_history.keys()
        ]

        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0.0

        healthy = sum(1 for score in health_scores if score >= 70)
        unhealthy = sum(1 for score in health_scores if score < 50)

        return {
            "total_models": total_models,
            "total_interactions": total_interactions,
            "average_health_score": round(avg_health, 2),
            "healthy_models": healthy,
            "unhealthy_models": unhealthy,
            "models_by_status": {
                status.value: sum(
                    1 for score in health_scores
                    if self._score_to_status(score) == status
                )
                for status in HealthStatus
            },
        }


def create_monitor(
    history_size: int = 1000,
    window_hours: int = 24
) -> LLMHealthMonitor:
    """
    Create and return a health monitor.

    Args:
        history_size: Max interactions to keep per model
        window_hours: Time window for calculations

    Returns:
        LLMHealthMonitor instance
    """
    return LLMHealthMonitor(history_size, window_hours)
