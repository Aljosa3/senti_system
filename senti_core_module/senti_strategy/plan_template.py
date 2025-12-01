"""
FAZA 15 - Plan Templates
Defines plan structures for strategic planning

Provides templates for high-level, mid-level, and atomic action plans.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class ActionPriority(Enum):
    """Priority levels for actions."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ActionStatus(Enum):
    """Status of action execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AtomicAction:
    """
    Represents a single atomic action that can be executed.
    """

    def __init__(
        self,
        action_id: str,
        name: str,
        description: str,
        action_type: str,
        parameters: Dict[str, Any],
        priority: ActionPriority = ActionPriority.MEDIUM,
        estimated_duration: int = 0,
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize an atomic action.

        Args:
            action_id: Unique action identifier
            name: Action name
            description: Action description
            action_type: Type of action (e.g., "system", "data", "compute")
            parameters: Action parameters
            priority: Action priority
            estimated_duration: Estimated duration in seconds
            dependencies: List of action IDs this action depends on
        """
        self.action_id = action_id
        self.name = name
        self.description = description
        self.action_type = action_type
        self.parameters = parameters
        self.priority = priority
        self.estimated_duration = estimated_duration
        self.dependencies = dependencies or []
        self.status = ActionStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.result = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action_id": self.action_id,
            "name": self.name,
            "description": self.description,
            "action_type": self.action_type,
            "parameters": self.parameters,
            "priority": self.priority.name,
            "estimated_duration": self.estimated_duration,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "created_at": self.created_at,
            "result": self.result
        }


class MidLevelStep:
    """
    Represents a mid-level step composed of atomic actions.
    """

    def __init__(
        self,
        step_id: str,
        name: str,
        description: str,
        actions: List[AtomicAction],
        success_criteria: Dict[str, Any]
    ):
        """
        Initialize a mid-level step.

        Args:
            step_id: Unique step identifier
            name: Step name
            description: Step description
            actions: List of atomic actions
            success_criteria: Criteria for step success
        """
        self.step_id = step_id
        self.name = name
        self.description = description
        self.actions = actions
        self.success_criteria = success_criteria
        self.status = ActionStatus.PENDING
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "actions": [action.to_dict() for action in self.actions],
            "success_criteria": self.success_criteria,
            "status": self.status.value,
            "created_at": self.created_at
        }


