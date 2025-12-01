"""
FAZA 15 - Strategy Manager
High-level orchestrator for strategic planning operations
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from .strategy_engine import StrategyEngine
from .reasoning_engine import ReasoningEngine
from .strategy_rules import StrategyRules
from .plan_template import HighLevelPlan
from .strategy_events import (
    StrategyCreatedEvent,
    StrategyOptimizedEvent,
    StrategyRejectedEvent,
    HighRiskStrategyEvent,
    StrategyExecutedEvent,
    StrategySimulationEvent
)


class StrategyManager:
    """
    Orchestrates strategic planning using strategy_engine and reasoning_engine.
    """

    def __init__(
        self,
        memory_manager=None,
        prediction_manager=None,
        anomaly_manager=None,
        event_bus=None,
        security_manager=None
    ):
        """
        Initialize strategy manager.

        Args:
            memory_manager: FAZA 12 Memory Manager
            prediction_manager: FAZA 13 Prediction Manager
            anomaly_manager: FAZA 14 Anomaly Manager
            event_bus: EventBus for publishing events
            security_manager: FAZA 8 Security Manager
        """
        self.memory_manager = memory_manager
        self.event_bus = event_bus

        self.engine = StrategyEngine(
            memory_manager,
            prediction_manager,
            anomaly_manager
        )

        self.reasoning = ReasoningEngine(
            memory_manager,
            prediction_manager,
            anomaly_manager
        )

        self.rules = StrategyRules(security_manager)

        self.active_strategies = {}
        self.strategy_count = 0
        self.enabled = True

    def create_strategy(
        self,
        objective: str,
        context: Optional[Dict[str, Any]] = None
    ) -> HighLevelPlan:
        """
        Create a new strategy.

        Args:
            objective: High-level objective
            context: Optional context data

        Returns:
            HighLevelPlan
        """
        if not self.enabled:
            return self._create_disabled_plan()

        context = context or {}

        # Generate plan using strategy engine
        plan = self.engine.generate_plan(objective, context)

        # Validate plan
        if not self.rules.validate_plan(plan):
            self._publish_rejection_event(plan, self.rules.get_violations())
            raise ValueError(f"Strategy validation failed: {self.rules.get_violations()}")

        # Check risk threshold
        if plan.risk_score > 80:
            self._publish_high_risk_event(plan)

        # Store in active strategies
        self.active_strategies[plan.plan_id] = plan
        self.strategy_count += 1

        # Store in episodic memory
        self._store_in_episodic(plan)

        # Publish creation event
        self._publish_creation_event(plan)

        return plan

    def evaluate_strategy(self, plan: HighLevelPlan) -> Dict[str, Any]:
        """
        Evaluate a strategy using reasoning engine.

        Args:
            plan: Plan to evaluate

        Returns:
            Evaluation results
        """
        # Perform chain-of-thought reasoning
        reasoning_steps = self.reasoning.chain_of_thought(
            plan.objective,
            {"plan_id": plan.plan_id, "risk_score": plan.risk_score}
        )

        # Simulate outcome
        simulation = self.reasoning.simulate_outcome(
            plan.objective,
            {"current_state": "active"}
        )

        # Build decision tree
        options = [step.name for step in plan.steps[:3]]  # Top 3 steps
        decision_tree = self.reasoning.build_decision_tree(
            options,
            {"urgency": 0.4, "value": 0.4, "risk": 0.2}
        )

        evaluation = {
            "plan_id": plan.plan_id,
            "reasoning_steps": reasoning_steps,
            "simulation": simulation,
            "decision_tree": decision_tree,
            "recommendation": "proceed" if plan.risk_score < 60 else "review",
            "evaluated_at": datetime.now().isoformat()
        }

        return evaluation

    def optimize_strategy(
        self,
        plan_id: str,
        feedback: Optional[Dict[str, Any]] = None
    ) -> HighLevelPlan:
        """
        Optimize an existing strategy.

        Args:
            plan_id: Plan ID to optimize
            feedback: Optional feedback for optimization

        Returns:
            Optimized HighLevelPlan
        """
        if plan_id not in self.active_strategies:
            raise KeyError(f"Plan {plan_id} not found")

        plan = self.active_strategies[plan_id]
        feedback = feedback or {"simplify": True}

        # Refine plan using strategy engine
        optimized_plan = self.engine.refine_plan(plan, feedback)

        # Validate optimized plan
        if not self.rules.validate_plan(optimized_plan):
            raise ValueError(f"Optimized plan validation failed: {self.rules.get_violations()}")

        # Update active strategies
        self.active_strategies[plan_id] = optimized_plan

        # Publish optimization event
        self._publish_optimization_event(optimized_plan)

        return optimized_plan

    def execute_atomic_action(
        self,
        plan_id: str,
        action_id: str
    ) -> Dict[str, Any]:
        """
        Execute a single atomic action.

        Args:
            plan_id: Plan ID
            action_id: Action ID

        Returns:
            Execution result
        """
        if plan_id not in self.active_strategies:
            raise KeyError(f"Plan {plan_id} not found")

        plan = self.active_strategies[plan_id]

        # Find action
        action = None
        for step in plan.steps:
            for a in step.actions:
                if a.action_id == action_id:
                    action = a
                    break

        if not action:
            raise KeyError(f"Action {action_id} not found in plan {plan_id}")

        # Simulate execution (real implementation would actually execute)
        result = {
            "plan_id": plan_id,
            "action_id": action_id,
            "action_name": action.name,
            "status": "completed",
            "result": "Action executed successfully",
            "executed_at": datetime.now().isoformat()
        }

        action.result = result

        return result

    def simulate_outcome(
        self,
        plan: HighLevelPlan
    ) -> Dict[str, Any]:
        """
        Simulate strategy outcome.

        Args:
            plan: Plan to simulate

        Returns:
            Simulation results
        """
        simulation = self.reasoning.simulate_outcome(
            plan.objective,
            {"plan_id": plan.plan_id}
        )

        # Publish simulation event
        self._publish_simulation_event(plan, simulation)

        return simulation

    def get_active_strategies(self) -> Dict[str, HighLevelPlan]:
        """Get all active strategies."""
        return self.active_strategies.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get strategy manager statistics."""
        return {
            "total_strategies": self.strategy_count,
            "active_strategies": len(self.active_strategies),
            "enabled": self.enabled,
            "engine_stats": self.engine.get_plan_stats(),
            "reasoning_stats": self.reasoning.get_reasoning_stats()
        }

    def enable(self):
        """Enable strategy manager."""
        self.enabled = True

    def disable(self):
        """Disable strategy manager."""
        self.enabled = False

    def _store_in_episodic(self, plan: HighLevelPlan):
        """Store plan in episodic memory."""
        if not self.memory_manager:
            return

        try:
            self.memory_manager.episodic_memory.store(
                event_type="STRATEGY",
                data=plan.to_dict(),
                tags=["strategy", f"risk_{plan.risk_score}"]
            )
        except Exception as e:
            print(f"[StrategyManager] Failed to store in memory: {e}")

    def _publish_creation_event(self, plan: HighLevelPlan):
        """Publish strategy creation event."""
        if not self.event_bus:
            return

        try:
            event = StrategyCreatedEvent(
                plan_id=plan.plan_id,
                objective=plan.objective,
                risk_score=plan.risk_score,
                details={"steps": plan.get_total_steps(), "actions": plan.get_total_actions()}
            )
            self.event_bus.emit(event.event_type, event.to_dict())
        except Exception as e:
            print(f"[StrategyManager] Failed to publish event: {e}")

    def _publish_optimization_event(self, plan: HighLevelPlan):
        """Publish strategy optimization event."""
        if not self.event_bus:
            return

        try:
            event = StrategyOptimizedEvent(
                plan_id=plan.plan_id,
                optimization_count=plan.optimized_count,
                improvements={"risk_reduced": True}
            )
            self.event_bus.emit(event.event_type, event.to_dict())
        except Exception as e:
            print(f"[StrategyManager] Failed to publish event: {e}")

    def _publish_rejection_event(self, plan: HighLevelPlan, violations: List[str]):
        """Publish strategy rejection event."""
        if not self.event_bus:
            return

        try:
            event = StrategyRejectedEvent(
                plan_id=plan.plan_id,
                reason="Validation failed",
                violations=violations
            )
            self.event_bus.emit(event.event_type, event.to_dict())
        except Exception as e:
            print(f"[StrategyManager] Failed to publish event: {e}")

    def _publish_high_risk_event(self, plan: HighLevelPlan):
        """Publish high risk strategy event."""
        if not self.event_bus:
            return

        try:
            event = HighRiskStrategyEvent(
                plan_id=plan.plan_id,
                risk_score=plan.risk_score,
                objective=plan.objective,
                risk_factors=["high_complexity", "prediction_risk"]
            )
            self.event_bus.emit(event.event_type, event.to_dict())
        except Exception as e:
            print(f"[StrategyManager] Failed to publish event: {e}")

    def _publish_simulation_event(self, plan: HighLevelPlan, simulation: Dict[str, Any]):
        """Publish simulation event."""
        if not self.event_bus:
            return

        try:
            event = StrategySimulationEvent(
                plan_id=plan.plan_id,
                simulation_results=simulation
            )
            self.event_bus.emit(event.event_type, event.to_dict())
        except Exception as e:
            print(f"[StrategyManager] Failed to publish event: {e}")

    def _create_disabled_plan(self) -> HighLevelPlan:
        """Create a disabled plan."""
        from .plan_template import StrategyTemplate
        return StrategyTemplate.create_empty_plan("disabled", "System disabled")
