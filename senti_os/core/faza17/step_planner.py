"""
Step Planner for SENTI OS FAZA 17

This module decomposes complex tasks into discrete steps:
- Task decomposition into sequential or parallel steps
- Step validation and safety checks
- Control flow graph creation
- Dependency analysis
- Safety boundary enforcement

All planning respects SENTI OS privacy and safety principles.
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StepType(Enum):
    """Types of execution steps."""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    DECISION = "decision"


class ExecutionMode(Enum):
    """Execution modes for steps."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class Step:
    """Represents a single execution step."""
    step_id: str
    step_type: StepType
    description: str
    dependencies: List[str] = field(default_factory=list)
    requires_external_access: bool = False
    estimated_complexity: float = 0.5
    max_cost: float = 1.0
    timeout_seconds: int = 60
    metadata: Dict = field(default_factory=dict)
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class PlanningResult:
    """Result of planning operation."""
    steps: List[Step]
    execution_mode: ExecutionMode
    total_estimated_cost: float
    total_estimated_time: int
    safety_checks_passed: bool
    warnings: List[str] = field(default_factory=list)
    control_flow_graph: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class StepPlanner:
    """
    Plans and decomposes complex tasks into executable steps.

    This planner ensures all steps are safe, valid, and properly sequenced
    according to dependencies and safety requirements.
    """

    MAX_STEPS_PER_TASK = 20
    MAX_COMPLEXITY_PER_STEP = 0.9

    def __init__(self):
        """Initialize the step planner."""
        self.planning_history: List[PlanningResult] = []
        logger.info("Step Planner initialized")

    def plan_task(
        self,
        task_description: str,
        context: Optional[Dict] = None,
        allow_parallel: bool = True,
        max_steps: int = 10,
    ) -> PlanningResult:
        """
        Plan a task by breaking it into steps.

        Args:
            task_description: Description of the task
            context: Optional context for planning
            allow_parallel: Whether to allow parallel execution
            max_steps: Maximum number of steps

        Returns:
            PlanningResult with planned steps
        """
        context = context or {}

        steps = self._decompose_task(task_description, context, max_steps)

        if not steps:
            return PlanningResult(
                steps=[],
                execution_mode=ExecutionMode.SEQUENTIAL,
                total_estimated_cost=0.0,
                total_estimated_time=0,
                safety_checks_passed=False,
                warnings=["Task decomposition failed - no steps generated"],
            )

        validated_steps = self._validate_steps(steps)

        execution_mode = self._determine_execution_mode(
            validated_steps,
            allow_parallel,
        )

        control_flow_graph = self._build_control_flow_graph(validated_steps)

        safety_passed, warnings = self._perform_safety_checks(
            validated_steps,
            context,
        )

        total_cost = sum(step.max_cost for step in validated_steps)
        total_time = self._estimate_total_time(validated_steps, execution_mode)

        result = PlanningResult(
            steps=validated_steps,
            execution_mode=execution_mode,
            total_estimated_cost=total_cost,
            total_estimated_time=total_time,
            safety_checks_passed=safety_passed,
            warnings=warnings,
            control_flow_graph=control_flow_graph,
        )

        self.planning_history.append(result)

        logger.info(f"Task planned: {len(validated_steps)} steps, mode: {execution_mode.value}")

        return result

    def _decompose_task(
        self,
        task_description: str,
        context: Dict,
        max_steps: int,
    ) -> List[Step]:
        """
        Decompose task into individual steps.

        Args:
            task_description: Description of task
            context: Context for decomposition
            max_steps: Maximum steps allowed

        Returns:
            List of Step instances
        """
        task_lower = task_description.lower()

        steps = []

        if "analyze" in task_lower or "analysis" in task_lower:
            steps.append(Step(
                step_id="step_001",
                step_type=StepType.ANALYSIS,
                description="Perform initial analysis of input data",
                estimated_complexity=0.6,
                max_cost=0.3,
            ))

        if "generate" in task_lower or "create" in task_lower:
            steps.append(Step(
                step_id=f"step_{len(steps)+1:03d}",
                step_type=StepType.GENERATION,
                description="Generate output based on analysis",
                dependencies=[steps[-1].step_id] if steps else [],
                estimated_complexity=0.7,
                max_cost=0.5,
            ))

        if "validate" in task_lower or "verify" in task_lower or "check" in task_lower:
            steps.append(Step(
                step_id=f"step_{len(steps)+1:03d}",
                step_type=StepType.VALIDATION,
                description="Validate generated output",
                dependencies=[steps[-1].step_id] if steps else [],
                estimated_complexity=0.4,
                max_cost=0.2,
            ))

        if "transform" in task_lower or "convert" in task_lower:
            steps.append(Step(
                step_id=f"step_{len(steps)+1:03d}",
                step_type=StepType.TRANSFORMATION,
                description="Transform data to required format",
                estimated_complexity=0.5,
                max_cost=0.3,
            ))

        if "combine" in task_lower or "merge" in task_lower or "aggregate" in task_lower:
            steps.append(Step(
                step_id=f"step_{len(steps)+1:03d}",
                step_type=StepType.AGGREGATION,
                description="Aggregate results from multiple sources",
                dependencies=[s.step_id for s in steps] if steps else [],
                estimated_complexity=0.6,
                max_cost=0.4,
            ))

        if not steps:
            steps.append(Step(
                step_id="step_001",
                step_type=StepType.ANALYSIS,
                description=f"Process: {task_description[:50]}",
                estimated_complexity=0.5,
                max_cost=0.5,
            ))

        steps = steps[:min(len(steps), max_steps, self.MAX_STEPS_PER_TASK)]

        return steps

    def _validate_steps(self, steps: List[Step]) -> List[Step]:
        """
        Validate and sanitize steps.

        Args:
            steps: List of steps to validate

        Returns:
            Validated list of steps
        """
        validated = []

        for step in steps:
            if step.estimated_complexity > self.MAX_COMPLEXITY_PER_STEP:
                logger.warning(f"Step {step.step_id} complexity too high, capping")
                step.estimated_complexity = self.MAX_COMPLEXITY_PER_STEP

            invalid_deps = [
                dep for dep in step.dependencies
                if dep not in [s.step_id for s in validated]
            ]
            if invalid_deps:
                logger.warning(f"Step {step.step_id} has invalid dependencies, removing")
                step.dependencies = [
                    dep for dep in step.dependencies if dep not in invalid_deps
                ]

            validated.append(step)

        return validated

    def _determine_execution_mode(
        self,
        steps: List[Step],
        allow_parallel: bool,
    ) -> ExecutionMode:
        """
        Determine optimal execution mode.

        Args:
            steps: List of validated steps
            allow_parallel: Whether parallel execution is allowed

        Returns:
            ExecutionMode
        """
        if not allow_parallel:
            return ExecutionMode.SEQUENTIAL

        has_dependencies = any(step.dependencies for step in steps)

        if not has_dependencies and len(steps) > 1:
            return ExecutionMode.PARALLEL

        return ExecutionMode.SEQUENTIAL

    def _build_control_flow_graph(self, steps: List[Step]) -> Dict:
        """
        Build control flow graph from steps.

        Args:
            steps: List of steps

        Returns:
            Dictionary representing control flow
        """
        graph = {
            "nodes": [
                {
                    "id": step.step_id,
                    "type": step.step_type.value,
                    "description": step.description,
                }
                for step in steps
            ],
            "edges": [],
        }

        for step in steps:
            for dep in step.dependencies:
                graph["edges"].append({
                    "from": dep,
                    "to": step.step_id,
                    "type": "dependency",
                })

        return graph

    def _perform_safety_checks(
        self,
        steps: List[Step],
        context: Dict,
    ) -> tuple[bool, List[str]]:
        """
        Perform safety checks on planned steps.

        Args:
            steps: List of steps to check
            context: Context for checks

        Returns:
            Tuple of (passed, warnings)
        """
        warnings = []
        passed = True

        if len(steps) > self.MAX_STEPS_PER_TASK:
            warnings.append(f"Number of steps ({len(steps)}) exceeds maximum ({self.MAX_STEPS_PER_TASK})")
            passed = False

        total_cost = sum(step.max_cost for step in steps)
        if total_cost > context.get("max_total_cost", 10.0):
            warnings.append(f"Total estimated cost ({total_cost:.2f}) exceeds limit")
            passed = False

        requires_external = [s for s in steps if s.requires_external_access]
        has_consent = context.get("user_consent", False)

        if requires_external and not has_consent:
            warnings.append(f"{len(requires_external)} steps require external access but no consent")
            passed = False

        has_circular = self._detect_circular_dependencies(steps)
        if has_circular:
            warnings.append("Circular dependencies detected in step plan")
            passed = False

        return passed, warnings

    def _detect_circular_dependencies(self, steps: List[Step]) -> bool:
        """
        Detect circular dependencies in steps.

        Args:
            steps: List of steps to check

        Returns:
            True if circular dependencies exist
        """
        step_map = {step.step_id: step for step in steps}

        visited = set()
        path = set()

        def has_cycle(step_id: str) -> bool:
            if step_id in path:
                return True
            if step_id in visited:
                return False

            visited.add(step_id)
            path.add(step_id)

            step = step_map.get(step_id)
            if step:
                for dep in step.dependencies:
                    if has_cycle(dep):
                        return True

            path.remove(step_id)
            return False

        for step in steps:
            if has_cycle(step.step_id):
                return True

        return False

    def _estimate_total_time(
        self,
        steps: List[Step],
        execution_mode: ExecutionMode,
    ) -> int:
        """
        Estimate total execution time.

        Args:
            steps: List of steps
            execution_mode: Execution mode

        Returns:
            Estimated time in seconds
        """
        if execution_mode == ExecutionMode.PARALLEL:
            return max(step.timeout_seconds for step in steps) if steps else 0

        return sum(step.timeout_seconds for step in steps)

    def get_statistics(self) -> Dict:
        """
        Get planning statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.planning_history:
            return {
                "total_plans": 0,
                "average_steps": 0,
                "parallel_plans": 0,
                "sequential_plans": 0,
            }

        total = len(self.planning_history)
        avg_steps = sum(len(p.steps) for p in self.planning_history) / total
        parallel = sum(1 for p in self.planning_history if p.execution_mode == ExecutionMode.PARALLEL)

        return {
            "total_plans": total,
            "average_steps": round(avg_steps, 1),
            "parallel_plans": parallel,
            "sequential_plans": total - parallel,
        }


def create_planner() -> StepPlanner:
    """
    Create and return a step planner.

    Returns:
        Configured StepPlanner instance
    """
    planner = StepPlanner()
    logger.info("Step Planner created")
    return planner