class HighLevelPlan:
    """
    Represents a high-level strategic plan.
    """

    def __init__(
        self,
        plan_id: str,
        objective: str,
        description: str,
        steps: List[MidLevelStep],
        risk_score: int,
        expected_outcome: str,
        constraints: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a high-level plan.

        Args:
            plan_id: Unique plan identifier
            objective: High-level objective
            description: Plan description
            steps: List of mid-level steps
            risk_score: Overall risk score (0-100)
            expected_outcome: Expected outcome description
            constraints: Optional constraints
            metadata: Optional metadata
        """
        self.plan_id = plan_id
        self.objective = objective
        self.description = description
        self.steps = steps
        self.risk_score = risk_score
        self.expected_outcome = expected_outcome
        self.constraints = constraints or {}
        self.metadata = metadata or {}
        self.status = ActionStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.optimized_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "plan_id": self.plan_id,
            "objective": self.objective,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "risk_score": self.risk_score,
            "expected_outcome": self.expected_outcome,
            "constraints": self.constraints,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at,
            "optimized_count": self.optimized_count
        }

    def get_total_actions(self) -> int:
        """Get total number of atomic actions in plan."""
        return sum(len(step.actions) for step in self.steps)

    def get_total_steps(self) -> int:
        """Get total number of steps in plan."""
        return len(self.steps)


class StrategyTemplate:
    """
    Defines common strategy templates.
    """

    @staticmethod
    def create_empty_plan(plan_id: str, objective: str) -> HighLevelPlan:
        """
        Create an empty plan template.

        Args:
            plan_id: Plan identifier
            objective: High-level objective

        Returns:
            Empty HighLevelPlan
        """
        return HighLevelPlan(
            plan_id=plan_id,
            objective=objective,
            description="",
            steps=[],
            risk_score=0,
            expected_outcome=""
        )

    @staticmethod
    def create_optimization_plan(target_component: str, objective: str) -> HighLevelPlan:
        """
        Create a plan for system optimization.

        Args:
            target_component: Component to optimize
            objective: Optimization objective

        Returns:
            HighLevelPlan for optimization
        """
        plan_id = f"opt_{target_component}_{datetime.now().timestamp()}"

        # Analysis step
        analysis_actions = [
            AtomicAction(
                action_id=f"{plan_id}_analyze",
                name="Analyze Component",
                description=f"Analyze {target_component} performance",
                action_type="analysis",
                parameters={"component": target_component},
                priority=ActionPriority.HIGH
            )
        ]

        analysis_step = MidLevelStep(
            step_id=f"{plan_id}_step_analysis",
            name="Analysis Phase",
            description=f"Analyze {target_component} current state",
            actions=analysis_actions,
            success_criteria={"data_collected": True}
        )

        # Optimization step
        optimize_actions = [
            AtomicAction(
                action_id=f"{plan_id}_optimize",
                name="Apply Optimization",
                description=f"Optimize {target_component}",
                action_type="optimization",
                parameters={"component": target_component},
                priority=ActionPriority.HIGH,
                dependencies=[f"{plan_id}_analyze"]
            )
        ]

        optimize_step = MidLevelStep(
            step_id=f"{plan_id}_step_optimize",
            name="Optimization Phase",
            description=f"Apply optimizations to {target_component}",
            actions=optimize_actions,
            success_criteria={"optimization_applied": True}
        )

        return HighLevelPlan(
            plan_id=plan_id,
            objective=objective,
            description=f"Optimize {target_component} for better performance",
            steps=[analysis_step, optimize_step],
            risk_score=30,
            expected_outcome=f"Improved performance of {target_component}",
            metadata={"template": "optimization", "component": target_component}
        )

    @staticmethod
    def create_response_plan(threat_type: str, severity: str) -> HighLevelPlan:
        """
        Create a plan for responding to threats/anomalies.

        Args:
            threat_type: Type of threat
            severity: Severity level

        Returns:
            HighLevelPlan for threat response
        """
        plan_id = f"response_{threat_type}_{datetime.now().timestamp()}"

        # Assessment step
        assess_actions = [
            AtomicAction(
                action_id=f"{plan_id}_assess",
                name="Assess Threat",
                description=f"Assess {threat_type} threat",
                action_type="assessment",
                parameters={"threat_type": threat_type, "severity": severity},
                priority=ActionPriority.CRITICAL
            )
        ]

        assess_step = MidLevelStep(
            step_id=f"{plan_id}_step_assess",
            name="Assessment Phase",
            description=f"Assess {threat_type} impact",
            actions=assess_actions,
            success_criteria={"threat_assessed": True}
        )

        # Mitigation step
        mitigate_actions = [
            AtomicAction(
                action_id=f"{plan_id}_mitigate",
                name="Mitigate Threat",
                description=f"Apply mitigation for {threat_type}",
                action_type="mitigation",
                parameters={"threat_type": threat_type},
                priority=ActionPriority.CRITICAL,
                dependencies=[f"{plan_id}_assess"]
            )
        ]

        mitigate_step = MidLevelStep(
            step_id=f"{plan_id}_step_mitigate",
            name="Mitigation Phase",
            description=f"Mitigate {threat_type} threat",
            actions=mitigate_actions,
            success_criteria={"threat_mitigated": True}
        )

        risk_score = 80 if severity in ["HIGH", "CRITICAL"] else 50

        return HighLevelPlan(
            plan_id=plan_id,
            objective=f"Respond to {threat_type} threat",
            description=f"Comprehensive response to {severity} {threat_type}",
            steps=[assess_step, mitigate_step],
            risk_score=risk_score,
            expected_outcome=f"{threat_type} threat neutralized",
            metadata={"template": "response", "threat_type": threat_type, "severity": severity}
        )
