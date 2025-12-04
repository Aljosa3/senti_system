"""
FAZA 28 – Agent Execution Loop (AEL)
Main Loop Controller

Core execution loop orchestrating all agents.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import signal

from .agent_manager import AgentManager, get_agent_manager
from .event_bus import EventBus, Event, get_event_bus
from .scheduler import Scheduler, create_scheduler
from .state_context import StateContext, get_state_context

logger = logging.getLogger(__name__)


class AELController:
    """
    Agent Execution Loop Controller.

    Main orchestrator coordinating:
    - Agent lifecycle management
    - Event-driven agent execution
    - Scheduler-based agent selection
    - Shared state management
    - System-wide coordination

    TODO: Add performance monitoring
    TODO: Add adaptive tick rate
    TODO: Add agent isolation/sandboxing
    TODO: Add distributed execution support
    """

    def __init__(
        self,
        agent_manager: Optional[AgentManager] = None,
        event_bus: Optional[EventBus] = None,
        scheduler: Optional[Scheduler] = None,
        state_context: Optional[StateContext] = None,
        tick_rate: float = 1.0,
        strategy: str = "priority"
    ):
        """
        Initialize AEL Controller.

        Args:
            agent_manager: AgentManager instance (None = use singleton)
            event_bus: EventBus instance (None = use singleton)
            scheduler: Scheduler instance (None = create new)
            state_context: StateContext instance (None = use singleton)
            tick_rate: Loop iteration rate in seconds
            strategy: Scheduling strategy ('priority', 'round_robin', 'load_aware')
        """
        self.agent_manager = agent_manager or get_agent_manager()
        self.event_bus = event_bus or get_event_bus()
        self.scheduler = scheduler or create_scheduler(strategy=strategy)
        self.state_context = state_context or get_state_context()

        self.tick_rate = tick_rate
        self.strategy = strategy

        self._running = False
        self._iteration = 0
        self._start_time: Optional[datetime] = None
        self._shutdown_requested = False

        logger.info(f"AELController initialized (tick_rate={tick_rate}s, strategy={strategy})")

    async def start(self) -> None:
        """
        Start the Agent Execution Loop.

        Lifecycle:
        1. Initialize system
        2. Start all agents
        3. Enter main loop
        4. Handle shutdown gracefully

        TODO: Add health check system
        TODO: Add loop recovery on errors
        TODO: Emit system_started event
        """
        if self._running:
            logger.warning("AEL already running")
            return

        logger.info("Starting Agent Execution Loop...")
        self._running = True
        self._start_time = datetime.now()
        self._iteration = 0

        try:
            # Initialize state
            self.state_context.set("ael_status", "starting")
            self.state_context.set("ael_start_time", self._start_time.isoformat())

            # Start all agents
            await self.agent_manager.start_all(self.state_context)

            # Emit startup event
            self.event_bus.emit("ael_started", "ael_controller", data={
                "tick_rate": self.tick_rate,
                "strategy": self.strategy,
                "agent_count": len(self.agent_manager.list_agents(enabled_only=True))
            })

            self.state_context.set("ael_status", "running")

            # Main loop
            await self._main_loop()

        except Exception as e:
            logger.error(f"Fatal error in AEL: {e}", exc_info=True)
            self.state_context.set("ael_status", "error")
            raise
        finally:
            await self._shutdown()

    async def _main_loop(self) -> None:
        """
        Main execution loop.

        Each iteration:
        1. Select agents to run (via scheduler)
        2. Execute agent tick() methods
        3. Handle events
        4. Update state
        5. Check for shutdown

        TODO: Add iteration timeout
        TODO: Add performance metrics collection
        TODO: Add adaptive sleep timing
        """
        logger.info("Entering main loop...")

        while self._running and not self._shutdown_requested:
            self._iteration += 1
            iteration_start = asyncio.get_event_loop().time()

            try:
                # Update iteration state
                self.state_context.set("ael_iteration", self._iteration)
                self.state_context.set("ael_last_tick", datetime.now().isoformat())

                # Select agents to run
                agents = self.agent_manager.get_agents_by_priority(enabled_only=True)
                selected_agents = self.scheduler.select_agents(agents)

                logger.debug(f"Iteration {self._iteration}: {len(selected_agents)} agents selected")

                # Execute agent ticks
                for agent in selected_agents:
                    if not self.scheduler.should_run_agent(agent, self._iteration):
                        continue

                    try:
                        agent_start = asyncio.get_event_loop().time()
                        await agent.on_tick(self.state_context)
                        agent_duration = asyncio.get_event_loop().time() - agent_start

                        # Record execution
                        self.scheduler.record_execution(agent.name, agent_duration)

                    except Exception as e:
                        logger.error(f"Error in agent {agent.name} tick: {e}")
                        await agent.on_error(e, self.state_context)

                        # Emit error event
                        self.event_bus.emit("agent_error", "ael_controller", data={
                            "agent": agent.name,
                            "error": str(e),
                            "iteration": self._iteration
                        })

                # TODO: Process pending events from event_bus
                # TODO: Submit tasks to FAZA 25 orchestrator
                # TODO: Process FAZA 26 action commands
                # TODO: Send optimization reports to FAZA 27.5
                # TODO: Push telemetry to FAZA 24 dashboard

                # Calculate sleep time
                iteration_duration = asyncio.get_event_loop().time() - iteration_start
                sleep_time = max(0, self.tick_rate - iteration_duration)

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(f"Iteration took longer than tick_rate: {iteration_duration:.3f}s")

            except asyncio.CancelledError:
                logger.info("Loop cancelled, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop iteration {self._iteration}: {e}", exc_info=True)
                # Continue loop despite errors
                await asyncio.sleep(self.tick_rate)

        logger.info("Main loop exited")

    async def _shutdown(self) -> None:
        """
        Graceful shutdown.

        TODO: Add shutdown timeout
        TODO: Save state before shutdown
        TODO: Emit shutdown_complete event
        """
        if not self._running:
            return

        logger.info("Shutting down AEL...")
        self._running = False
        self.state_context.set("ael_status", "shutdown")

        # Shutdown all agents
        await self.agent_manager.shutdown_all(self.state_context)

        # Emit shutdown event
        self.event_bus.emit("ael_shutdown", "ael_controller", data={
            "total_iterations": self._iteration,
            "uptime_seconds": (datetime.now() - self._start_time).total_seconds() if self._start_time else 0
        })

        logger.info(f"AEL shutdown complete (ran {self._iteration} iterations)")

    async def stop(self) -> None:
        """
        Request graceful shutdown.

        Safe to call from signal handlers or external threads.
        """
        logger.info("Stop requested")
        self._shutdown_requested = True
        self._running = False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get AEL statistics.

        Returns:
            Dictionary with statistics
        """
        uptime = (datetime.now() - self._start_time).total_seconds() if self._start_time else 0

        return {
            "running": self._running,
            "iteration": self._iteration,
            "uptime_seconds": uptime,
            "tick_rate": self.tick_rate,
            "strategy": self.strategy,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "agent_manager": self.agent_manager.get_stats(),
            "event_bus": self.event_bus.get_stats(),
            "scheduler": self.scheduler.get_stats(),
            "state_context": self.state_context.get_stats()
        }

    def __repr__(self) -> str:
        return f"<AELController: running={self._running}, iteration={self._iteration}>"


