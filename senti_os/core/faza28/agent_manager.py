"""
FAZA 28 – Agent Execution Loop (AEL)
Agent Manager

Manages agent registry, lifecycle, and coordination.
Provides central registry for all active agents.
"""

import logging
from typing import Dict, List, Optional, Any
from .agent_base import AgentBase

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Central registry and lifecycle manager for all agents.

    Responsibilities:
    - Agent registration and discovery
    - Agent lifecycle management (start, stop)
    - Agent priority and state tracking
    - Agent filtering and selection

    TODO: Add agent dependency resolution
    TODO: Add agent health monitoring
    TODO: Add agent restart policies
    """

    def __init__(self):
        """Initialize agent manager"""
        self.agents: Dict[str, AgentBase] = {}
        self._started = False
        logger.info("AgentManager initialized")

    def register(self, agent: AgentBase) -> None:
        """
        Register an agent instance.

        Args:
            agent: AgentBase instance to register

        Raises:
            ValueError: If agent name already exists

        TODO: Validate agent configuration
        TODO: Check for name conflicts
        TODO: Emit agent_registered event
        """
        if agent.name in self.agents:
            raise ValueError(f"Agent '{agent.name}' already registered")

        self.agents[agent.name] = agent
        logger.info(f"Agent registered: {agent.name} (priority={agent.priority}, enabled={agent.enabled})")

    def unregister(self, agent_name: str) -> None:
        """
        Unregister an agent by name.

        Args:
            agent_name: Name of agent to unregister

        TODO: Call agent shutdown before unregistering
        TODO: Emit agent_unregistered event
        """
        if agent_name in self.agents:
            agent = self.agents.pop(agent_name)
            logger.info(f"Agent unregistered: {agent_name}")
        else:
            logger.warning(f"Cannot unregister: agent '{agent_name}' not found")

    def get_agent(self, agent_name: str) -> Optional[AgentBase]:
        """
        Get agent by name.

        Args:
            agent_name: Name of agent

        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_name)

    def list_agents(self, enabled_only: bool = False) -> List[AgentBase]:
        """
        List all registered agents.

        Args:
            enabled_only: If True, only return enabled agents

        Returns:
            List of agent instances
        """
        agents = list(self.agents.values())

        if enabled_only:
            agents = [a for a in agents if a.enabled]

        return agents

    def get_agents_by_priority(self, enabled_only: bool = True) -> List[AgentBase]:
        """
        Get agents sorted by priority (highest first).

        Args:
            enabled_only: If True, only return enabled agents

        Returns:
            List of agents sorted by priority descending

        TODO: Add priority group batching
        TODO: Consider agent load balancing
        """
        agents = self.list_agents(enabled_only=enabled_only)
        return sorted(agents, key=lambda a: a.priority, reverse=True)

    async def start_all(self, context: Any) -> None:
        """
        Start all enabled agents.

        Args:
            context: StateContext instance

        TODO: Start agents in priority order
        TODO: Handle agent startup failures gracefully
        TODO: Emit system_started event
        """
        if self._started:
            logger.warning("AgentManager already started")
            return

        logger.info("Starting all agents...")
        started_count = 0

        for agent in self.get_agents_by_priority(enabled_only=True):
            try:
                await agent.on_start(context)
                started_count += 1
            except Exception as e:
                logger.error(f"Failed to start agent {agent.name}: {e}")
                await agent.on_error(e, context)

        self._started = True
        logger.info(f"AgentManager started: {started_count} agents active")

    async def shutdown_all(self, context: Any) -> None:
        """
        Shutdown all agents gracefully.

        Args:
            context: StateContext instance

        TODO: Shutdown in reverse priority order
        TODO: Add timeout for graceful shutdown
        TODO: Emit system_shutdown event
        """
        if not self._started:
            logger.warning("AgentManager not started")
            return

        logger.info("Shutting down all agents...")
        shutdown_count = 0

        # Shutdown in reverse priority order (lowest priority first)
        for agent in reversed(self.get_agents_by_priority(enabled_only=False)):
            try:
                await agent.on_shutdown(context)
                shutdown_count += 1
            except Exception as e:
                logger.error(f"Error during shutdown of agent {agent.name}: {e}")

        self._started = False
        logger.info(f"AgentManager shutdown complete: {shutdown_count} agents stopped")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent manager statistics.

        Returns:
            Dictionary with statistics
        """
        agents = self.list_agents()
        enabled_agents = [a for a in agents if a.enabled]

        return {
            "total_agents": len(agents),
            "enabled_agents": len(enabled_agents),
            "disabled_agents": len(agents) - len(enabled_agents),
            "started": self._started,
            "agents": [a.get_stats() for a in agents]
        }

    def __repr__(self) -> str:
        return f"<AgentManager: {len(self.agents)} agents, started={self._started}>"


# Singleton instance
_agent_manager_instance: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """
    Get singleton AgentManager instance.

    Returns:
        Global AgentManager instance
    """
    global _agent_manager_instance
    if _agent_manager_instance is None:
        _agent_manager_instance = AgentManager()
    return _agent_manager_instance


def create_agent_manager() -> AgentManager:
    """
    Factory function: create new AgentManager instance.

    Returns:
        New AgentManager instance
    """
    return AgentManager()
