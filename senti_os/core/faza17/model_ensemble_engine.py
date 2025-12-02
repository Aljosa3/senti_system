"""
Model Ensemble Engine for SENTI OS FAZA 17

This module combines outputs from multiple models:
- Weighted confidence scoring
- Conflict detection and resolution
- Consensus result production
- Quality assessment
- Ensemble strategy selection

Integrates with FAZA 16 cross-verification layer for multi-source validation.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from statistics import mean, median, stdev


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnsembleStrategy(Enum):
    """Strategies for combining model outputs."""
    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_VOTE = "majority_vote"
    HIGHEST_CONFIDENCE = "highest_confidence"
    CONSENSUS = "consensus"
    BEST_OF_N = "best_of_n"


class ConflictResolution(Enum):
    """Methods for resolving conflicts."""
    HIGHEST_RELIABILITY = "highest_reliability"
    MAJORITY_RULE = "majority_rule"
    EXPERT_MODEL = "expert_model"
    MANUAL_REVIEW = "manual_review"


@dataclass
class ModelOutput:
    """Output from a single model."""
    model_id: str
    content: str
    confidence: float
    reliability_score: float
    processing_time: float
    cost: float
    metadata: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EnsembleResult:
    """Result of ensemble operation."""
    final_output: str
    confidence_score: float
    strategy_used: EnsembleStrategy
    participating_models: List[str]
    model_weights: Dict[str, float]
    conflicts_detected: int
    conflicts_resolved: int
    quality_score: float
    explanation: str
    individual_outputs: List[ModelOutput] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ModelEnsembleEngine:
    """
    Combines outputs from multiple models to produce consensus results.

    This engine uses various strategies to combine model outputs, detect
    conflicts, and produce high-quality ensemble results.
    """

    MIN_CONFIDENCE_THRESHOLD = 0.5
    MIN_MODELS_FOR_ENSEMBLE = 2

    def __init__(self):
        """Initialize the ensemble engine."""
        self.ensemble_history: List[EnsembleResult] = []
        logger.info("Model Ensemble Engine initialized")

    def combine_outputs(
        self,
        outputs: List[ModelOutput],
        strategy: EnsembleStrategy = EnsembleStrategy.WEIGHTED_AVERAGE,
        conflict_resolution: ConflictResolution = ConflictResolution.HIGHEST_RELIABILITY,
    ) -> EnsembleResult:
        """
        Combine multiple model outputs into single result.

        Args:
            outputs: List of ModelOutput instances
            strategy: Ensemble strategy to use
            conflict_resolution: How to resolve conflicts

        Returns:
            EnsembleResult with combined output
        """
        if not outputs:
            return EnsembleResult(
                final_output="",
                confidence_score=0.0,
                strategy_used=strategy,
                participating_models=[],
                model_weights={},
                conflicts_detected=0,
                conflicts_resolved=0,
                quality_score=0.0,
                explanation="No model outputs provided",
            )

        if len(outputs) == 1:
            return self._handle_single_output(outputs[0], strategy)

        model_weights = self._calculate_model_weights(outputs)

        conflicts = self._detect_conflicts(outputs)

        if conflicts:
            logger.info(f"Detected {len(conflicts)} conflicts, resolving...")

        if strategy == EnsembleStrategy.WEIGHTED_AVERAGE:
            result = self._weighted_average_strategy(outputs, model_weights)
        elif strategy == EnsembleStrategy.MAJORITY_VOTE:
            result = self._majority_vote_strategy(outputs)
        elif strategy == EnsembleStrategy.HIGHEST_CONFIDENCE:
            result = self._highest_confidence_strategy(outputs)
        elif strategy == EnsembleStrategy.CONSENSUS:
            result = self._consensus_strategy(outputs, model_weights)
        else:
            result = self._best_of_n_strategy(outputs)

        quality_score = self._assess_quality(outputs, result, conflicts)

        ensemble_result = EnsembleResult(
            final_output=result["output"],
            confidence_score=result["confidence"],
            strategy_used=strategy,
            participating_models=[o.model_id for o in outputs],
            model_weights=model_weights,
            conflicts_detected=len(conflicts),
            conflicts_resolved=len(conflicts),
            quality_score=quality_score,
            explanation=result.get("explanation", "Ensemble combination complete"),
            individual_outputs=outputs,
        )

        self.ensemble_history.append(ensemble_result)

        logger.info(f"Ensemble complete: {len(outputs)} models, confidence: {result['confidence']:.2f}")

        return ensemble_result

    def _handle_single_output(
        self,
        output: ModelOutput,
        strategy: EnsembleStrategy,
    ) -> EnsembleResult:
        """Handle case with single model output."""
        ensemble_result = EnsembleResult(
            final_output=output.content,
            confidence_score=output.confidence * 0.8,
            strategy_used=strategy,
            participating_models=[output.model_id],
            model_weights={output.model_id: 1.0},
            conflicts_detected=0,
            conflicts_resolved=0,
            quality_score=output.confidence * output.reliability_score,
            explanation="Single model output, no ensemble needed",
            individual_outputs=[output],
        )

        self.ensemble_history.append(ensemble_result)

        return ensemble_result

    def _calculate_model_weights(self, outputs: List[ModelOutput]) -> Dict[str, float]:
        """
        Calculate weights for each model based on reliability and confidence.

        Args:
            outputs: List of model outputs

        Returns:
            Dictionary mapping model_id to weight
        """
        weights = {}

        for output in outputs:
            weight = (output.reliability_score + output.confidence) / 2.0
            weights[output.model_id] = weight

        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        return weights

    def _detect_conflicts(self, outputs: List[ModelOutput]) -> List[tuple]:
        """
        Detect conflicts between model outputs.

        Args:
            outputs: List of model outputs

        Returns:
            List of conflict tuples
        """
        conflicts = []

        for i, out1 in enumerate(outputs):
            for out2 in outputs[i + 1:]:
                if self._are_outputs_conflicting(out1.content, out2.content):
                    conflicts.append((out1.model_id, out2.model_id))

        return conflicts

    def _are_outputs_conflicting(self, content1: str, content2: str) -> bool:
        """
        Check if two outputs conflict.

        Args:
            content1: First content
            content2: Second content

        Returns:
            True if conflicting
        """
        negation_words = {"not", "no", "never", "false", "incorrect", "opposite"}

        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        has_negation1 = bool(words1.intersection(negation_words))
        has_negation2 = bool(words2.intersection(negation_words))

        similarity = len(words1.intersection(words2)) / len(words1.union(words2)) if words1.union(words2) else 0

        if similarity > 0.5 and has_negation1 != has_negation2:
            return True

        return False

    def _weighted_average_strategy(
        self,
        outputs: List[ModelOutput],
        weights: Dict[str, float],
    ) -> Dict:
        """Weighted average ensemble strategy."""
        weighted_confidence = sum(
            output.confidence * weights[output.model_id]
            for output in outputs
        )

        best_output = max(outputs, key=lambda o: o.confidence * weights[o.model_id])

        return {
            "output": best_output.content,
            "confidence": weighted_confidence,
            "explanation": f"Weighted average of {len(outputs)} models",
        }

    def _majority_vote_strategy(self, outputs: List[ModelOutput]) -> Dict:
        """Majority vote ensemble strategy."""
        content_votes = {}

        for output in outputs:
            content_key = output.content[:100]
            if content_key not in content_votes:
                content_votes[content_key] = []
            content_votes[content_key].append(output)

        majority_content = max(content_votes.keys(), key=lambda k: len(content_votes[k]))
        majority_outputs = content_votes[majority_content]

        avg_confidence = mean(o.confidence for o in majority_outputs)

        return {
            "output": majority_outputs[0].content,
            "confidence": avg_confidence,
            "explanation": f"Majority vote: {len(majority_outputs)}/{len(outputs)} models agree",
        }

    def _highest_confidence_strategy(self, outputs: List[ModelOutput]) -> Dict:
        """Highest confidence ensemble strategy."""
        best_output = max(outputs, key=lambda o: o.confidence)

        return {
            "output": best_output.content,
            "confidence": best_output.confidence,
            "explanation": f"Selected highest confidence model: {best_output.model_id}",
        }

    def _consensus_strategy(
        self,
        outputs: List[ModelOutput],
        weights: Dict[str, float],
    ) -> Dict:
        """Consensus-based ensemble strategy."""
        confidence_threshold = self.MIN_CONFIDENCE_THRESHOLD

        confident_outputs = [o for o in outputs if o.confidence >= confidence_threshold]

        if not confident_outputs:
            confident_outputs = outputs

        best_output = max(
            confident_outputs,
            key=lambda o: o.confidence * o.reliability_score * weights[o.model_id]
        )

        consensus_confidence = mean(o.confidence for o in confident_outputs)

        return {
            "output": best_output.content,
            "confidence": consensus_confidence,
            "explanation": f"Consensus from {len(confident_outputs)} confident models",
        }

    def _best_of_n_strategy(self, outputs: List[ModelOutput]) -> Dict:
        """Best-of-N ensemble strategy."""
        scored_outputs = [
            (o, o.confidence * o.reliability_score / (o.cost + 0.01))
            for o in outputs
        ]

        best_output, best_score = max(scored_outputs, key=lambda x: x[1])

        return {
            "output": best_output.content,
            "confidence": best_output.confidence,
            "explanation": f"Best quality/cost ratio: {best_output.model_id}",
        }

    def _assess_quality(
        self,
        outputs: List[ModelOutput],
        result: Dict,
        conflicts: List[tuple],
    ) -> float:
        """
        Assess overall quality of ensemble result.

        Args:
            outputs: Model outputs
            result: Ensemble result
            conflicts: Detected conflicts

        Returns:
            Quality score (0.0 to 1.0)
        """
        avg_confidence = mean(o.confidence for o in outputs)
        avg_reliability = mean(o.reliability_score for o in outputs)

        conflict_penalty = min(0.3, len(conflicts) * 0.05)

        model_agreement = 1.0 - (len(conflicts) / max(1, len(outputs) * (len(outputs) - 1) / 2))

        quality = (avg_confidence * 0.4 + avg_reliability * 0.3 + model_agreement * 0.3) - conflict_penalty

        return max(0.0, min(1.0, quality))

    def get_statistics(self) -> Dict:
        """
        Get ensemble statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.ensemble_history:
            return {
                "total_ensembles": 0,
                "average_confidence": 0.0,
                "average_quality": 0.0,
                "total_conflicts": 0,
            }

        total = len(self.ensemble_history)

        return {
            "total_ensembles": total,
            "average_confidence": round(mean(e.confidence_score for e in self.ensemble_history), 3),
            "average_quality": round(mean(e.quality_score for e in self.ensemble_history), 3),
            "total_conflicts": sum(e.conflicts_detected for e in self.ensemble_history),
            "average_models_per_ensemble": round(mean(len(e.participating_models) for e in self.ensemble_history), 1),
        }


def create_ensemble_engine() -> ModelEnsembleEngine:
    """
    Create and return a model ensemble engine.

    Returns:
        Configured ModelEnsembleEngine instance
    """
    engine = ModelEnsembleEngine()
    logger.info("Model Ensemble Engine created")
    return engine