# Singleton instance
_ael_controller_instance: Optional[AELController] = None


def get_ael_controller(
    tick_rate: float = 1.0,
    strategy: str = "priority"
) -> AELController:
    """
    Get singleton AELController instance.

    Args:
        tick_rate: Loop iteration rate (only used on first call)
        strategy: Scheduling strategy (only used on first call)

    Returns:
        Global AELController instance
    """
    global _ael_controller_instance
    if _ael_controller_instance is None:
        _ael_controller_instance = AELController(
            tick_rate=tick_rate,
            strategy=strategy
        )
    return _ael_controller_instance


def create_ael_controller(
    tick_rate: float = 1.0,
    strategy: str = "priority"
) -> AELController:
    """
    Factory function: create new AELController instance.

    Args:
        tick_rate: Loop iteration rate in seconds
        strategy: Scheduling strategy

    Returns:
        New AELController instance
    """
    return AELController(tick_rate=tick_rate, strategy=strategy)


async def run_ael_loop(
    tick_rate: float = 1.0,
    strategy: str = "priority"
) -> None:
    """
    Convenience function to run AEL with signal handlers.

    Args:
        tick_rate: Loop iteration rate in seconds
        strategy: Scheduling strategy

    TODO: Add configuration file support
    TODO: Add command-line argument parsing
    """
    controller = get_ael_controller(tick_rate=tick_rate, strategy=strategy)

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, requesting shutdown...")
        asyncio.create_task(controller.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the loop
    await controller.start()
