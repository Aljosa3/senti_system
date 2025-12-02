"""
Reliability Feedback Loop for SENTI OS FAZA 17

This module learns from task outcomes and adjusts model reliability:
- Tracks success/failure rates per model
- Adjusts reliability scores dynamically
- Integrates with FAZA 16 source registry
- Prevents rapid score oscillation
- Provides trend analysis

The feedback loop ensures models are evaluated based on actual performance.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from statistics import mean


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutcomeType(Enum):
    """Types of task outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class FeedbackEntry:
    """Represents a single feedback entry."""
    model_id: str
    task_id: str
    outcome: OutcomeType
    confidence_claimed: float
    actual_quality: float
    processing_time: float
    cost: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class ModelMetrics:
    """Metrics for a model."""
    model_id: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float
    average_quality: float
    average_processing_time: float
    total_cost: float
    current_reliability: float
    reliability_trend: str
    last_updated: str


class ReliabilityFeedbackLoop:
    """
    Learns from task outcomes to adjust model reliability scores.

    This loop provides continuous improvement by tracking model
    performance and adjusting reliability scores accordingly.
    """

    LEARNING_RATE = 0.1
    MIN_RELIABILITY = 0.1
    MAX_RELIABILITY = 1.0
    MIN_SAMPLES_FOR_UPDATE = 3
    STABILITY_WINDOW_HOURS = 24

    def __init__(self, faza16_registry=None):
        """
        Initialize the reliability feedback loop.

        Args:
            faza16_registry: Optional FAZA 16 SourceRegistry for integration
        """
        self.faza16_registry = faza16_registry
        self.feedback_history: List[FeedbackEntry] = []
        self.model_metrics: Dict[str, ModelMetrics] = {}

        logger.info("Reliability Feedback Loop initialized")

    def record_outcome(
        self,
        model_id: str,
        task_id: str,
        outcome: OutcomeType,
        confidence_claimed: float,
        actual_quality: float,
        processing_time: float = 0.0,
        cost: float = 0.0,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Record a task outcome for a model.

        Args:
            model_id: ID of the model
            task_id: ID of the task
            outcome: Outcome type
            confidence_claimed: Confidence model claimed
            actual_quality: Actual quality achieved (0.0-1.0)
            processing_time: Time taken in seconds
            cost: Cost incurred
            metadata: Optional additional metadata
        """
        entry = FeedbackEntry(
            model_id=model_id,
            task_id=task_id,
            outcome=outcome,
            confidence_claimed=confidence_claimed,
            actual_quality=actual_quality,
            processing_time=processing_time,
            cost=cost,
            metadata=metadata or {},
        )

        self.feedback_history.append(entry)

        self._update_model_metrics(model_id)

        logger.debug(f"Outcome recorded for {model_id}: {outcome.value}")

    def update_reliability_scores(self) -> Dict[str, float]:
        """
        Update reliability scores for all models based on recent feedback.

        Returns:
            Dictionary mapping model_id to new reliability score
        """
        updated_scores = {}

        for model_id in self.model_metrics.keys():
            new_score = self._calculate_new_reliability(model_id)

            if new_score is not None:
                old_score = self.model_metrics[model_id].current_reliability
                self.model_metrics[model_id].current_reliability = new_score
                self.model_metrics[model_id].last_updated = datetime.now().isoformat()

                updated_scores[model_id] = new_score

                if self.faza16_registry:
                    try:
                        self.faza16_registry.update_reliability_score(
                            model_id,
                            success=(new_score > old_score),
                            weight=abs(new_score - old_score),
                        )
                    except Exception as e:
                        logger.warning(f"Failed to update FAZA 16 registry: {e}")

                logger.info(f"Reliability updated for {model_id}: {old_score:.3f} -> {new_score:.3f}")

        return updated_scores

    def _update_model_metrics(self, model_id: str) -> None:
        """
        Update metrics for a specific model.

        Args:
            model_id: ID of the model
        """
        entries = [e for e in self.feedback_history if e.model_id == model_id]

        if not entries:
            return

        total = len(entries)
        successful = sum(1 for e in entries if e.outcome == OutcomeType.SUCCESS)
        failed = sum(1 for e in entries if e.outcome == OutcomeType.FAILURE)

        success_rate = successful / total if total > 0 else 0.0

        avg_quality = mean(e.actual_quality for e in entries)
        avg_time = mean(e.processing_time for e in entries)
        total_cost = sum(e.cost for e in entries)

        current_reliability = self.model_metrics[model_id].current_reliability if model_id in self.model_metrics else 0.5

        trend = self._calculate_trend(model_id)

        self.model_metrics[model_id] = ModelMetrics(
            model_id=model_id,
            total_tasks=total,
            successful_tasks=successful,
            failed_tasks=failed,
            success_rate=success_rate,
            average_quality=avg_quality,
            average_processing_time=avg_time,
            total_cost=total_cost,
            current_reliability=current_reliability,
            reliability_trend=trend,
            last_updated=datetime.now().isoformat(),
        )

    def _calculate_new_reliability(self, model_id: str) -> Optional[float]:
        """
        Calculate new reliability score for a model.

        Args:
            model_id: ID of the model

        Returns:
            New reliability score or None if insufficient data
        """
        if model_id not in self.model_metrics:
            return None

        metrics = self.model_metrics[model_id]

        if metrics.total_tasks < self.MIN_SAMPLES_FOR_UPDATE:
            return None

        performance_score = (
            metrics.success_rate * 0.5 +
            metrics.average_quality * 0.3 +
            self._calibration_score(model_id) * 0.2
        )

        current = metrics.current_reliability
        target = performance_score

        new_score = current + self.LEARNING_RATE * (target - current)

        new_score = max(self.MIN_RELIABILITY, min(self.MAX_RELIABILITY, new_score))

        return new_score

    def _calibration_score(self, model_id: str) -> float:
        """
        Calculate calibration score (how well confidence matches quality).

        Args:
            model_id: ID of the model

        Returns:
            Calibration score (0.0-1.0)
        """
        entries = [e for e in self.feedback_history if e.model_id == model_id]

        if not entries:
            return 0.5

        calibration_errors = [
            abs(e.confidence_claimed - e.actual_quality)
            for e in entries
        ]

        avg_error = mean(calibration_errors)

        calibration_score = max(0.0, 1.0 - avg_error)

        return calibration_score

    def _calculate_trend(self, model_id: str) -> str:
        """
        Calculate reliability trend for a model.

        Args:
            model_id: ID of the model

        Returns:
            Trend description
        """
        cutoff_time = datetime.now() - timedelta(hours=self.STABILITY_WINDOW_HOURS)

        recent_entries = [
            e for e in self.feedback_history
            if e.model_id == model_id and datetime.fromisoformat(e.timestamp) > cutoff_time
        ]

        if len(recent_entries) < 5:
            return "insufficient_data"

        mid_point = len(recent_entries) // 2
        first_half = recent_entries[:mid_point]
        second_half = recent_entries[mid_point:]

        first_half_success = sum(1 for e in first_half if e.outcome == OutcomeType.SUCCESS) / len(first_half)
        second_half_success = sum(1 for e in second_half if e.outcome == OutcomeType.SUCCESS) / len(second_half)

        diff = second_half_success - first_half_success

        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"

    def get_model_metrics(self, model_id: str) -> Optional[ModelMetrics]:
        """
        Get metrics for a specific model.

        Args:
            model_id: ID of the model

        Returns:
            ModelMetrics if available, None otherwise
        """
        return self.model_metrics.get(model_id)

    def get_all_metrics(self) -> Dict[str, ModelMetrics]:
        """
        Get metrics for all models.

        Returns:
            Dictionary of model metrics
        """
        return self.model_metrics.copy()

    def get_top_models(self, n: int = 5) -> List[ModelMetrics]:
        """
        Get top N models by reliability.

        Args:
            n: Number of models to return

        Returns:
            List of top ModelMetrics
        """
        sorted_models = sorted(
            self.model_metrics.values(),
            key=lambda m: m.current_reliability,
            reverse=True,
        )

        return sorted_models[:n]

    def get_statistics(self) -> Dict:
        """
        Get feedback loop statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.feedback_history:
            return {
                "total_feedback_entries": 0,
                "total_models_tracked": 0,
                "overall_success_rate": 0.0,
                "average_reliability": 0.0,
            }

        total_entries = len(self.feedback_history)
        total_models = len(self.model_metrics)

        successful = sum(1 for e in self.feedback_history if e.outcome == OutcomeType.SUCCESS)
        success_rate = successful / total_entries if total_entries > 0 else 0.0

        avg_reliability = mean(m.current_reliability for m in self.model_metrics.values()) if self.model_metrics else 0.0

        return {
            "total_feedback_entries": total_entries,
            "total_models_tracked": total_models,
            "overall_success_rate": round(success_rate, 3),
            "average_reliability": round(avg_reliability, 3),
            "models_improving": sum(1 for m in self.model_metrics.values() if m.reliability_trend == "improving"),
            "models_declining": sum(1 for m in self.model_metrics.values() if m.reliability_trend == "declining"),
        }

    def clear_old_feedback(self, days: int = 30) -> int:
        """
        Clear feedback entries older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of entries removed
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        original_count = len(self.feedback_history)

        self.feedback_history = [
            e for e in self.feedback_history
            if datetime.fromisoformat(e.timestamp) > cutoff_time
        ]

        removed = original_count - len(self.feedback_history)

        if removed > 0:
            logger.info(f"Cleared {removed} old feedback entries")

            for model_id in self.model_metrics.keys():
                self._update_model_metrics(model_id)

        return removed


def create_feedback_loop(faza16_registry=None) -> ReliabilityFeedbackLoop:
    """
    Create and return a reliability feedback loop.

    Args:
        faza16_registry: Optional FAZA 16 registry for integration

    Returns:
        Configured ReliabilityFeedbackLoop instance
    """
    loop = ReliabilityFeedbackLoop(faza16_registry)
    logger.info("Reliability Feedback Loop created")
    return loop
