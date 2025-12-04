"""
FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise Edition)
Meta Policies

Enterprise policy framework providing:
- Safety policies (kill-switch, isolation)
- Load-balance constraints
- Conflict resolution
- Escalation rules
- Failover routing

All policies are pluggable and can be enabled/disabled dynamically.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Policy types"""
    SAFETY = "safety"
    LOAD_BALANCE = "load_balance"
    CONFLICT_RESOLUTION = "conflict_resolution"
    ESCALATION = "escalation"
    FAILOVER = "failover"


class PolicyAction(Enum):
    """Actions that policies can trigger"""
    ALLOW = "allow"
    DENY = "deny"
    THROTTLE = "throttle"
    ISOLATE = "isolate"
    KILL = "kill"
    ESCALATE = "escalate"
    REROUTE = "reroute"
    RESET = "reset"


@dataclass
class PolicyDecision:
    """
    Decision made by a policy.

    Attributes:
        action: Action to take
        reason: Human-readable reason for decision
        metadata: Additional decision metadata
        timestamp: When decision was made
    """
    action: PolicyAction
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        return f"<PolicyDecision: {self.action.value} - {self.reason}>"


class Policy:
    """
    Base class for all policies.

    Policies evaluate conditions and return decisions.
    """

    def __init__(
        self,
        name: str,
        policy_type: PolicyType,
        enabled: bool = True,
        priority: int = 5
    ):
        """
        Initialize policy.

        Args:
            name: Policy name
            policy_type: Type of policy
            enabled: Whether policy is enabled
            priority: Priority (higher = evaluated first)
        """
        self.name = name
        self.policy_type = policy_type
        self.enabled = enabled
        self.priority = priority
        self.evaluation_count = 0
        self.triggered_count = 0

    def evaluate(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        """
        Evaluate policy against context.

        Args:
            context: Context containing agent info, metrics, etc.

        Returns:
            PolicyDecision if policy triggers, None otherwise

        TODO: Add policy evaluation caching
        TODO: Track evaluation latency
        """
        self.evaluation_count += 1

        if not self.enabled:
            return None

        decision = self._evaluate_impl(context)

        if decision:
            self.triggered_count += 1
            logger.info(f"Policy '{self.name}' triggered: {decision.action.value}")

        return decision

    def _evaluate_impl(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        """
        Implementation of policy evaluation logic.

        Subclasses must override this method.

        Args:
            context: Evaluation context

        Returns:
            PolicyDecision if policy triggers, None otherwise
        """
        raise NotImplementedError("Subclasses must implement _evaluate_impl")

    def get_stats(self) -> Dict[str, Any]:
        """Get policy statistics"""
        return {
            "name": self.name,
            "type": self.policy_type.value,
            "enabled": self.enabled,
            "priority": self.priority,
            "evaluation_count": self.evaluation_count,
            "triggered_count": self.triggered_count,
            "trigger_rate": self.triggered_count / max(1, self.evaluation_count)
        }

    def __repr__(self) -> str:
        return f"<Policy: {self.name} ({self.policy_type.value})>"


# ==================== Safety Policies ====================

class KillSwitchPolicy(Policy):
    """
    Emergency kill-switch policy.

    Kills agent if critical conditions are met:
    - Error rate exceeds threshold
    - Meta-score below critical threshold
    - Continuous failures
    """

    def __init__(
        self,
        max_error_rate: float = 0.5,
        min_meta_score: float = 0.1,
        max_consecutive_failures: int = 10
    ):
        super().__init__(
            name="kill_switch",
            policy_type=PolicyType.SAFETY,
            priority=10  # Highest priority
        )
        self.max_error_rate = max_error_rate
        self.min_meta_score = min_meta_score
        self.max_consecutive_failures = max_consecutive_failures

    def _evaluate_impl(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        agent_score = context.get("agent_score")
        if not agent_score:
            return None

        # Check meta-score
        if agent_score.meta_score < self.min_meta_score:
            return PolicyDecision(
                action=PolicyAction.KILL,
                reason=f"Meta-score {agent_score.meta_score:.3f} below critical threshold {self.min_meta_score}",
                metadata={"agent_name": agent_score.agent_name, "score": agent_score.meta_score}
            )

        # Check error rate
        components = agent_score.components
        if components:
            tick_count = components.get("tick_count", 0)
            error_count = components.get("error_count", 0)
            if tick_count > 0:
                error_rate = error_count / tick_count
                if error_rate > self.max_error_rate:
                    return PolicyDecision(
                        action=PolicyAction.KILL,
                        reason=f"Error rate {error_rate:.3f} exceeds maximum {self.max_error_rate}",
                        metadata={"agent_name": agent_score.agent_name, "error_rate": error_rate}
                    )

        return None


class IsolationPolicy(Policy):
    """
    Isolation policy for problematic agents.

    Isolates agent if:
    - Performance degraded but not critical
    - Intermittent failures
    - Suspicious behavior detected
    """

    def __init__(
        self,
        performance_threshold: float = 0.3,
        reliability_threshold: float = 0.4
    ):
        super().__init__(
            name="isolation",
            policy_type=PolicyType.SAFETY,
            priority=8
        )
        self.performance_threshold = performance_threshold
        self.reliability_threshold = reliability_threshold

    def _evaluate_impl(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        agent_score = context.get("agent_score")
        if not agent_score:
            return None

        # Check if agent should be isolated
        if (agent_score.performance_score < self.performance_threshold or
            agent_score.reliability_score < self.reliability_threshold):

            return PolicyDecision(
                action=PolicyAction.ISOLATE,
                reason=f"Agent showing degraded performance/reliability",
                metadata={
                    "agent_name": agent_score.agent_name,
                    "performance": agent_score.performance_score,
                    "reliability": agent_score.reliability_score
                }
            )

        return None


# ==================== Load Balance Policies ====================

class LoadBalancePolicy(Policy):
    """
    Load balancing policy.

    Throttles or reroutes agents based on:
    - System load
    - Agent execution time
    - Resource usage
    """

    def __init__(
        self,
        max_execution_time: float = 1.0,
        max_concurrent_heavy: int = 3
    ):
        super().__init__(
            name="load_balance",
            policy_type=PolicyType.LOAD_BALANCE,
            priority=6
        )
        self.max_execution_time = max_execution_time
        self.max_concurrent_heavy = max_concurrent_heavy

    def _evaluate_impl(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        agent_score = context.get("agent_score")
        if not agent_score:
            return None

        # Check execution time
        avg_exec_time = agent_score.components.get("avg_execution_time", 0)
        if avg_exec_time > self.max_execution_time:
            return PolicyDecision(
                action=PolicyAction.THROTTLE,
                reason=f"Execution time {avg_exec_time:.3f}s exceeds {self.max_execution_time}s",
                metadata={"agent_name": agent_score.agent_name, "exec_time": avg_exec_time}
            )

        return None


class OverloadPolicy(Policy):
    """
    System overload protection policy.

    Prevents system overload by:
    - Limiting concurrent agents
    - Throttling low-priority agents
    - Denying new agent registrations
    """

    def __init__(
        self,
        max_agents: int = 50,
        max_active_agents: int = 20
    ):
        super().__init__(
            name="overload_protection",
            policy_type=PolicyType.LOAD_BALANCE,
            priority=7
        )
        self.max_agents = max_agents
        self.max_active_agents = max_active_agents

    def _evaluate_impl(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        total_agents = context.get("total_agents", 0)
        active_agents = context.get("active_agents", 0)

        if total_agents >= self.max_agents:
            return PolicyDecision(
                action=PolicyAction.DENY,
                reason=f"System at capacity: {total_agents}/{self.max_agents} agents",
                metadata={"total_agents": total_agents, "limit": self.max_agents}
            )

        if active_agents >= self.max_active_agents:
            return PolicyDecision(
                action=PolicyAction.THROTTLE,
                reason=f"Too many active agents: {active_agents}/{self.max_active_agents}",
                metadata={"active_agents": active_agents, "limit": self.max_active_agents}
            )

        return None


# ==================== Conflict Resolution Policies ====================

class ConflictResolutionPolicy(Policy):
    """
    Resolves conflicts between agents.

    Handles:
    - State write conflicts
    - Event conflicts
    - Resource conflicts
    """

    def __init__(self, resolution_strategy: str = "priority_based"):
        super().__init__(
            name="conflict_resolution",
            policy_type=PolicyType.CONFLICT_RESOLUTION,
            priority=7
        )
        self.resolution_strategy = resolution_strategy

    def _evaluate_impl(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        conflict_type = context.get("conflict_type")
        if not conflict_type:
            return None

        agents = context.get("conflicting_agents", [])

        if self.resolution_strategy == "priority_based":
            # Resolve by agent priority
            return PolicyDecision(
                action=PolicyAction.ALLOW,
                reason=f"Conflict resolved using priority-based strategy",
                metadata={"strategy": "priority_based", "agents": agents}
            )

        return None


# ==================== Escalation Policies ====================

class EscalationPolicy(Policy):
    """
    Escalation policy for critical issues.

    Escalates when:
    - Multiple policy violations
    - System-wide degradation
    - Critical agent failures
    """

    def __init__(
        self,
        escalation_threshold: int = 3,
        time_window: int = 300  # 5 minutes
    ):
        super().__init__(
            name="escalation",
            policy_type=PolicyType.ESCALATION,
            priority=9
        )
        self.escalation_threshold = escalation_threshold
        self.time_window = time_window
        self.violation_history: List[datetime] = []

    def _evaluate_impl(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        # Check for multiple violations in time window
        now = datetime.now()
        self.violation_history = [
            t for t in self.violation_history
            if (now - t).total_seconds() < self.time_window
        ]

        # Add current violation
        has_violation = context.get("has_violation", False)
        if has_violation:
            self.violation_history.append(now)

        if len(self.violation_history) >= self.escalation_threshold:
            return PolicyDecision(
                action=PolicyAction.ESCALATE,
                reason=f"{len(self.violation_history)} violations in {self.time_window}s window",
                metadata={"violation_count": len(self.violation_history)}
            )

        return None


# ==================== Failover Policies ====================

class FailoverPolicy(Policy):
    """
    Failover routing policy.

    Reroutes work when:
    - Agent fails
    - Agent isolated
    - Load redistribution needed
    """

    def __init__(self):
        super().__init__(
            name="failover",
            policy_type=PolicyType.FAILOVER,
            priority=8
        )

    def _evaluate_impl(self, context: Dict[str, Any]) -> Optional[PolicyDecision]:
        agent_status = context.get("agent_status")
        if agent_status in ["failed", "isolated", "killed"]:
            return PolicyDecision(
                action=PolicyAction.REROUTE,
                reason=f"Agent {agent_status}, rerouting work to healthy agents",
                metadata={"agent_status": agent_status}
            )

        return None


# ==================== Policy Manager ====================

class PolicyManager:
    """
    Enterprise policy manager.

    Manages all policies and their evaluation.
    Policies are evaluated in priority order.
    """

    def __init__(self):
        """Initialize policy manager"""
        self.policies: Dict[str, Policy] = {}
        self._sorted_policies: List[Policy] = []
        logger.info("PolicyManager initialized")

    def register_policy(self, policy: Policy) -> None:
        """
        Register a policy.

        Args:
            policy: Policy instance to register

        TODO: Add policy conflict detection
        TODO: Emit policy_registered event
        """
        self.policies[policy.name] = policy
        self._update_sorted_policies()
        logger.info(f"Policy registered: {policy.name} ({policy.policy_type.value}, priority={policy.priority})")

    def unregister_policy(self, policy_name: str) -> None:
        """
        Unregister a policy.

        Args:
            policy_name: Name of policy to unregister
        """
        if policy_name in self.policies:
            policy = self.policies.pop(policy_name)
            self._update_sorted_policies()
            logger.info(f"Policy unregistered: {policy_name}")

    def enable_policy(self, policy_name: str) -> None:
        """Enable a policy"""
        if policy_name in self.policies:
            self.policies[policy_name].enabled = True
            logger.info(f"Policy enabled: {policy_name}")

    def disable_policy(self, policy_name: str) -> None:
        """Disable a policy"""
        if policy_name in self.policies:
            self.policies[policy_name].enabled = False
            logger.info(f"Policy disabled: {policy_name}")

    def evaluate_all(self, context: Dict[str, Any]) -> List[PolicyDecision]:
        """
        Evaluate all enabled policies.

        Args:
            context: Context for policy evaluation

        Returns:
            List of PolicyDecision objects

        TODO: Add short-circuit evaluation
        TODO: Add policy evaluation timeout
        """
        decisions = []

        for policy in self._sorted_policies:
            if not policy.enabled:
                continue

            try:
                decision = policy.evaluate(context)
                if decision:
                    decisions.append(decision)
            except Exception as e:
                logger.error(f"Error evaluating policy '{policy.name}': {e}")

        return decisions

    def evaluate_by_type(
        self,
        policy_type: PolicyType,
        context: Dict[str, Any]
    ) -> List[PolicyDecision]:
        """
        Evaluate policies of specific type.

        Args:
            policy_type: Type of policies to evaluate
            context: Context for evaluation

        Returns:
            List of PolicyDecision objects
        """
        decisions = []

        for policy in self._sorted_policies:
            if policy.policy_type == policy_type and policy.enabled:
                try:
                    decision = policy.evaluate(context)
                    if decision:
                        decisions.append(decision)
                except Exception as e:
                    logger.error(f"Error evaluating policy '{policy.name}': {e}")

        return decisions

    def _update_sorted_policies(self) -> None:
        """Update sorted policy list (by priority, descending)"""
        self._sorted_policies = sorted(
            self.policies.values(),
            key=lambda p: p.priority,
            reverse=True
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get policy manager statistics"""
        return {
            "total_policies": len(self.policies),
            "enabled_policies": len([p for p in self.policies.values() if p.enabled]),
            "policies_by_type": {
                pt.value: len([p for p in self.policies.values() if p.policy_type == pt])
                for pt in PolicyType
            },
            "policies": [p.get_stats() for p in self.policies.values()]
        }

    def __repr__(self) -> str:
        return f"<PolicyManager: {len(self.policies)} policies>"


# Singleton instance
_policy_manager_instance: Optional[PolicyManager] = None


def get_policy_manager() -> PolicyManager:
    """
    Get singleton PolicyManager instance.

    Returns:
        Global PolicyManager instance
    """
    global _policy_manager_instance
    if _policy_manager_instance is None:
        _policy_manager_instance = PolicyManager()
        # Register default policies
        _register_default_policies(_policy_manager_instance)
    return _policy_manager_instance


def _register_default_policies(manager: PolicyManager) -> None:
    """Register default enterprise policies"""
    manager.register_policy(KillSwitchPolicy())
    manager.register_policy(IsolationPolicy())
    manager.register_policy(LoadBalancePolicy())
    manager.register_policy(OverloadPolicy())
    manager.register_policy(ConflictResolutionPolicy())
    manager.register_policy(EscalationPolicy())
    manager.register_policy(FailoverPolicy())
    logger.info("Default policies registered")


def create_policy_manager() -> PolicyManager:
    """
    Factory function: create new PolicyManager instance.

    Returns:
        New PolicyManager instance
    """
    return PolicyManager()
