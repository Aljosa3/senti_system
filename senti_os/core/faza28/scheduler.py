"""
FAZA 28 – Agent Execution Loop (AEL)
Scheduler

Agent scheduling and selection logic.
Determines which agents to run in each loop iteration.
"""

import logging
from typing import List, Optional, Dict, Any
from .agent_base import AgentBase

logger = logging.getLogger(__name__)


class Scheduler:
    """
    Agent scheduler for AEL.

    Scheduling strategies:
    - Priority-based: Higher priority agents run more frequently
    - Round-robin: Fair scheduling across all agents
    - Load-aware: Consider agent execution time and load

    TODO: Add time-based scheduling (cron-like)
    TODO: Add conditional scheduling (event-triggered)
    TODO: Add agent throttling/rate limiting
    TODO: Add agent dependency scheduling
    """

    def __init__(self, strategy: str = "priority"):
        """
        Initialize scheduler.

        Args:
            strategy: Scheduling strategy ('priority', 'round_robin', 'load_aware')
        """
        self.strategy = strategy
        self._round_robin_index = 0
        self._execution_counts: Dict[str, int] = {}
        self._last_execution_times: Dict[str, float] = {}
        logger.info(f"Scheduler initialized with strategy: {strategy}")

    def select_agents(self, agents: List[AgentBase], max_agents: Optional[int] = None) -> List[AgentBase]:
        """
        Select agents to run in this iteration.

        Args:
            agents: List of available agents
            max_agents: Maximum number of agents to select (None = all)

        Returns:
            List of selected agents

        TODO: Add adaptive selection based on system load
        TODO: Add agent cooldown periods
        TODO: Consider agent execution history
        """
        if not agents:
            return []

        # Filter enabled agents only
        enabled_agents = [a for a in agents if a.enabled]

        if not enabled_agents:
            return []

        # Apply scheduling strategy
        if self.strategy == "priority":
            selected = self._select_by_priority(enabled_agents, max_agents)
        elif self.strategy == "round_robin":
            selected = self._select_round_robin(enabled_agents, max_agents)
        elif self.strategy == "load_aware":
            selected = self._select_load_aware(enabled_agents, max_agents)
        else:
            logger.warning(f"Unknown strategy '{self.strategy}', using priority")
            selected = self._select_by_priority(enabled_agents, max_agents)

        return selected

    def _select_by_priority(self, agents: List[AgentBase], max_agents: Optional[int]) -> List[AgentBase]:
        """
        Select agents by priority (highest first).

        Args:
            agents: List of enabled agents
            max_agents: Maximum number to select

        Returns:
            Selected agents
        """
        # Sort by priority (descending)
        sorted_agents = sorted(agents, key=lambda a: a.priority, reverse=True)

        # Limit selection
        if max_agents:
            return sorted_agents[:max_agents]
        return sorted_agents

    def _select_round_robin(self, agents: List[AgentBase], max_agents: Optional[int]) -> List[AgentBase]:
        """
        Select agents using round-robin.

        Args:
            agents: List of enabled agents
            max_agents: Maximum number to select

        Returns:
            Selected agents
        """
        if not agents:
            return []

        # Determine how many to select
        count = min(max_agents, len(agents)) if max_agents else len(agents)

        # Select agents starting from round_robin_index
        selected = []
        for i in range(count):
            idx = (self._round_robin_index + i) % len(agents)
            selected.append(agents[idx])

        # Update index for next iteration
        self._round_robin_index = (self._round_robin_index + count) % len(agents)

        return selected

    def _select_load_aware(self, agents: List[AgentBase], max_agents: Optional[int]) -> List[AgentBase]:
        """
        Select agents considering execution load.

        Args:
            agents: List of enabled agents
            max_agents: Maximum number to select

        Returns:
            Selected agents

        TODO: Use actual execution time measurements
        TODO: Consider agent error rates
        TODO: Add dynamic priority adjustment
        """
        # For now, use priority-based with execution count balancing
        sorted_agents = sorted(
            agents,
            key=lambda a: (
                a.priority,  # Primary: priority
                -self._execution_counts.get(a.name, 0)  # Secondary: fewer executions first
            ),
            reverse=True
        )

        if max_agents:
            return sorted_agents[:max_agents]
        return sorted_agents

    def record_execution(self, agent_name: str, execution_time: float) -> None:
        """
        Record agent execution for scheduling decisions.

        Args:
            agent_name: Name of executed agent
            execution_time: Time taken to execute (seconds)

        TODO: Use execution time for load balancing
        TODO: Track execution patterns
        TODO: Emit execution_recorded event
        """
        self._execution_counts[agent_name] = self._execution_counts.get(agent_name, 0) + 1
        self._last_execution_times[agent_name] = execution_time

    def should_run_agent(self, agent: AgentBase, iteration: int) -> bool:
        """
        Determine if an agent should run in this iteration.

        Args:
            agent: Agent to check
            iteration: Current loop iteration number

        Returns:
            True if agent should run

        TODO: Add time-based conditions
        TODO: Add event-based conditions
        TODO: Add resource-based conditions
        """
        if not agent.enabled:
            return False

        # Priority-based throttling: higher priority = run more often
        # Priority 10: every iteration
        # Priority 5: every 2 iterations
        # Priority 1: every 10 iterations
        if agent.priority >= 10:
            return True
        elif agent.priority >= 7:
            return iteration % 2 == 0
        elif agent.priority >= 5:
            return iteration % 3 == 0
        elif agent.priority >= 3:
            return iteration % 5 == 0
        else:
            return iteration % 10 == 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get scheduler statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "strategy": self.strategy,
            "round_robin_index": self._round_robin_index,
            "total_executions": sum(self._execution_counts.values()),
            "execution_counts": dict(self._execution_counts),
            "last_execution_times": dict(self._last_execution_times)
        }

    def reset(self) -> None:
        """Reset scheduler state"""
        self._round_robin_index = 0
        self._execution_counts.clear()
        self._last_execution_times.clear()
        logger.debug("Scheduler state reset")

    def __repr__(self) -> str:
        return f"<Scheduler: {self.strategy}, {sum(self._execution_counts.values())} total executions>"


def create_scheduler(strategy: str = "priority") -> Scheduler:
    """
    Factory function: create new Scheduler instance.

    Args:
        strategy: Scheduling strategy

    Returns:
        New Scheduler instance
    """
    return Scheduler(strategy=strategy)
