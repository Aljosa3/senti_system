"""
FAZA 28 – Agent Execution Loop (AEL)
Agent Base Class

Base class for all FAZA 28 agents.
Defines lifecycle hooks and event handlers.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AgentBase:
    """
    Base class for all FAZA 28 agents.

    Lifecycle hooks:
    - on_start: Called when agent is registered or system boots
    - on_tick: Called each loop iteration
    - on_event: Called when agent receives an event
    - on_error: Called when an error occurs
    - on_shutdown: Called on system shutdown

    All agents must:
    1. Inherit from AgentBase
    2. Set unique 'name' attribute
    3. Override at least on_tick() method
    """

    name: str = "abstract_agent"
    priority: int = 5  # 0-10, higher = more important
    enabled: bool = True

    def __init__(self):
        """Initialize agent"""
        self.tick_count = 0
        self.error_count = 0
        self.metadata: dict = {}
        logger.info(f"Agent initialized: {self.name}")

    async def on_start(self, context: Any) -> None:
        """
        Called when agent is registered or system boots.

        Args:
            context: StateContext instance

        TODO: Load agent configuration
        TODO: Initialize agent-specific resources
        TODO: Emit startup event
        """
        logger.info(f"Agent starting: {self.name}")

    async def on_event(self, event: Any, context: Any) -> None:
        """
        Called when agent receives an event.

        Args:
            event: Event instance
            context: StateContext instance

        TODO: Implement event subscription filtering
        TODO: Add event priority handling
        TODO: Emit response events
        """
        logger.debug(f"Agent {self.name} received event: {event.type if hasattr(event, 'type') else 'unknown'}")

    async def on_tick(self, context: Any) -> None:
        """
        Called each loop iteration (main agent logic).

        Args:
            context: StateContext instance

        TODO: Implement agent-specific logic
        TODO: Update context/memory
        TODO: Submit tasks to FAZA 25
        TODO: Emit events to other agents
        """
        self.tick_count += 1
        logger.debug(f"Agent {self.name} tick #{self.tick_count}")

    async def on_error(self, error: Exception, context: Any) -> None:
        """
        Called when an error occurs during agent execution.

        Args:
            error: Exception that occurred
            context: StateContext instance

        TODO: Implement error recovery strategies
        TODO: Emit error events
        TODO: Update error metrics
        """
        self.error_count += 1
        logger.error(f"Agent {self.name} error #{self.error_count}: {error}")

    async def on_shutdown(self, context: Any) -> None:
        """
        Called on system shutdown.

        Args:
            context: StateContext instance

        TODO: Cleanup resources
        TODO: Save state
        TODO: Emit shutdown event
        """
        logger.info(f"Agent shutting down: {self.name} (ticks: {self.tick_count}, errors: {self.error_count})")

    def get_stats(self) -> dict:
        """Get agent statistics"""
        return {
            "name": self.name,
            "priority": self.priority,
            "enabled": self.enabled,
            "tick_count": self.tick_count,
            "error_count": self.error_count,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        return f"<Agent: {self.name} (priority={self.priority}, enabled={self.enabled})>"
