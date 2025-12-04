"""
FAZA 28 – Agent Execution Loop (AEL)

Agent-based execution system for Senti OS.

Provides:
- Agent lifecycle management
- Event-driven agent coordination
- Intelligent agent scheduling
- Shared state management
- Main execution loop orchestration

Architecture:
    AgentBase         - Base class for all agents
    AgentManager      - Agent registry and lifecycle
    EventBus          - Inter-agent event system
    Scheduler         - Agent selection logic
    StateContext      - Shared state management
    AELController     - Main loop orchestrator

Usage:
    from senti_os.core.faza28 import (
        AgentBase,
        get_ael_controller,
        get_agent_manager,
        get_event_bus,
        get_state_context
    )

    # Define custom agent
    class MyAgent(AgentBase):
        name = "my_agent"
        priority = 8

        async def on_tick(self, context):
            # Agent logic here
            context.set("my_state", "active")
            print(f"Agent {self.name} tick #{self.tick_count}")

    # Register agent
    manager = get_agent_manager()
    manager.register(MyAgent())

    # Start AEL
    controller = get_ael_controller(tick_rate=1.0, strategy="priority")
    await controller.start()

Integration Points:
    FAZA 25: Submit tasks via orchestrator
    FAZA 26: Execute action commands
    FAZA 27.5: Optimize task graphs
    FAZA 24: Push telemetry to dashboard
"""

# Agent Base
from senti_os.core.faza28.agent_base import AgentBase

# Agent Management
from senti_os.core.faza28.agent_manager import (
    AgentManager,
    get_agent_manager,
    create_agent_manager
)

# Event System
from senti_os.core.faza28.event_bus import (
    Event,
    EventBus,
    get_event_bus,
    create_event_bus
)

# Scheduler
from senti_os.core.faza28.scheduler import (
    Scheduler,
    create_scheduler
)

# State Management
from senti_os.core.faza28.state_context import (
    StateContext,
    get_state_context,
    create_state_context
)

# Main Loop
from senti_os.core.faza28.ael_loop import (
    AELController,
    get_ael_controller,
    create_ael_controller,
    run_ael_loop
)


__all__ = [
    # Agent Base
    "AgentBase",

    # Agent Management
    "AgentManager",
    "get_agent_manager",
    "create_agent_manager",

    # Event System
    "Event",
    "EventBus",
    "get_event_bus",
    "create_event_bus",

    # Scheduler
    "Scheduler",
    "create_scheduler",

    # State Management
    "StateContext",
    "get_state_context",
    "create_state_context",

    # Main Loop (primary API)
    "AELController",
    "get_ael_controller",
    "create_ael_controller",
    "run_ael_loop",
]


__version__ = "1.0.0"
__author__ = "Senti System"
__description__ = "FAZA 28 - Agent Execution Loop"
