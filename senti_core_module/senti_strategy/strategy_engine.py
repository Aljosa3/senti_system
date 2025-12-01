"""
FAZA 15 - Strategy Engine
Core strategic planning mechanism for Senti OS

Provides goal decomposition, plan generation, risk mapping, and conflict detection.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import uuid
from .plan_template import (
    HighLevelPlan, MidLevelStep, AtomicAction,
    ActionPriority, StrategyTemplate
)


class StrategyEngine:
    """
    Core strategy engine for autonomous strategic planning.
    Uses FAZA 12 (Memory), FAZA 13 (Prediction), and FAZA 14 (Anomaly) as inputs.
    """

    MAX_STEPS = 20
    MAX_ATOMIC_ACTIONS = 50

    def __init__(
        self,
        memory_manager=None,
        prediction_manager=None,
        anomaly_manager=None
    ):
        """
        Initialize the strategy engine.

        Args:
            memory_manager: FAZA 12 Memory Manager
            prediction_manager: FAZA 13 Prediction Manager
            anomaly_manager: FAZA 14 Anomaly Manager
        """
        self.memory_manager = memory_manager
        self.prediction_manager = prediction_manager
        self.anomaly_manager = anomaly_manager
        self.generated_plans = []

    def decompose_goal(self, goal: str, context: Dict[str, Any]) -> List[str]:
        """
        Decompose a high-level goal into sub-goals.

        Args:
            goal: High-level goal description
            context: Context data

        Returns:
            List of sub-goals
        """
        # Simple goal decomposition based on keywords
        sub_goals = []

        if "optimize" in goal.lower():
            sub_goals.extend([
                "Analyze current state",
                "Identify bottlenecks",
                "Apply optimization",
                "Validate improvements"
            ])
        elif "respond" in goal.lower() or "mitigate" in goal.lower():
            sub_goals.extend([
                "Assess situation",
                "Determine response strategy",
                "Execute response",
                "Monitor outcome"
            ])
        elif "learn" in goal.lower() or "improve" in goal.lower():
            sub_goals.extend([
                "Gather data",
                "Analyze patterns",
                "Generate insights",
                "Apply learnings"
            ])
        else:
            # Generic decomposition
            sub_goals.extend([
                "Initialize",
                "Execute main task",
                "Verify results",
                "Cleanup"
            ])

        return sub_goals[:self.MAX_STEPS]

    def score_goal(self, goal: str, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Score a goal based on urgency, value, and risk.

        Args:
            goal: Goal description
            context: Context data

        Returns:
            Dictionary with urgency, value, and risk scores (0.0-1.0)
        """
        urgency = 0.5
        value = 0.5
        risk = 0.3

        # Analyze goal keywords for urgency
        if any(word in goal.lower() for word in ["critical", "urgent", "immediate", "emergency"]):
            urgency = 0.9
        elif any(word in goal.lower() for word in ["high priority", "important"]):
            urgency = 0.7

        # Analyze value
        if any(word in goal.lower() for word in ["optimize", "improve", "enhance"]):
            value = 0.8
        elif any(word in goal.lower() for word in ["fix", "repair", "resolve"]):
            value = 0.7

        # Integrate prediction risk if available
        if self.prediction_manager:
            try:
                last_pred = self.prediction_manager.get_last_prediction()
                if last_pred and last_pred.risk_score > 50:
                    risk = min(1.0, last_pred.risk_score / 100.0)
            except Exception:
                pass

        # Integrate anomaly data if available
        if self.anomaly_manager:
            try:
                active_anomalies = self.anomaly_manager.get_active_anomalies()
                if len(active_anomalies) > 3:
                    risk = min(1.0, risk + 0.2)
            except Exception:
                pass

        return {
            "urgency": urgency,
            "value": value,
            "risk": risk
        }

    def map_risk(self, plan: HighLevelPlan) -> int:
        """
        Map risk factors for a plan using FAZA 13 and FAZA 14.

        Args:
            plan: HighLevelPlan to assess

        Returns:
            Risk score (0-100)
        """
        base_risk = plan.risk_score

        # Factor in prediction risk
        if self.prediction_manager:
            try:
                last_pred = self.prediction_manager.get_last_prediction()
                if last_pred:
                    base_risk = int((base_risk + last_pred.risk_score) / 2)
            except Exception:
                pass

        # Factor in anomaly risk
        if self.anomaly_manager:
            try:
                active_anomalies = self.anomaly_manager.get_active_anomalies()
                high_severity_count = sum(
                    1 for a in active_anomalies.values()
                    if a.severity in ["HIGH", "CRITICAL"]
                )
                if high_severity_count > 0:
                    base_risk = min(100, base_risk + (high_severity_count * 10))
            except Exception:
                pass

        # Factor in plan complexity
        total_actions = plan.get_total_actions()
        if total_actions > 30:
            base_risk = min(100, base_risk + 10)

        return base_risk

    def generate_plan(
        self,
        objective: str,
        context: Dict[str, Any]
    ) -> HighLevelPlan:
        """
        Generate a strategic plan for an objective.

        Args:
            objective: High-level objective
            context: Context data

        Returns:
            HighLevelPlan
        """
        plan_id = str(uuid.uuid4())[:8]

        # Decompose goal into sub-goals
        sub_goals = self.decompose_goal(objective, context)

        # Score the goal
        scores = self.score_goal(objective, context)

        # Create steps and actions
        steps = []
        action_counter = 0

        for idx, sub_goal in enumerate(sub_goals):
            if action_counter >= self.MAX_ATOMIC_ACTIONS:
                break

            step_id = f"{plan_id}_step_{idx}"

            # Create 1-3 actions per step
            actions = []
            num_actions = min(3, self.MAX_ATOMIC_ACTIONS - action_counter)

            for action_idx in range(num_actions):
                action_id = f"{step_id}_action_{action_idx}"

                # Determine priority based on scores
                if scores["urgency"] > 0.7:
                    priority = ActionPriority.HIGH
                elif scores["urgency"] > 0.5:
                    priority = ActionPriority.MEDIUM
                else:
                    priority = ActionPriority.LOW

                action = AtomicAction(
                    action_id=action_id,
                    name=f"Action for {sub_goal}",
                    description=f"Execute {sub_goal}",
                    action_type="execution",
                    parameters={"sub_goal": sub_goal, "context": context},
                    priority=priority
                )

                actions.append(action)
                action_counter += 1

            step = MidLevelStep(
                step_id=step_id,
                name=sub_goal,
                description=f"Complete {sub_goal}",
                actions=actions,
                success_criteria={"completed": True}
            )

            steps.append(step)

        # Calculate initial risk score
        risk_score = int(scores["risk"] * 100)

        plan = HighLevelPlan(
            plan_id=plan_id,
            objective=objective,
            description=f"Strategic plan for: {objective}",
            steps=steps,
            risk_score=risk_score,
            expected_outcome=f"Successfully achieve: {objective}",
            metadata={
                "urgency": scores["urgency"],
                "value": scores["value"],
                "generated_at": datetime.now().isoformat()
            }
        )

        # Map risk using FAZA 13 + 14
        plan.risk_score = self.map_risk(plan)

        self.generated_plans.append(plan)
        return plan

    def refine_plan(
        self,
        plan: HighLevelPlan,
        feedback: Dict[str, Any]
    ) -> HighLevelPlan:
        """
        Refine a plan based on feedback.

        Args:
            plan: Existing plan to refine
            feedback: Feedback data

        Returns:
            Refined HighLevelPlan
        """
        # Adjust risk score based on feedback
        if feedback.get("reduce_risk"):
            plan.risk_score = max(0, plan.risk_score - 10)

        # Remove low-priority actions if needed
        if feedback.get("simplify"):
            for step in plan.steps:
                step.actions = [
                    a for a in step.actions
                    if a.priority != ActionPriority.LOW
                ]

        # Add error handling if requested
        if feedback.get("add_error_handling"):
            for step in plan.steps:
                if len(step.actions) < 5:
                    error_action = AtomicAction(
                        action_id=f"{step.step_id}_error_handler",
                        name="Error Handler",
                        description="Handle errors in step",
                        action_type="error_handling",
                        parameters={"step": step.step_id},
                        priority=ActionPriority.HIGH
                    )
                    step.actions.append(error_action)

        plan.optimized_count += 1
        return plan

    def detect_conflicts(self, plan: HighLevelPlan) -> List[str]:
        """
        Detect conflicts in a plan using FAZA 8 security rules.

        Args:
            plan: Plan to check

        Returns:
            List of conflict descriptions
        """
        conflicts = []

        # Check plan size constraints
        if plan.get_total_steps() > self.MAX_STEPS:
            conflicts.append(f"Plan exceeds maximum steps ({self.MAX_STEPS})")

        if plan.get_total_actions() > self.MAX_ATOMIC_ACTIONS:
            conflicts.append(f"Plan exceeds maximum actions ({self.MAX_ATOMIC_ACTIONS})")

        # Check for circular dependencies
        action_deps = {}
        for step in plan.steps:
            for action in step.actions:
                action_deps[action.action_id] = action.dependencies

        visited = set()
        def has_cycle(action_id, path):
            if action_id in path:
                return True
            if action_id in visited:
                return False
            visited.add(action_id)
            for dep in action_deps.get(action_id, []):
                if has_cycle(dep, path + [action_id]):
                    return True
            return False

        for action_id in action_deps:
            if has_cycle(action_id, []):
                conflicts.append(f"Circular dependency detected involving {action_id}")
                break

        return conflicts

    def get_plan_stats(self) -> Dict[str, Any]:
        """
        Get statistics about generated plans.

        Returns:
            Statistics dictionary
        """
        return {
            "total_plans": len(self.generated_plans),
            "avg_steps": sum(p.get_total_steps() for p in self.generated_plans) / len(self.generated_plans) if self.generated_plans else 0,
            "avg_actions": sum(p.get_total_actions() for p in self.generated_plans) / len(self.generated_plans) if self.generated_plans else 0,
            "avg_risk": sum(p.risk_score for p in self.generated_plans) / len(self.generated_plans) if self.generated_plans else 0
        }
