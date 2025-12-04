"""
FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise Edition)
Strategy Adapter

Dynamically adapts system behavior based on:
- Current system state
- Agent performance
- Load conditions
- Detected anomalies

Adaptation capabilities:
- Adjust scheduling strategy (priority/round-robin/load-aware)
- Modify agent priorities in real-time
- Reroute events between agents
- Adjust tick-rate of individual agents
- Apply enterprise-level strategies ("aggressive", "balanced", "safe")
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SystemStrategy(Enum):
    """Enterprise-level system strategies"""
    AGGRESSIVE = "aggressive"  # Maximum performance, higher risk
    BALANCED = "balanced"      # Balance performance and stability
    SAFE = "safe"              # Maximum stability, conservative
    ADAPTIVE = "adaptive"      # Auto-adapt based on conditions


@dataclass
class AdaptationAction:
    """
    Action to adapt system behavior.

    Attributes:
        action_type: Type of adaptation
        target: Target agent or component
        old_value: Previous value
        new_value: New value
        reason: Reason for adaptation
        timestamp: When adaptation was made
    """
    action_type: str
    target: str
    old_value: Any
    new_value: Any
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        return f"<AdaptationAction: {self.action_type} on {self.target}>"


class StrategyAdapter:
    """
    Enterprise strategy adaptation engine.

    Dynamically adapts system behavior based on real-time conditions.
    Supports multiple adaptation strategies and enterprise-level policies.
    """

    def __init__(
        self,
        default_strategy: SystemStrategy = SystemStrategy.BALANCED,
        auto_adapt: bool = True,
        adaptation_cooldown: float = 30.0
    ):
        """
        Initialize strategy adapter.

        Args:
            default_strategy: Default system strategy
            auto_adapt: Enable automatic adaptation
            adaptation_cooldown: Minimum time between adaptations (seconds)
        """
        self.current_strategy = default_strategy
        self.auto_adapt = auto_adapt
        self.adaptation_cooldown = adaptation_cooldown

        # Adaptation history
        self.adaptation_history: List[AdaptationAction] = []
        self.last_adaptation_time: Dict[str, datetime] = {}

        # Strategy parameters
        self.strategy_params = self._init_strategy_params()

        logger.info(f"StrategyAdapter initialized: strategy={default_strategy.value}")

    def _init_strategy_params(self) -> Dict[SystemStrategy, Dict[str, Any]]:
        """
        Initialize parameters for each strategy.

        Returns:
            Dictionary of strategy -> parameters
        """
        return {
            SystemStrategy.AGGRESSIVE: {
                "scheduling_strategy": "priority",
                "tick_rate_multiplier": 1.5,
                "max_concurrent_agents": 50,
                "error_tolerance": 0.1,
                "priority_boost": 2,
                "throttle_threshold": 0.9
            },
            SystemStrategy.BALANCED: {
                "scheduling_strategy": "load_aware",
                "tick_rate_multiplier": 1.0,
                "max_concurrent_agents": 20,
                "error_tolerance": 0.05,
                "priority_boost": 1,
                "throttle_threshold": 0.7
            },
            SystemStrategy.SAFE: {
                "scheduling_strategy": "round_robin",
                "tick_rate_multiplier": 0.7,
                "max_concurrent_agents": 10,
                "error_tolerance": 0.01,
                "priority_boost": 0,
                "throttle_threshold": 0.5
            },
            SystemStrategy.ADAPTIVE: {
                "scheduling_strategy": "load_aware",
                "tick_rate_multiplier": 1.0,
                "max_concurrent_agents": 20,
                "error_tolerance": 0.05,
                "priority_boost": 1,
                "throttle_threshold": 0.7
            }
        }

    def adapt_system(
        self,
        system_metrics: Dict[str, Any],
        agent_scores: Dict[str, Any],
        anomalies: List[Any],
        stability_issues: List[Any]
    ) -> List[AdaptationAction]:
        """
        Adapt system based on current state.

        Args:
            system_metrics: System-wide metrics
            agent_scores: Agent performance scores
            anomalies: Detected anomalies
            stability_issues: Stability issues

        Returns:
            List of AdaptationAction objects

        TODO: Add adaptation prediction
        TODO: Add rollback mechanism
        """
        if not self.auto_adapt:
            return []

        actions = []

        # Determine if strategy change needed
        if self.current_strategy == SystemStrategy.ADAPTIVE:
            new_strategy = self._determine_optimal_strategy(
                system_metrics, agent_scores, anomalies, stability_issues
            )
            if new_strategy != self.current_strategy:
                action = self._change_strategy(new_strategy)
                if action:
                    actions.append(action)

        # Agent-specific adaptations
        actions.extend(self._adapt_agent_priorities(agent_scores))
        actions.extend(self._adapt_agent_tick_rates(agent_scores, system_metrics))
        actions.extend(self._adapt_scheduling(system_metrics))

        # Event routing adaptations
        if anomalies:
            actions.extend(self._adapt_event_routing(anomalies))

        # Store actions
        self.adaptation_history.extend(actions)

        # Limit history
        if len(self.adaptation_history) > 1000:
            self.adaptation_history = self.adaptation_history[-1000:]

        return actions

    def _determine_optimal_strategy(
        self,
        system_metrics: Dict[str, Any],
        agent_scores: Dict[str, Any],
        anomalies: List[Any],
        stability_issues: List[Any]
    ) -> SystemStrategy:
        """
        Determine optimal strategy based on current conditions.

        Args:
            system_metrics: System metrics
            agent_scores: Agent scores
            anomalies: Anomalies
            stability_issues: Stability issues

        Returns:
            Recommended SystemStrategy
        """
        # Calculate system health
        avg_score = system_metrics.get("avg_meta_score", 0.5)
        error_rate = system_metrics.get("error_rate", 0.0)
        anomaly_count = len(anomalies)
        stability_count = len(stability_issues)

        # Decision logic
        if stability_count > 2 or anomaly_count > 5:
            # System unstable, switch to SAFE
            return SystemStrategy.SAFE

        elif avg_score > 0.8 and error_rate < 0.01 and anomaly_count == 0:
            # System healthy, can be AGGRESSIVE
            return SystemStrategy.AGGRESSIVE

        else:
            # Default to BALANCED
            return SystemStrategy.BALANCED

    def _change_strategy(self, new_strategy: SystemStrategy) -> Optional[AdaptationAction]:
        """
        Change system strategy.

        Args:
            new_strategy: New strategy to apply

        Returns:
            AdaptationAction or None
        """
        if new_strategy == self.current_strategy:
            return None

        old_strategy = self.current_strategy
        self.current_strategy = new_strategy

        logger.info(f"Strategy changed: {old_strategy.value} -> {new_strategy.value}")

        return AdaptationAction(
            action_type="change_strategy",
            target="system",
            old_value=old_strategy.value,
            new_value=new_strategy.value,
            reason=f"Adaptive strategy change to {new_strategy.value}"
        )

    def _adapt_agent_priorities(
        self,
        agent_scores: Dict[str, Any]
    ) -> List[AdaptationAction]:
        """
        Adapt agent priorities based on scores.

        Args:
            agent_scores: Agent score dictionary

        Returns:
            List of AdaptationAction objects

        TODO: Integrate with FAZA 28 agent_manager
        """
        actions = []

        params = self.strategy_params[self.current_strategy]
        priority_boost = params["priority_boost"]

        for agent_name, score in agent_scores.items():
            meta_score = score.get("meta_score", 0.5)

            # Boost priority for high-performing agents
            if meta_score > 0.8 and priority_boost > 0:
                if self._can_adapt(f"priority_{agent_name}"):
                    actions.append(AdaptationAction(
                        action_type="boost_priority",
                        target=agent_name,
                        old_value=score.get("priority", 5),
                        new_value=score.get("priority", 5) + priority_boost,
                        reason=f"High performance (score={meta_score:.3f})"
                    ))

            # Reduce priority for low-performing agents
            elif meta_score < 0.3:
                if self._can_adapt(f"priority_{agent_name}"):
                    actions.append(AdaptationAction(
                        action_type="reduce_priority",
                        target=agent_name,
                        old_value=score.get("priority", 5),
                        new_value=max(1, score.get("priority", 5) - 1),
                        reason=f"Low performance (score={meta_score:.3f})"
                    ))

        return actions

    def _adapt_agent_tick_rates(
        self,
        agent_scores: Dict[str, Any],
        system_metrics: Dict[str, Any]
    ) -> List[AdaptationAction]:
        """
        Adapt agent tick rates based on performance and load.

        Args:
            agent_scores: Agent scores
            system_metrics: System metrics

        Returns:
            List of AdaptationAction objects

        TODO: Integrate with FAZA 28 scheduler
        """
        actions = []

        params = self.strategy_params[self.current_strategy]
        tick_multiplier = params["tick_rate_multiplier"]

        system_load = system_metrics.get("system_load", 0.5)

        for agent_name, score in agent_scores.items():
            meta_score = score.get("meta_score", 0.5)

            # Throttle slow agents if system under load
            if system_load > 0.7 and meta_score < 0.4:
                if self._can_adapt(f"tick_rate_{agent_name}"):
                    actions.append(AdaptationAction(
                        action_type="throttle_tick_rate",
                        target=agent_name,
                        old_value=1.0,
                        new_value=0.5,
                        reason=f"System overload + low performance"
                    ))

            # Boost tick rate for high-performing agents
            elif system_load < 0.5 and meta_score > 0.8:
                if self._can_adapt(f"tick_rate_{agent_name}"):
                    actions.append(AdaptationAction(
                        action_type="boost_tick_rate",
                        target=agent_name,
                        old_value=1.0,
                        new_value=tick_multiplier,
                        reason=f"System idle + high performance"
                    ))

        return actions

    def _adapt_scheduling(
        self,
        system_metrics: Dict[str, Any]
    ) -> List[AdaptationAction]:
        """
        Adapt scheduling strategy.

        Args:
            system_metrics: System metrics

        Returns:
            List of AdaptationAction objects

        TODO: Integrate with FAZA 28 scheduler
        """
        actions = []

        params = self.strategy_params[self.current_strategy]
        target_strategy = params["scheduling_strategy"]

        current_scheduling = system_metrics.get("scheduling_strategy", "priority")

        if target_strategy != current_scheduling:
            if self._can_adapt("scheduling_strategy"):
                actions.append(AdaptationAction(
                    action_type="change_scheduling",
                    target="scheduler",
                    old_value=current_scheduling,
                    new_value=target_strategy,
                    reason=f"Strategy {self.current_strategy.value} requires {target_strategy}"
                ))

        return actions

    def _adapt_event_routing(self, anomalies: List[Any]) -> List[AdaptationAction]:
        """
        Adapt event routing to avoid problematic agents.

        Args:
            anomalies: List of anomalies

        Returns:
            List of AdaptationAction objects

        TODO: Integrate with FAZA 28 event_bus
        """
        actions = []

        # Find agents with event anomalies
        problematic_agents = set()
        for anomaly in anomalies:
            if hasattr(anomaly, "anomaly_type") and "event" in anomaly.anomaly_type.value:
                problematic_agents.add(anomaly.agent_name)

        for agent_name in problematic_agents:
            if self._can_adapt(f"event_routing_{agent_name}"):
                actions.append(AdaptationAction(
                    action_type="reroute_events",
                    target=agent_name,
                    old_value="normal",
                    new_value="isolated",
                    reason=f"Event anomaly detected"
                ))

        return actions

    def _can_adapt(self, adaptation_key: str) -> bool:
        """
        Check if adaptation is allowed (respect cooldown).

        Args:
            adaptation_key: Key for this adaptation type

        Returns:
            True if adaptation allowed
        """
        last_time = self.last_adaptation_time.get(adaptation_key)
        if last_time is None:
            self.last_adaptation_time[adaptation_key] = datetime.now()
            return True

        time_since = (datetime.now() - last_time).total_seconds()
        if time_since >= self.adaptation_cooldown:
            self.last_adaptation_time[adaptation_key] = datetime.now()
            return True

        return False

    def apply_strategy(self, strategy: SystemStrategy) -> None:
        """
        Manually apply a strategy.

        Args:
            strategy: Strategy to apply
        """
        action = self._change_strategy(strategy)
        if action:
            self.adaptation_history.append(action)
            logger.info(f"Manually applied strategy: {strategy.value}")

    def get_current_params(self) -> Dict[str, Any]:
        """
        Get current strategy parameters.

        Returns:
            Dictionary of current parameters
        """
        return self.strategy_params[self.current_strategy].copy()

    def get_adaptation_summary(self) -> Dict[str, Any]:
        """
        Get adaptation summary.

        Returns:
            Dictionary with adaptation statistics
        """
        recent_actions = [
            a for a in self.adaptation_history
            if (datetime.now() - a.timestamp).total_seconds() < 300
        ]

        return {
            "current_strategy": self.current_strategy.value,
            "auto_adapt": self.auto_adapt,
            "total_adaptations": len(self.adaptation_history),
            "recent_adaptations": len(recent_actions),
            "adaptations_by_type": {
                action_type: len([a for a in recent_actions if a.action_type == action_type])
                for action_type in set(a.action_type for a in recent_actions)
            }
        }

    def reset(self) -> None:
        """Reset adaptation history"""
        self.adaptation_history.clear()
        self.last_adaptation_time.clear()
        logger.info("Strategy adapter reset")

    def __repr__(self) -> str:
        return f"<StrategyAdapter: {self.current_strategy.value}>"


# Singleton instance
_strategy_adapter_instance: Optional[StrategyAdapter] = None


def get_strategy_adapter() -> StrategyAdapter:
    """
    Get singleton StrategyAdapter instance.

    Returns:
        Global StrategyAdapter instance
    """
    global _strategy_adapter_instance
    if _strategy_adapter_instance is None:
        _strategy_adapter_instance = StrategyAdapter()
    return _strategy_adapter_instance


def create_strategy_adapter(**kwargs) -> StrategyAdapter:
    """
    Factory function: create new StrategyAdapter instance.

    Args:
        **kwargs: Arguments passed to StrategyAdapter constructor

    Returns:
        New StrategyAdapter instance
    """
    return StrategyAdapter(**kwargs)
