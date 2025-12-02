"""
Explainability Engine for SENTI OS FAZA 17

This module provides transparent explanations for all orchestration decisions:
- Why specific models were chosen
- How steps were planned
- Ensemble reasoning
- Conflict resolution explanations
- Decision trails for audit

Ensures full transparency and compliance with EU AI Act requirements.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions to explain."""
    MODEL_SELECTION = "model_selection"
    STEP_PLANNING = "step_planning"
    ENSEMBLE_STRATEGY = "ensemble_strategy"
    PRIORITY_ASSIGNMENT = "priority_assignment"
    CONFLICT_RESOLUTION = "conflict_resolution"
    PIPELINE_ROUTING = "pipeline_routing"


@dataclass
class DecisionFactor:
    """A single factor in a decision."""
    factor_name: str
    factor_value: float
    weight: float
    description: str


@dataclass
class ExplanationEntry:
    """Explanation for a single decision."""
    decision_id: str
    decision_type: DecisionType
    summary: str
    factors: List[DecisionFactor] = field(default_factory=list)
    alternatives_considered: List[str] = field(default_factory=list)
    final_choice: str = ""
    confidence_in_decision: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


class ExplainabilityEngine:
    """
    Provides transparent explanations for orchestration decisions.

    This engine logs all decision-making processes and provides
    human-readable explanations for regulatory compliance and debugging.
    """

    def __init__(self):
        """Initialize the explainability engine."""
        self.explanation_log: List[ExplanationEntry] = []
        logger.info("Explainability Engine initialized")

    def explain_model_selection(
        self,
        decision_id: str,
        selected_model: str,
        candidates: List[str],
        selection_factors: Dict[str, float],
        routing_logic: str,
    ) -> ExplanationEntry:
        """
        Explain why a specific model was selected.

        Args:
            decision_id: Unique decision identifier
            selected_model: The model that was chosen
            candidates: All candidate models considered
            selection_factors: Factors that influenced selection
            routing_logic: Description of routing logic used

        Returns:
            ExplanationEntry with details
        """
        factors = [
            DecisionFactor(
                factor_name=name,
                factor_value=value,
                weight=1.0 / len(selection_factors),
                description=f"{name}: {value:.3f}",
            )
            for name, value in selection_factors.items()
        ]

        summary = (
            f"Selected '{selected_model}' from {len(candidates)} candidates. "
            f"Routing logic: {routing_logic}. "
            f"Key factors: {', '.join(f'{k}={v:.2f}' for k, v in list(selection_factors.items())[:3])}"
        )

        explanation = ExplanationEntry(
            decision_id=decision_id,
            decision_type=DecisionType.MODEL_SELECTION,
            summary=summary,
            factors=factors,
            alternatives_considered=candidates,
            final_choice=selected_model,
            confidence_in_decision=max(selection_factors.values()) if selection_factors else 0.5,
        )

        self.explanation_log.append(explanation)
        logger.debug(f"Model selection explained: {decision_id}")

        return explanation

    def explain_step_planning(
        self,
        decision_id: str,
        num_steps: int,
        execution_mode: str,
        estimated_cost: float,
        estimated_time: int,
        safety_checks_passed: bool,
    ) -> ExplanationEntry:
        """
        Explain how steps were planned.

        Args:
            decision_id: Unique decision identifier
            num_steps: Number of steps planned
            execution_mode: Execution mode (sequential/parallel)
            estimated_cost: Estimated total cost
            estimated_time: Estimated total time
            safety_checks_passed: Whether safety checks passed

        Returns:
            ExplanationEntry with details
        """
        factors = [
            DecisionFactor(
                factor_name="complexity",
                factor_value=num_steps / 10.0,
                weight=0.3,
                description=f"Task decomposed into {num_steps} steps",
            ),
            DecisionFactor(
                factor_name="cost",
                factor_value=min(estimated_cost, 1.0),
                weight=0.3,
                description=f"Estimated cost: ${estimated_cost:.2f}",
            ),
            DecisionFactor(
                factor_name="time",
                factor_value=min(estimated_time / 300.0, 1.0),
                weight=0.2,
                description=f"Estimated time: {estimated_time}s",
            ),
            DecisionFactor(
                factor_name="safety",
                factor_value=1.0 if safety_checks_passed else 0.0,
                weight=0.2,
                description=f"Safety: {'passed' if safety_checks_passed else 'FAILED'}",
            ),
        ]

        summary = (
            f"Planned {num_steps} steps in {execution_mode} mode. "
            f"Est. cost: ${estimated_cost:.2f}, Est. time: {estimated_time}s. "
            f"Safety checks: {'passed' if safety_checks_passed else 'FAILED'}."
        )

        explanation = ExplanationEntry(
            decision_id=decision_id,
            decision_type=DecisionType.STEP_PLANNING,
            summary=summary,
            factors=factors,
            final_choice=execution_mode,
            confidence_in_decision=0.9 if safety_checks_passed else 0.3,
        )

        self.explanation_log.append(explanation)
        logger.debug(f"Step planning explained: {decision_id}")

        return explanation

    def explain_ensemble_strategy(
        self,
        decision_id: str,
        strategy: str,
        num_models: int,
        conflicts_detected: int,
        final_confidence: float,
    ) -> ExplanationEntry:
        """
        Explain ensemble strategy selection.

        Args:
            decision_id: Unique decision identifier
            strategy: Strategy used
            num_models: Number of models combined
            conflicts_detected: Number of conflicts
            final_confidence: Final confidence score

        Returns:
            ExplanationEntry with details
        """
        factors = [
            DecisionFactor(
                factor_name="model_count",
                factor_value=min(num_models / 5.0, 1.0),
                weight=0.3,
                description=f"Combined {num_models} models",
            ),
            DecisionFactor(
                factor_name="conflicts",
                factor_value=max(0.0, 1.0 - conflicts_detected / max(num_models, 1)),
                weight=0.3,
                description=f"Conflicts: {conflicts_detected}",
            ),
            DecisionFactor(
                factor_name="confidence",
                factor_value=final_confidence,
                weight=0.4,
                description=f"Final confidence: {final_confidence:.3f}",
            ),
        ]

        summary = (
            f"Used '{strategy}' to combine {num_models} models. "
            f"Detected {conflicts_detected} conflicts. "
            f"Final confidence: {final_confidence:.3f}."
        )

        explanation = ExplanationEntry(
            decision_id=decision_id,
            decision_type=DecisionType.ENSEMBLE_STRATEGY,
            summary=summary,
            factors=factors,
            final_choice=strategy,
            confidence_in_decision=final_confidence,
        )

        self.explanation_log.append(explanation)
        logger.debug(f"Ensemble strategy explained: {decision_id}")

        return explanation

    def explain_priority_assignment(
        self,
        decision_id: str,
        task_id: str,
        assigned_priority: str,
        reasoning: str,
    ) -> ExplanationEntry:
        """
        Explain priority assignment.

        Args:
            decision_id: Unique decision identifier
            task_id: Task identifier
            assigned_priority: Priority assigned
            reasoning: Reasoning for assignment

        Returns:
            ExplanationEntry with details
        """
        priority_map = {"HIGH": 1.0, "NORMAL": 0.5, "LOW": 0.2}

        factors = [
            DecisionFactor(
                factor_name="priority_level",
                factor_value=priority_map.get(assigned_priority, 0.5),
                weight=1.0,
                description=reasoning,
            ),
        ]

        summary = f"Assigned {assigned_priority} priority to task {task_id}. Reason: {reasoning}"

        explanation = ExplanationEntry(
            decision_id=decision_id,
            decision_type=DecisionType.PRIORITY_ASSIGNMENT,
            summary=summary,
            factors=factors,
            final_choice=assigned_priority,
            confidence_in_decision=0.9,
            metadata={"task_id": task_id},
        )

        self.explanation_log.append(explanation)
        logger.debug(f"Priority assignment explained: {decision_id}")

        return explanation

    def explain_conflict_resolution(
        self,
        decision_id: str,
        conflicting_models: List[str],
        resolution_method: str,
        chosen_output: str,
    ) -> ExplanationEntry:
        """
        Explain how conflicts were resolved.

        Args:
            decision_id: Unique decision identifier
            conflicting_models: Models that had conflicts
            resolution_method: Method used to resolve
            chosen_output: Final output chosen

        Returns:
            ExplanationEntry with details
        """
        factors = [
            DecisionFactor(
                factor_name="conflict_count",
                factor_value=len(conflicting_models) / 5.0,
                weight=0.5,
                description=f"{len(conflicting_models)} models in conflict",
            ),
            DecisionFactor(
                factor_name="resolution_method",
                factor_value=0.8,
                weight=0.5,
                description=f"Used {resolution_method}",
            ),
        ]

        summary = (
            f"Resolved conflict between {len(conflicting_models)} models "
            f"using '{resolution_method}'. Selected output from {chosen_output}."
        )

        explanation = ExplanationEntry(
            decision_id=decision_id,
            decision_type=DecisionType.CONFLICT_RESOLUTION,
            summary=summary,
            factors=factors,
            alternatives_considered=conflicting_models,
            final_choice=chosen_output,
            confidence_in_decision=0.7,
        )

        self.explanation_log.append(explanation)
        logger.debug(f"Conflict resolution explained: {decision_id}")

        return explanation

    def get_explanation(self, decision_id: str) -> Optional[ExplanationEntry]:
        """
        Retrieve explanation by decision ID.

        Args:
            decision_id: Decision identifier

        Returns:
            ExplanationEntry if found, None otherwise
        """
        for entry in self.explanation_log:
            if entry.decision_id == decision_id:
                return entry

        return None

    def get_recent_explanations(self, limit: int = 10) -> List[ExplanationEntry]:
        """
        Get recent explanations.

        Args:
            limit: Maximum number to return

        Returns:
            List of recent ExplanationEntry instances
        """
        return self.explanation_log[-limit:]

    def get_explanations_by_type(
        self,
        decision_type: DecisionType,
    ) -> List[ExplanationEntry]:
        """
        Get all explanations of a specific type.

        Args:
            decision_type: Type of decisions to retrieve

        Returns:
            List of matching ExplanationEntry instances
        """
        return [
            entry for entry in self.explanation_log
            if entry.decision_type == decision_type
        ]

    def generate_audit_report(self) -> Dict:
        """
        Generate comprehensive audit report.

        Returns:
            Dictionary with audit information
        """
        total = len(self.explanation_log)

        if total == 0:
            return {
                "total_decisions": 0,
                "decisions_by_type": {},
                "average_confidence": 0.0,
            }

        decisions_by_type = {}
        for decision_type in DecisionType:
            count = sum(1 for e in self.explanation_log if e.decision_type == decision_type)
            decisions_by_type[decision_type.value] = count

        avg_confidence = sum(e.confidence_in_decision for e in self.explanation_log) / total

        return {
            "total_decisions": total,
            "decisions_by_type": decisions_by_type,
            "average_confidence": round(avg_confidence, 3),
            "oldest_decision": self.explanation_log[0].timestamp if self.explanation_log else None,
            "newest_decision": self.explanation_log[-1].timestamp if self.explanation_log else None,
        }

    def clear_old_explanations(self, keep_last_n: int = 1000) -> int:
        """
        Clear old explanations, keeping only recent ones.

        Args:
            keep_last_n: Number of explanations to keep

        Returns:
            Number of explanations removed
        """
        if len(self.explanation_log) <= keep_last_n:
            return 0

        removed = len(self.explanation_log) - keep_last_n
        self.explanation_log = self.explanation_log[-keep_last_n:]

        logger.info(f"Cleared {removed} old explanations")
        return removed


def create_explainability_engine() -> ExplainabilityEngine:
    """
    Create and return an explainability engine.

    Returns:
        Configured ExplainabilityEngine instance
    """
    engine = ExplainabilityEngine()
    logger.info("Explainability Engine created")
    return engine
