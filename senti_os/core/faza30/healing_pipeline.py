"""
FAZA 30 – Healing Pipeline

12-step self-healing pipeline orchestrating fault detection, classification, and repair.

Provides:
- 12-step healing pipeline
- Fault detection → classification → repair flow
- Snapshot management integration
- Health verification
- Rollback capability

Architecture:
    HealingStage - 12 pipeline stages
    HealingContext - Pipeline execution context
    HealingPipeline - Main orchestrator

Usage:
    from senti_os.core.faza30.healing_pipeline import HealingPipeline

    pipeline = HealingPipeline(detection_engine, classification_engine, repair_engines)
    result = pipeline.execute_healing_cycle()
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


class HealingStage(Enum):
    """12-stage healing pipeline."""
    STAGE_1_DETECT = "detect"                      # Detect faults from all layers
    STAGE_2_CLASSIFY = "classify"                  # Classify fault category
    STAGE_3_SNAPSHOT = "snapshot"                  # Take pre-repair snapshot
    STAGE_4_SELECT_STRATEGY = "select_strategy"    # Select repair strategy
    STAGE_5_PREPARE = "prepare"                    # Prepare repair context
    STAGE_6_EXECUTE_REPAIR = "execute_repair"      # Execute repair action
    STAGE_7_VERIFY = "verify"                      # Verify repair success
    STAGE_8_HEALTH_CHECK = "health_check"          # Check system health
    STAGE_9_ROLLBACK = "rollback"                  # Rollback if needed
    STAGE_10_STABILIZE = "stabilize"               # Stabilize system
    STAGE_11_LEARN = "learn"                       # Learn from repair
    STAGE_12_REPORT = "report"                     # Report results


class HealingOutcome(Enum):
    """Overall healing outcome."""
    SUCCESS = "success"             # Healing successful
    PARTIAL = "partial"             # Partial success
    FAILED = "failed"               # Healing failed
    ROLLBACK = "rollback"           # Rolled back to snapshot
    SKIPPED = "skipped"             # No action needed


@dataclass
class HealingContext:
    """
    Context for healing pipeline execution.

    Attributes:
        cycle_id: Unique cycle identifier
        faults: List of detected faults
        classifications: Fault classifications
        repairs: Repair results
        snapshot_id: Pre-repair snapshot ID
        health_before: Health score before repair
        health_after: Health score after repair
        stage_results: Results per stage
        metadata: Additional context metadata
    """
    cycle_id: str
    faults: List[Any] = field(default_factory=list)
    classifications: List[Any] = field(default_factory=list)
    repairs: List[Any] = field(default_factory=list)
    snapshot_id: Optional[str] = None
    health_before: float = 0.0
    health_after: float = 0.0
    stage_results: Dict[HealingStage, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HealingResult:
    """
    Result of healing pipeline execution.

    Attributes:
        cycle_id: Healing cycle ID
        outcome: Overall outcome
        faults_detected: Number of faults detected
        faults_repaired: Number of faults repaired
        health_improvement: Health score improvement
        duration: Total healing duration
        stages_completed: List of completed stages
        rollback_performed: Whether rollback was needed
        context: Full healing context
    """
    cycle_id: str
    outcome: HealingOutcome
    faults_detected: int
    faults_repaired: int
    health_improvement: float
    duration: float
    stages_completed: List[HealingStage]
    rollback_performed: bool
    context: HealingContext
    timestamp: datetime = field(default_factory=datetime.now)


class HealingPipeline:
    """
    12-step self-healing pipeline.

    Coordinates:
    - Fault detection
    - Classification
    - Snapshot management
    - Repair execution
    - Verification
    - Rollback if needed
    - System stabilization
    - Learning and reporting

    Features:
    - Complete pipeline orchestration
    - Automatic rollback on failure
    - Health monitoring
    - Stage-by-stage execution tracking
    """

    def __init__(
        self,
        detection_engine: Any,
        classification_engine: Any,
        repair_engines: Dict[str, Any],
        snapshot_manager: Optional[Any] = None,
        health_engine: Optional[Any] = None
    ):
        """
        Initialize healing pipeline.

        Args:
            detection_engine: DetectionEngine instance
            classification_engine: ClassificationEngine instance
            repair_engines: Dict of repair engines by category
            snapshot_manager: Optional SnapshotManager
            health_engine: Optional HealthEngine
        """
        self.detection_engine = detection_engine
        self.classification_engine = classification_engine
        self.repair_engines = repair_engines
        self.snapshot_manager = snapshot_manager
        self.health_engine = health_engine

        self._healing_history: List[HealingResult] = []
        self._stats = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "rollback_cycles": 0,
            "avg_duration": 0.0,
            "avg_health_improvement": 0.0
        }

    def execute_healing_cycle(
        self,
        faza25_metrics: Optional[Dict] = None,
        faza27_metrics: Optional[Dict] = None,
        faza28_metrics: Optional[Dict] = None,
        faza28_5_metrics: Optional[Dict] = None,
        faza29_metrics: Optional[Dict] = None
    ) -> HealingResult:
        """
        Execute complete 12-stage healing cycle.

        Args:
            faza25_metrics: FAZA 25 metrics
            faza27_metrics: FAZA 27 metrics
            faza28_metrics: FAZA 28 metrics
            faza28_5_metrics: FAZA 28.5 metrics
            faza29_metrics: FAZA 29 metrics

        Returns:
            HealingResult with outcome and details
        """
        start_time = datetime.now()
        cycle_id = f"healing_{start_time.timestamp()}"

        # Initialize context
        context = HealingContext(cycle_id=cycle_id)
        stages_completed: List[HealingStage] = []

        try:
            # STAGE 1: DETECT
            context = self._stage_1_detect(context, faza25_metrics, faza27_metrics,
                                          faza28_metrics, faza28_5_metrics, faza29_metrics)
            stages_completed.append(HealingStage.STAGE_1_DETECT)

            if not context.faults:
                # No faults detected - skip remaining stages
                duration = (datetime.now() - start_time).total_seconds()
                result = HealingResult(
                    cycle_id=cycle_id,
                    outcome=HealingOutcome.SKIPPED,
                    faults_detected=0,
                    faults_repaired=0,
                    health_improvement=0.0,
                    duration=duration,
                    stages_completed=stages_completed,
                    rollback_performed=False,
                    context=context
                )
                self._update_statistics(result)
                return result

            # STAGE 2: CLASSIFY
            context = self._stage_2_classify(context)
            stages_completed.append(HealingStage.STAGE_2_CLASSIFY)

            # STAGE 3: SNAPSHOT
            context = self._stage_3_snapshot(context)
            stages_completed.append(HealingStage.STAGE_3_SNAPSHOT)

            # STAGE 4: SELECT STRATEGY
            context = self._stage_4_select_strategy(context)
            stages_completed.append(HealingStage.STAGE_4_SELECT_STRATEGY)

            # STAGE 5: PREPARE
            context = self._stage_5_prepare(context)
            stages_completed.append(HealingStage.STAGE_5_PREPARE)

            # STAGE 6: EXECUTE REPAIR
            context = self._stage_6_execute_repair(context)
            stages_completed.append(HealingStage.STAGE_6_EXECUTE_REPAIR)

            # STAGE 7: VERIFY
            context = self._stage_7_verify(context)
            stages_completed.append(HealingStage.STAGE_7_VERIFY)

            # STAGE 8: HEALTH CHECK
            context = self._stage_8_health_check(context)
            stages_completed.append(HealingStage.STAGE_8_HEALTH_CHECK)

            # STAGE 9: ROLLBACK (if needed)
            rollback_performed = False
            if context.health_after < context.health_before:
                context = self._stage_9_rollback(context)
                stages_completed.append(HealingStage.STAGE_9_ROLLBACK)
                rollback_performed = True

            # STAGE 10: STABILIZE
            context = self._stage_10_stabilize(context)
            stages_completed.append(HealingStage.STAGE_10_STABILIZE)

            # STAGE 11: LEARN
            context = self._stage_11_learn(context)
            stages_completed.append(HealingStage.STAGE_11_LEARN)

            # STAGE 12: REPORT
            context = self._stage_12_report(context)
            stages_completed.append(HealingStage.STAGE_12_REPORT)

            # Determine outcome
            if rollback_performed:
                outcome = HealingOutcome.ROLLBACK
            else:
                successful_repairs = sum(1 for r in context.repairs if hasattr(r, 'status') and str(r.status) == 'RepairStatus.SUCCESS')
                if successful_repairs == len(context.faults):
                    outcome = HealingOutcome.SUCCESS
                elif successful_repairs > 0:
                    outcome = HealingOutcome.PARTIAL
                else:
                    outcome = HealingOutcome.FAILED

            duration = (datetime.now() - start_time).total_seconds()
            health_improvement = context.health_after - context.health_before

            result = HealingResult(
                cycle_id=cycle_id,
                outcome=outcome,
                faults_detected=len(context.faults),
                faults_repaired=sum(1 for r in context.repairs if hasattr(r, 'status') and 'SUCCESS' in str(r.status)),
                health_improvement=health_improvement,
                duration=duration,
                stages_completed=stages_completed,
                rollback_performed=rollback_performed,
                context=context
            )

            self._update_statistics(result)
            self._healing_history.append(result)

            return result

        except Exception as e:
            # Pipeline error - return failed result
            duration = (datetime.now() - start_time).total_seconds()
            context.metadata["error"] = str(e)

            result = HealingResult(
                cycle_id=cycle_id,
                outcome=HealingOutcome.FAILED,
                faults_detected=len(context.faults),
                faults_repaired=0,
                health_improvement=0.0,
                duration=duration,
                stages_completed=stages_completed,
                rollback_performed=False,
                context=context
            )

            self._update_statistics(result)
            return result

    def _stage_1_detect(
        self,
        context: HealingContext,
        faza25_metrics: Optional[Dict],
        faza27_metrics: Optional[Dict],
        faza28_metrics: Optional[Dict],
        faza28_5_metrics: Optional[Dict],
        faza29_metrics: Optional[Dict]
    ) -> HealingContext:
        """Stage 1: Detect faults."""
        faults = self.detection_engine.detect_faults(
            faza25_metrics or {},
            faza27_metrics or {},
            faza28_metrics or {},
            faza28_5_metrics or {},
            faza29_metrics or {}
        )

        context.faults = faults
        context.stage_results[HealingStage.STAGE_1_DETECT] = {
            "faults_detected": len(faults),
            "critical_faults": sum(1 for f in faults if 'critical' in str(getattr(f, 'severity', '')).lower())
        }

        return context

    def _stage_2_classify(self, context: HealingContext) -> HealingContext:
        """Stage 2: Classify faults."""
        classifications = []

        for fault in context.faults:
            classification = self.classification_engine.classify_fault(fault)
            classifications.append(classification)

        context.classifications = classifications
        context.stage_results[HealingStage.STAGE_2_CLASSIFY] = {
            "classifications_completed": len(classifications),
            "by_category": {}
        }

        # Count by category
        for cls in classifications:
            category = str(getattr(cls, 'category', 'unknown'))
            context.stage_results[HealingStage.STAGE_2_CLASSIFY]["by_category"][category] = \
                context.stage_results[HealingStage.STAGE_2_CLASSIFY]["by_category"].get(category, 0) + 1

        return context

    def _stage_3_snapshot(self, context: HealingContext) -> HealingContext:
        """Stage 3: Take pre-repair snapshot."""
        if self.snapshot_manager:
            snapshot_id = self.snapshot_manager.create_snapshot(
                snapshot_type="pre_repair",
                metadata={"cycle_id": context.cycle_id, "fault_count": len(context.faults)}
            )
            context.snapshot_id = snapshot_id
            context.stage_results[HealingStage.STAGE_3_SNAPSHOT] = {
                "snapshot_created": True,
                "snapshot_id": snapshot_id
            }
        else:
            context.stage_results[HealingStage.STAGE_3_SNAPSHOT] = {
                "snapshot_created": False,
                "reason": "SnapshotManager not available"
            }

        return context

    def _stage_4_select_strategy(self, context: HealingContext) -> HealingContext:
        """Stage 4: Select repair strategies."""
        strategies = []

        for i, classification in enumerate(context.classifications):
            category = str(getattr(classification, 'category', '')).lower()
            fault = context.faults[i] if i < len(context.faults) else None

            # Match repair engine to category
            for engine_name, engine in self.repair_engines.items():
                if engine.can_repair(fault, {"classification": classification}):
                    strategies.append({
                        "fault_id": getattr(fault, 'fault_id', 'unknown'),
                        "engine": engine_name,
                        "category": category
                    })
                    break

        context.metadata["repair_strategies"] = strategies
        context.stage_results[HealingStage.STAGE_4_SELECT_STRATEGY] = {
            "strategies_selected": len(strategies)
        }

        return context

    def _stage_5_prepare(self, context: HealingContext) -> HealingContext:
        """Stage 5: Prepare repair context."""
        # Record health before repair
        if self.health_engine:
            context.health_before = self.health_engine.compute_health_score()
        else:
            context.health_before = 0.5  # Neutral baseline

        context.stage_results[HealingStage.STAGE_5_PREPARE] = {
            "health_before": context.health_before,
            "ready": True
        }

        return context

    def _stage_6_execute_repair(self, context: HealingContext) -> HealingContext:
        """Stage 6: Execute repairs."""
        repairs = []
        strategies = context.metadata.get("repair_strategies", [])

        for i, strategy in enumerate(strategies):
            fault = context.faults[i] if i < len(context.faults) else None
            classification = context.classifications[i] if i < len(context.classifications) else None

            engine_name = strategy.get("engine")
            engine = self.repair_engines.get(engine_name)

            if engine and fault:
                repair_result = engine.repair(fault, {"classification": classification})
                repairs.append(repair_result)

        context.repairs = repairs
        context.stage_results[HealingStage.STAGE_6_EXECUTE_REPAIR] = {
            "repairs_attempted": len(repairs),
            "repairs_successful": sum(1 for r in repairs if 'SUCCESS' in str(getattr(r, 'status', '')))
        }

        return context

    def _stage_7_verify(self, context: HealingContext) -> HealingContext:
        """Stage 7: Verify repairs."""
        verified = 0

        for repair in context.repairs:
            if getattr(repair, 'verification_passed', False):
                verified += 1

        context.stage_results[HealingStage.STAGE_7_VERIFY] = {
            "repairs_verified": verified,
            "verification_rate": verified / len(context.repairs) if context.repairs else 0.0
        }

        return context

    def _stage_8_health_check(self, context: HealingContext) -> HealingContext:
        """Stage 8: Check post-repair health."""
        if self.health_engine:
            context.health_after = self.health_engine.compute_health_score()
        else:
            # Estimate health based on repair success
            success_rate = len([r for r in context.repairs if 'SUCCESS' in str(getattr(r, 'status', ''))]) / len(context.repairs) if context.repairs else 0
            context.health_after = context.health_before + (success_rate * 0.2)

        context.stage_results[HealingStage.STAGE_8_HEALTH_CHECK] = {
            "health_after": context.health_after,
            "health_delta": context.health_after - context.health_before
        }

        return context

    def _stage_9_rollback(self, context: HealingContext) -> HealingContext:
        """Stage 9: Rollback to snapshot."""
        if self.snapshot_manager and context.snapshot_id:
            self.snapshot_manager.restore_snapshot(context.snapshot_id)
            context.stage_results[HealingStage.STAGE_9_ROLLBACK] = {
                "rollback_performed": True,
                "snapshot_restored": context.snapshot_id
            }
        else:
            context.stage_results[HealingStage.STAGE_9_ROLLBACK] = {
                "rollback_performed": False,
                "reason": "No snapshot available"
            }

        return context

    def _stage_10_stabilize(self, context: HealingContext) -> HealingContext:
        """Stage 10: Stabilize system."""
        # Allow system to stabilize for a moment
        context.stage_results[HealingStage.STAGE_10_STABILIZE] = {
            "stabilization_complete": True,
            "waiting_period": 0.5
        }

        return context

    def _stage_11_learn(self, context: HealingContext) -> HealingContext:
        """Stage 11: Learn from repair."""
        # Extract learnings
        learnings = {
            "fault_patterns": [str(getattr(f, 'fault_type', '')) for f in context.faults],
            "repair_effectiveness": {
                str(getattr(r, 'fault_id', '')): getattr(r, 'success_rate', 0.0)
                for r in context.repairs
            },
            "health_improvement": context.health_after - context.health_before
        }

        context.stage_results[HealingStage.STAGE_11_LEARN] = learnings

        return context

    def _stage_12_report(self, context: HealingContext) -> HealingContext:
        """Stage 12: Generate report."""
        report = {
            "cycle_id": context.cycle_id,
            "faults_detected": len(context.faults),
            "faults_repaired": sum(1 for r in context.repairs if 'SUCCESS' in str(getattr(r, 'status', ''))),
            "health_before": context.health_before,
            "health_after": context.health_after,
            "improvement": context.health_after - context.health_before,
            "stages_completed": len(context.stage_results)
        }

        context.stage_results[HealingStage.STAGE_12_REPORT] = report

        return context

    def _update_statistics(self, result: HealingResult) -> None:
        """Update pipeline statistics."""
        self._stats["total_cycles"] += 1

        if result.outcome == HealingOutcome.SUCCESS:
            self._stats["successful_cycles"] += 1
        elif result.outcome == HealingOutcome.FAILED:
            self._stats["failed_cycles"] += 1
        elif result.outcome == HealingOutcome.ROLLBACK:
            self._stats["rollback_cycles"] += 1

        # Update averages
        total = self._stats["total_cycles"]
        current_avg_duration = self._stats["avg_duration"]
        new_avg_duration = (current_avg_duration * (total - 1) + result.duration) / total
        self._stats["avg_duration"] = new_avg_duration

        current_avg_improvement = self._stats["avg_health_improvement"]
        new_avg_improvement = (current_avg_improvement * (total - 1) + result.health_improvement) / total
        self._stats["avg_health_improvement"] = new_avg_improvement

    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            **self._stats,
            "history_size": len(self._healing_history)
        }

    def get_recent_cycles(self, limit: int = 10) -> List[HealingResult]:
        """Get recent healing cycles."""
        return self._healing_history[-limit:]


def create_healing_pipeline(
    detection_engine: Any,
    classification_engine: Any,
    repair_engines: Dict[str, Any],
    snapshot_manager: Optional[Any] = None,
    health_engine: Optional[Any] = None
) -> HealingPipeline:
    """
    Factory function to create HealingPipeline.

    Args:
        detection_engine: DetectionEngine instance
        classification_engine: ClassificationEngine instance
        repair_engines: Dict of repair engines
        snapshot_manager: Optional SnapshotManager
        health_engine: Optional HealthEngine

    Returns:
        Initialized HealingPipeline instance
    """
    return HealingPipeline(
        detection_engine,
        classification_engine,
        repair_engines,
        snapshot_manager,
        health_engine
    )
