"""
FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise Edition)
Stability Engine

Enterprise stability detection and recovery:
- Detects multi-agent instability patterns
- Feedback loops
- Deadlocks
- Starvation
- Runaway agents
- Escalating load conditions

Provides recovery actions:
- Reset agent
- Redistribute tasks
- Throttle agent
- Isolate agent
- Escalate to meta-policy
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class StabilityIssue(Enum):
    """Types of stability issues"""
    FEEDBACK_LOOP = "feedback_loop"
    DEADLOCK = "deadlock"
    STARVATION = "starvation"
    RUNAWAY_AGENT = "runaway_agent"
    ESCALATING_LOAD = "escalating_load"
    THRASHING = "thrashing"
    CASCADE_FAILURE = "cascade_failure"


class RecoveryAction(Enum):
    """Recovery actions"""
    RESET_AGENT = "reset_agent"
    REDISTRIBUTE_TASKS = "redistribute_tasks"
    THROTTLE_AGENT = "throttle_agent"
    ISOLATE_AGENT = "isolate_agent"
    ESCALATE_POLICY = "escalate_policy"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"
    WAIT_AND_MONITOR = "wait_and_monitor"


@dataclass
class StabilityReport:
    """
    Stability analysis report.

    Attributes:
        issue_type: Type of stability issue
        severity: Severity score (0.0 - 1.0)
        affected_agents: List of affected agent names
        description: Human-readable description
        recommended_action: Recommended recovery action
        confidence: Detection confidence (0.0 - 1.0)
        timestamp: When issue was detected
        metadata: Additional issue data
    """
    issue_type: StabilityIssue
    severity: float
    affected_agents: List[str]
    description: str
    recommended_action: RecoveryAction
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"<StabilityReport: {self.issue_type.value} (severity={self.severity:.2f})>"


class StabilityEngine:
    """
    Enterprise stability detection and recovery engine.

    Monitors system-wide stability and detects:
    - Feedback loops between agents
    - Deadlock conditions
    - Agent starvation
    - Runaway agents
    - Escalating load patterns

    Recommends and can execute recovery actions.
    """

    def __init__(
        self,
        feedback_loop_threshold: int = 10,
        deadlock_timeout: float = 30.0,
        starvation_threshold: float = 60.0,
        runaway_tick_threshold: int = 1000,
        load_escalation_rate: float = 2.0,
        history_window: int = 300
    ):
        """
        Initialize stability engine.

        Args:
            feedback_loop_threshold: Max cycles before feedback loop detected
            deadlock_timeout: Time before deadlock suspected (seconds)
            starvation_threshold: Time before starvation detected (seconds)
            runaway_tick_threshold: Tick count for runaway detection
            load_escalation_rate: Rate multiplier for load escalation detection
            history_window: Time window for historical analysis (seconds)
        """
        self.feedback_loop_threshold = feedback_loop_threshold
        self.deadlock_timeout = deadlock_timeout
        self.starvation_threshold = starvation_threshold
        self.runaway_tick_threshold = runaway_tick_threshold
        self.load_escalation_rate = load_escalation_rate
        self.history_window = history_window

        # Tracking data
        self.agent_interactions: Dict[str, List[str]] = defaultdict(list)  # agent -> [interacted_with]
        self.agent_last_tick: Dict[str, datetime] = {}
        self.agent_tick_counts: Dict[str, List[int]] = defaultdict(list)  # time-series
        self.system_load_history: List[float] = []

        # Detected issues
        self.stability_reports: List[StabilityReport] = []
        self.max_report_history = 1000

        logger.info("StabilityEngine initialized")

    def analyze_stability(
        self,
        agent_metrics: Dict[str, Any],
        system_metrics: Dict[str, Any]
    ) -> List[StabilityReport]:
        """
        Analyze system stability.

        Args:
            agent_metrics: Dict of agent_name -> metrics
            system_metrics: System-wide metrics

        Returns:
            List of StabilityReport objects

        TODO: Add parallel analysis
        TODO: Add caching for repeated analysis
        """
        reports = []

        # Update tracking data
        self._update_tracking_data(agent_metrics, system_metrics)

        # Run stability checks
        reports.extend(self._detect_feedback_loops())
        reports.extend(self._detect_deadlocks(agent_metrics))
        reports.extend(self._detect_starvation(agent_metrics))
        reports.extend(self._detect_runaway_agents(agent_metrics))
        reports.extend(self._detect_escalating_load())
        reports.extend(self._detect_thrashing(agent_metrics))
        reports.extend(self._detect_cascade_failures(agent_metrics))

        # Store reports
        for report in reports:
            self.stability_reports.append(report)
            logger.warning(f"Stability issue detected: {report}")

        # Limit report history
        if len(self.stability_reports) > self.max_report_history:
            self.stability_reports = self.stability_reports[-self.max_report_history:]

        return reports

    def _detect_feedback_loops(self) -> List[StabilityReport]:
        """
        Detect feedback loops between agents.

        Feedback loop: A -> B -> C -> A (circular interaction)

        Returns:
            List of StabilityReport objects
        """
        reports = []

        # Build interaction graph
        visited = set()
        path = []

        def dfs(agent: str, start: str, depth: int = 0) -> Optional[List[str]]:
            """DFS to detect cycles"""
            if depth > self.feedback_loop_threshold:
                return None

            if agent == start and depth > 0:
                return path.copy()

            if agent in visited:
                return None

            visited.add(agent)
            path.append(agent)

            for next_agent in self.agent_interactions.get(agent, []):
                cycle = dfs(next_agent, start, depth + 1)
                if cycle:
                    return cycle

            path.pop()
            visited.remove(agent)
            return None

        # Check each agent for cycles
        for agent in self.agent_interactions.keys():
            visited.clear()
            path.clear()
            cycle = dfs(agent, agent)

            if cycle:
                severity = min(1.0, len(cycle) / 5.0)  # Longer cycles = more severe
                reports.append(StabilityReport(
                    issue_type=StabilityIssue.FEEDBACK_LOOP,
                    severity=severity,
                    affected_agents=cycle,
                    description=f"Feedback loop detected: {' -> '.join(cycle)}",
                    recommended_action=RecoveryAction.ISOLATE_AGENT,
                    confidence=0.9,
                    metadata={"cycle_length": len(cycle)}
                ))
                break  # Only report first cycle found

        return reports

    def _detect_deadlocks(self, agent_metrics: Dict[str, Any]) -> List[StabilityReport]:
        """
        Detect deadlock conditions.

        Deadlock: Multiple agents waiting for each other, no progress

        Args:
            agent_metrics: Agent metrics dictionary

        Returns:
            List of StabilityReport objects
        """
        reports = []

        now = datetime.now()
        potentially_deadlocked = []

        for agent_name, last_tick in self.agent_last_tick.items():
            time_since_tick = (now - last_tick).total_seconds()

            if time_since_tick > self.deadlock_timeout:
                potentially_deadlocked.append(agent_name)

        # If multiple agents haven't ticked in a while, suspect deadlock
        if len(potentially_deadlocked) >= 2:
            severity = min(1.0, len(potentially_deadlocked) / 5.0)
            reports.append(StabilityReport(
                issue_type=StabilityIssue.DEADLOCK,
                severity=severity,
                affected_agents=potentially_deadlocked,
                description=f"Potential deadlock: {len(potentially_deadlocked)} agents inactive",
                recommended_action=RecoveryAction.RESET_AGENT,
                confidence=0.7,
                metadata={"inactive_time": self.deadlock_timeout}
            ))

        return reports

    def _detect_starvation(self, agent_metrics: Dict[str, Any]) -> List[StabilityReport]:
        """
        Detect agent starvation.

        Starvation: Agent not getting execution time

        Args:
            agent_metrics: Agent metrics dictionary

        Returns:
            List of StabilityReport objects
        """
        reports = []

        now = datetime.now()

        for agent_name, last_tick in self.agent_last_tick.items():
            time_since_tick = (now - last_tick).total_seconds()

            if time_since_tick > self.starvation_threshold:
                severity = min(1.0, time_since_tick / self.starvation_threshold)
                reports.append(StabilityReport(
                    issue_type=StabilityIssue.STARVATION,
                    severity=severity,
                    affected_agents=[agent_name],
                    description=f"Agent starved: no ticks for {time_since_tick:.1f}s",
                    recommended_action=RecoveryAction.REDISTRIBUTE_TASKS,
                    confidence=0.8,
                    metadata={"starvation_time": time_since_tick}
                ))

        return reports

    def _detect_runaway_agents(self, agent_metrics: Dict[str, Any]) -> List[StabilityReport]:
        """
        Detect runaway agents.

        Runaway: Agent consuming excessive resources, too many ticks

        Args:
            agent_metrics: Agent metrics dictionary

        Returns:
            List of StabilityReport objects
        """
        reports = []

        for agent_name, metrics in agent_metrics.items():
            tick_count = metrics.get("tick_count", 0)

            # Check if agent has excessive tick count
            if tick_count > self.runaway_tick_threshold:
                # Check recent tick rate
                recent_ticks = self.agent_tick_counts.get(agent_name, [])
                if len(recent_ticks) >= 2:
                    recent_rate = recent_ticks[-1] - recent_ticks[-2]
                    if recent_rate > 100:  # More than 100 ticks since last check
                        severity = min(1.0, recent_rate / 500.0)
                        reports.append(StabilityReport(
                            issue_type=StabilityIssue.RUNAWAY_AGENT,
                            severity=severity,
                            affected_agents=[agent_name],
                            description=f"Runaway agent detected: {recent_rate} ticks in interval",
                            recommended_action=RecoveryAction.THROTTLE_AGENT,
                            confidence=0.9,
                            metadata={"tick_rate": recent_rate, "total_ticks": tick_count}
                        ))

        return reports

    def _detect_escalating_load(self) -> List[StabilityReport]:
        """
        Detect escalating system load.

        Escalating load: System load increasing exponentially

        Returns:
            List of StabilityReport objects
        """
        reports = []

        if len(self.system_load_history) < 3:
            return reports

        # Check if load is increasing rapidly
        recent = self.system_load_history[-3:]
        if recent[0] > 0:
            rate_1 = recent[1] / recent[0]
            rate_2 = recent[2] / recent[1] if recent[1] > 0 else 1.0

            # Escalating if both rates exceed threshold
            if rate_1 > self.load_escalation_rate and rate_2 > self.load_escalation_rate:
                severity = min(1.0, (rate_1 + rate_2) / (2 * self.load_escalation_rate))
                reports.append(StabilityReport(
                    issue_type=StabilityIssue.ESCALATING_LOAD,
                    severity=severity,
                    affected_agents=[],  # System-wide
                    description=f"System load escalating: {recent[0]:.1f} -> {recent[1]:.1f} -> {recent[2]:.1f}",
                    recommended_action=RecoveryAction.THROTTLE_AGENT,
                    confidence=0.8,
                    metadata={"load_history": recent, "rate_1": rate_1, "rate_2": rate_2}
                ))

        return reports

    def _detect_thrashing(self, agent_metrics: Dict[str, Any]) -> List[StabilityReport]:
        """
        Detect system thrashing.

        Thrashing: Excessive context switching, low productivity

        Args:
            agent_metrics: Agent metrics dictionary

        Returns:
            List of StabilityReport objects
        """
        reports = []

        # Count agents with very high tick counts but low productivity
        thrashing_agents = []

        for agent_name, metrics in agent_metrics.items():
            tick_count = metrics.get("tick_count", 0)
            # Assuming low productivity = high ticks but low state changes
            state_writes = metrics.get("state_writes", 0)

            if tick_count > 100 and state_writes < 10:
                thrashing_agents.append(agent_name)

        if len(thrashing_agents) >= 3:
            severity = min(1.0, len(thrashing_agents) / 10.0)
            reports.append(StabilityReport(
                issue_type=StabilityIssue.THRASHING,
                severity=severity,
                affected_agents=thrashing_agents,
                description=f"System thrashing detected: {len(thrashing_agents)} unproductive agents",
                recommended_action=RecoveryAction.THROTTLE_AGENT,
                confidence=0.6,
                metadata={"thrashing_agent_count": len(thrashing_agents)}
            ))

        return reports

    def _detect_cascade_failures(self, agent_metrics: Dict[str, Any]) -> List[StabilityReport]:
        """
        Detect cascade failures.

        Cascade: Multiple agents failing in sequence

        Args:
            agent_metrics: Agent metrics dictionary

        Returns:
            List of StabilityReport objects
        """
        reports = []

        # Count recent agent failures
        recent_failures = []
        cutoff = datetime.now() - timedelta(seconds=60)

        for report in self.stability_reports:
            if report.timestamp > cutoff and report.issue_type in [
                StabilityIssue.DEADLOCK,
                StabilityIssue.RUNAWAY_AGENT
            ]:
                recent_failures.extend(report.affected_agents)

        unique_failures = set(recent_failures)

        if len(unique_failures) >= 3:
            severity = min(1.0, len(unique_failures) / 5.0)
            reports.append(StabilityReport(
                issue_type=StabilityIssue.CASCADE_FAILURE,
                severity=severity,
                affected_agents=list(unique_failures),
                description=f"Cascade failure: {len(unique_failures)} agents affected in 60s",
                recommended_action=RecoveryAction.EMERGENCY_SHUTDOWN,
                confidence=0.7,
                metadata={"failure_count": len(unique_failures)}
            ))

        return reports

    def _update_tracking_data(
        self,
        agent_metrics: Dict[str, Any],
        system_metrics: Dict[str, Any]
    ) -> None:
        """
        Update internal tracking data.

        Args:
            agent_metrics: Agent metrics
            system_metrics: System metrics
        """
        now = datetime.now()

        # Update agent tick tracking
        for agent_name, metrics in agent_metrics.items():
            self.agent_last_tick[agent_name] = now
            tick_count = metrics.get("tick_count", 0)
            self.agent_tick_counts[agent_name].append(tick_count)

            # Limit history
            if len(self.agent_tick_counts[agent_name]) > 100:
                self.agent_tick_counts[agent_name] = self.agent_tick_counts[agent_name][-100:]

        # Update system load
        system_load = system_metrics.get("system_load", 0.0)
        self.system_load_history.append(system_load)

        # Limit history
        if len(self.system_load_history) > 100:
            self.system_load_history = self.system_load_history[-100:]

    def record_interaction(self, from_agent: str, to_agent: str) -> None:
        """
        Record interaction between agents.

        Args:
            from_agent: Source agent
            to_agent: Target agent
        """
        self.agent_interactions[from_agent].append(to_agent)

        # Limit interaction history
        if len(self.agent_interactions[from_agent]) > 100:
            self.agent_interactions[from_agent] = self.agent_interactions[from_agent][-100:]

    def execute_recovery(self, action: RecoveryAction, agent_names: List[str]) -> bool:
        """
        Execute recovery action.

        Args:
            action: Recovery action to execute
            agent_names: Affected agent names

        Returns:
            True if recovery succeeded

        TODO: Implement actual recovery actions
        TODO: Integrate with FAZA 28 agent_manager
        """
        logger.info(f"Executing recovery: {action.value} for agents: {agent_names}")

        # Placeholder for recovery logic
        # In production, this would:
        # - Call FAZA 28 agent_manager to reset/isolate/throttle agents
        # - Redistribute tasks via FAZA 25
        # - Apply policy changes via policy_manager

        return True

    def get_stability_summary(self) -> Dict[str, Any]:
        """
        Get stability summary.

        Returns:
            Dictionary with stability statistics
        """
        recent_reports = [
            r for r in self.stability_reports
            if (datetime.now() - r.timestamp).total_seconds() < self.history_window
        ]

        return {
            "total_issues": len(self.stability_reports),
            "recent_issues": len(recent_reports),
            "issues_by_type": {
                issue.value: len([r for r in recent_reports if r.issue_type == issue])
                for issue in StabilityIssue
            },
            "avg_severity": sum(r.severity for r in recent_reports) / max(1, len(recent_reports)),
            "critical_issues": len([r for r in recent_reports if r.severity > 0.8])
        }

    def clear_history(self) -> None:
        """Clear all tracking history"""
        self.agent_interactions.clear()
        self.agent_last_tick.clear()
        self.agent_tick_counts.clear()
        self.system_load_history.clear()
        self.stability_reports.clear()
        logger.info("Stability engine history cleared")

    def __repr__(self) -> str:
        return f"<StabilityEngine: {len(self.stability_reports)} total issues>"


# Singleton instance
_stability_engine_instance: Optional[StabilityEngine] = None


def get_stability_engine() -> StabilityEngine:
    """
    Get singleton StabilityEngine instance.

    Returns:
        Global StabilityEngine instance
    """
    global _stability_engine_instance
    if _stability_engine_instance is None:
        _stability_engine_instance = StabilityEngine()
    return _stability_engine_instance


def create_stability_engine(**kwargs) -> StabilityEngine:
    """
    Factory function: create new StabilityEngine instance.

    Args:
        **kwargs: Arguments passed to StabilityEngine constructor

    Returns:
        New StabilityEngine instance
    """
    return StabilityEngine(**kwargs)
