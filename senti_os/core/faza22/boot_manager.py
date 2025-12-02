"""
FAZA 22 - Boot Manager

Main orchestrator for SENTI OS lifecycle management.

Responsibilities:
- Initialize all FAZA stacks in correct order
- Manage system start/stop/restart lifecycle
- Emit status events to FAZA 19 event bus
- Track stack health and dependencies
- Provide unified status reporting

Boot Order:
    FAZA 21 (Persistence) →
    FAZA 19 (UIL) →
    FAZA 20 (UX Layer) →
    FAZA 17 (Orchestration) →
    FAZA 16 (LLM Control) →
    FAZA 18 (Auth Flow)

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import traceback


class BootState(Enum):
    """Boot lifecycle states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class StackStatus(Enum):
    """Individual stack status."""
    NOT_LOADED = "not_loaded"
    LOADED = "loaded"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class StackInfo:
    """Information about a FAZA stack."""
    name: str
    status: StackStatus = StackStatus.NOT_LOADED
    instance: Optional[Any] = None
    error: Optional[str] = None
    initialized_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None


@dataclass
class BootEvent:
    """Boot lifecycle event."""
    event_type: str
    timestamp: datetime
    stack_name: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class BootManager:
    """
    Main boot orchestrator for SENTI OS.

    Manages the complete system lifecycle with proper dependency ordering
    and comprehensive status tracking.
    """

    # Boot order (must initialize in this sequence)
    BOOT_ORDER = [
        "faza21",  # Persistence Layer (foundation)
        "faza19",  # UIL & Multi-Device (communication)
        "faza20",  # UX Layer (observability)
        "faza17",  # Multi-Model Orchestration
        "faza16",  # LLM Control Layer
        "faza18",  # Auth Flow Handler
    ]

    def __init__(
        self,
        storage_dir: str = "/home/pisarna/senti_system/data/faza21",
        enable_persistence: bool = True,
        enable_uil: bool = True,
        enable_ux: bool = True,
        enable_orchestration: bool = True,
        enable_llm_control: bool = True,
        enable_auth_flow: bool = True,
    ):
        """
        Initialize Boot Manager.

        Args:
            storage_dir: Directory for FAZA 21 persistent storage.
            enable_persistence: Enable FAZA 21.
            enable_uil: Enable FAZA 19.
            enable_ux: Enable FAZA 20.
            enable_orchestration: Enable FAZA 17.
            enable_llm_control: Enable FAZA 16.
            enable_auth_flow: Enable FAZA 18.
        """
        self.storage_dir = storage_dir

        # Configuration
        self.enabled_stacks = {
            "faza21": enable_persistence,
            "faza19": enable_uil,
            "faza20": enable_ux,
            "faza17": enable_orchestration,
            "faza16": enable_llm_control,
            "faza18": enable_auth_flow,
        }

        # State
        self.state = BootState.UNINITIALIZED
        self.stacks: Dict[str, StackInfo] = {}
        self.boot_events: List[BootEvent] = []

        # Initialize stack info
        for stack_name in self.BOOT_ORDER:
            self.stacks[stack_name] = StackInfo(name=stack_name)

        # Timestamps
        self.boot_started_at: Optional[datetime] = None
        self.boot_completed_at: Optional[datetime] = None

    def _emit_event(
        self,
        event_type: str,
        stack_name: Optional[str] = None,
        status: Optional[str] = None,
        message: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Emit boot event.

        Args:
            event_type: Type of event.
            stack_name: Stack name if applicable.
            status: Status if applicable.
            message: Event message.
            error: Error message if applicable.
        """
        event = BootEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            stack_name=stack_name,
            status=status,
            message=message,
            error=error
        )
        self.boot_events.append(event)

        # Emit to FAZA 19 event bus if available
        faza19_stack = self.stacks.get("faza19")
        if (faza19_stack and
            faza19_stack.instance and
            hasattr(faza19_stack.instance, 'event_bus')):
            try:
                event_bus = faza19_stack.instance.event_bus
                event_bus.publish(
                    category="system",
                    event_type=f"boot.{event_type}",
                    data={
                        "stack_name": stack_name,
                        "status": status,
                        "message": message,
                        "error": error,
                        "timestamp": event.timestamp.isoformat()
                    }
                )
            except Exception:
                # Silently ignore event bus errors during boot
                pass

    def load_all_stacks(self) -> bool:
        """
        Load all FAZA stack classes.

        Returns:
            True if all enabled stacks loaded successfully.
        """
        self._emit_event("load_started", message="Loading FAZA stacks")

        success = True

        # Load FAZA 21 - Persistence Layer
        if self.enabled_stacks["faza21"]:
            try:
                from senti_os.core.faza21 import FAZA21Stack
                stack_info = self.stacks["faza21"]
                stack_info.instance = FAZA21Stack(storage_dir=self.storage_dir)
                stack_info.status = StackStatus.LOADED
                self._emit_event(
                    "stack_loaded",
                    stack_name="faza21",
                    status="loaded",
                    message="FAZA 21 Persistence Layer loaded"
                )
            except Exception as e:
                self.stacks["faza21"].status = StackStatus.ERROR
                self.stacks["faza21"].error = str(e)
                self._emit_event(
                    "stack_error",
                    stack_name="faza21",
                    status="error",
                    error=str(e)
                )
                success = False

        # Load FAZA 19 - UIL & Multi-Device
        if self.enabled_stacks["faza19"]:
            try:
                from senti_os.core.faza19 import FAZA19Stack
                stack_info = self.stacks["faza19"]
                stack_info.instance = FAZA19Stack()
                stack_info.status = StackStatus.LOADED
                self._emit_event(
                    "stack_loaded",
                    stack_name="faza19",
                    status="loaded",
                    message="FAZA 19 UIL loaded"
                )
            except Exception as e:
                self.stacks["faza19"].status = StackStatus.ERROR
                self.stacks["faza19"].error = str(e)
                self._emit_event(
                    "stack_error",
                    stack_name="faza19",
                    status="error",
                    error=str(e)
                )
                success = False

        # Load FAZA 20 - UX Layer
        if self.enabled_stacks["faza20"]:
            try:
                from senti_os.core.faza20 import FAZA20Stack

                # Get references to other stacks for integration
                faza16 = self.stacks["faza16"].instance if self.enabled_stacks["faza16"] else None
                faza17 = self.stacks["faza17"].instance if self.enabled_stacks["faza17"] else None
                faza18 = self.stacks["faza18"].instance if self.enabled_stacks["faza18"] else None
                faza19 = self.stacks["faza19"].instance if self.enabled_stacks["faza19"] else None
                faza21 = self.stacks["faza21"].instance if self.enabled_stacks["faza21"] else None

                stack_info = self.stacks["faza20"]
                stack_info.instance = FAZA20Stack(
                    faza16_llm_control=faza16,
                    faza17_orchestration=faza17,
                    faza18_auth_flow=faza18,
                    faza19_uil=faza19,
                    faza21_persistence=faza21
                )
                stack_info.status = StackStatus.LOADED
                self._emit_event(
                    "stack_loaded",
                    stack_name="faza20",
                    status="loaded",
                    message="FAZA 20 UX Layer loaded"
                )
            except Exception as e:
                self.stacks["faza20"].status = StackStatus.ERROR
                self.stacks["faza20"].error = str(e)
                self._emit_event(
                    "stack_error",
                    stack_name="faza20",
                    status="error",
                    error=str(e)
                )
                success = False

        # Load FAZA 17 - Multi-Model Orchestration
        if self.enabled_stacks["faza17"]:
            try:
                from senti_os.core.faza17 import create_orchestration_manager
                stack_info = self.stacks["faza17"]
                stack_info.instance = create_orchestration_manager()
                stack_info.status = StackStatus.LOADED
                self._emit_event(
                    "stack_loaded",
                    stack_name="faza17",
                    status="loaded",
                    message="FAZA 17 Orchestration loaded"
                )
            except Exception as e:
                self.stacks["faza17"].status = StackStatus.ERROR
                self.stacks["faza17"].error = str(e)
                self._emit_event(
                    "stack_error",
                    stack_name="faza17",
                    status="error",
                    error=str(e)
                )
                success = False

        # Load FAZA 16 - LLM Control Layer
        if self.enabled_stacks["faza16"]:
            try:
                from senti_os.core.faza16 import create_manager
                stack_info = self.stacks["faza16"]
                stack_info.instance = create_manager()
                stack_info.status = StackStatus.LOADED
                self._emit_event(
                    "stack_loaded",
                    stack_name="faza16",
                    status="loaded",
                    message="FAZA 16 LLM Control loaded"
                )
            except Exception as e:
                self.stacks["faza16"].status = StackStatus.ERROR
                self.stacks["faza16"].error = str(e)
                self._emit_event(
                    "stack_error",
                    stack_name="faza16",
                    status="error",
                    error=str(e)
                )
                success = False

        # Load FAZA 18 - Auth Flow Handler
        # Note: FAZA 18 doesn't have a Stack class, it's a collection of utilities
        if self.enabled_stacks["faza18"]:
            try:
                # FAZA 18 is more of a utility collection, mark as loaded
                stack_info = self.stacks["faza18"]
                stack_info.status = StackStatus.LOADED
                self._emit_event(
                    "stack_loaded",
                    stack_name="faza18",
                    status="loaded",
                    message="FAZA 18 Auth Flow loaded"
                )
            except Exception as e:
                self.stacks["faza18"].status = StackStatus.ERROR
                self.stacks["faza18"].error = str(e)
                self._emit_event(
                    "stack_error",
                    stack_name="faza18",
                    status="error",
                    error=str(e)
                )
                success = False

        if success:
            self._emit_event("load_completed", message="All stacks loaded successfully")
        else:
            self._emit_event("load_failed", message="Some stacks failed to load")

        return success

    def start(self) -> bool:
        """
        Start SENTI OS.

        Initializes and starts all enabled FAZA stacks in correct order.

        Returns:
            True if system started successfully.
        """
        if self.state in [BootState.RUNNING, BootState.STARTING]:
            return False

        self.state = BootState.INITIALIZING
        self.boot_started_at = datetime.now()

        self._emit_event("boot_started", message="SENTI OS boot sequence initiated")

        # Load all stacks first
        if not self.load_all_stacks():
            self.state = BootState.ERROR
            self._emit_event("boot_failed", message="Failed to load stacks")
            return False

        # Initialize stacks in boot order
        for stack_name in self.BOOT_ORDER:
            if not self.enabled_stacks[stack_name]:
                continue

            stack_info = self.stacks[stack_name]
            if stack_info.status != StackStatus.LOADED:
                continue

            try:
                stack_info.status = StackStatus.INITIALIZING
                self._emit_event(
                    "stack_initializing",
                    stack_name=stack_name,
                    message=f"Initializing {stack_name}"
                )

                # Initialize based on stack type
                if stack_name == "faza21":
                    # Initialize persistence with no passphrase (simulated)
                    if hasattr(stack_info.instance, 'initialize'):
                        stack_info.instance.initialize(passphrase=None)

                elif stack_name == "faza19":
                    # FAZA 19 doesn't require explicit initialization
                    pass

                elif stack_name == "faza20":
                    # Initialize UX layer with module references
                    if hasattr(stack_info.instance, 'initialize'):
                        stack_info.instance.initialize()

                elif stack_name in ["faza16", "faza17"]:
                    # These don't have explicit initialize methods
                    pass

                elif stack_name == "faza18":
                    # FAZA 18 is utility collection, no initialization needed
                    pass

                stack_info.status = StackStatus.INITIALIZED
                stack_info.initialized_at = datetime.now()

                self._emit_event(
                    "stack_initialized",
                    stack_name=stack_name,
                    status="initialized",
                    message=f"{stack_name} initialized successfully"
                )

            except Exception as e:
                stack_info.status = StackStatus.ERROR
                stack_info.error = f"Initialization failed: {str(e)}"
                self.state = BootState.ERROR

                self._emit_event(
                    "stack_error",
                    stack_name=stack_name,
                    status="error",
                    error=str(e)
                )

                return False

        self.state = BootState.INITIALIZED

        # Start stacks that have start() methods
        self.state = BootState.STARTING
        self._emit_event("system_starting", message="Starting SENTI OS services")

        for stack_name in self.BOOT_ORDER:
            if not self.enabled_stacks[stack_name]:
                continue

            stack_info = self.stacks[stack_name]
            if stack_info.status != StackStatus.INITIALIZED:
                continue

            try:
                stack_info.status = StackStatus.STARTING

                # Start services that support it
                if hasattr(stack_info.instance, 'start'):
                    stack_info.instance.start()

                stack_info.status = StackStatus.RUNNING
                stack_info.started_at = datetime.now()

                self._emit_event(
                    "stack_started",
                    stack_name=stack_name,
                    status="running",
                    message=f"{stack_name} started successfully"
                )

            except Exception as e:
                stack_info.status = StackStatus.ERROR
                stack_info.error = f"Start failed: {str(e)}"

                self._emit_event(
                    "stack_error",
                    stack_name=stack_name,
                    status="error",
                    error=str(e)
                )

                # Continue with other stacks

        self.state = BootState.RUNNING
        self.boot_completed_at = datetime.now()

        boot_time = (self.boot_completed_at - self.boot_started_at).total_seconds()

        self._emit_event(
            "boot_completed",
            message=f"SENTI OS boot completed in {boot_time:.2f}s"
        )

        return True

    def stop(self) -> bool:
        """
        Stop SENTI OS.

        Stops all running stacks in reverse order.

        Returns:
            True if system stopped successfully.
        """
        if self.state not in [BootState.RUNNING, BootState.INITIALIZED]:
            return False

        self.state = BootState.STOPPING
        self._emit_event("shutdown_started", message="SENTI OS shutdown initiated")

        # Stop in reverse boot order
        for stack_name in reversed(self.BOOT_ORDER):
            if not self.enabled_stacks[stack_name]:
                continue

            stack_info = self.stacks[stack_name]
            if stack_info.status not in [StackStatus.RUNNING, StackStatus.INITIALIZED]:
                continue

            try:
                stack_info.status = StackStatus.STOPPING

                # Stop services that support it
                if hasattr(stack_info.instance, 'stop'):
                    stack_info.instance.stop()

                # Shutdown services that support it
                if hasattr(stack_info.instance, 'shutdown'):
                    stack_info.instance.shutdown()

                stack_info.status = StackStatus.STOPPED
                stack_info.stopped_at = datetime.now()

                self._emit_event(
                    "stack_stopped",
                    stack_name=stack_name,
                    status="stopped",
                    message=f"{stack_name} stopped successfully"
                )

            except Exception as e:
                stack_info.error = f"Stop failed: {str(e)}"

                self._emit_event(
                    "stack_error",
                    stack_name=stack_name,
                    status="error",
                    error=str(e)
                )

                # Continue with other stacks

        self.state = BootState.STOPPED
        self._emit_event("shutdown_completed", message="SENTI OS shutdown completed")

        return True

    def restart(self) -> bool:
        """
        Restart SENTI OS.

        Returns:
            True if system restarted successfully.
        """
        self._emit_event("restart_initiated", message="SENTI OS restart initiated")

        # Stop if running
        if self.state in [BootState.RUNNING, BootState.INITIALIZED]:
            if not self.stop():
                self._emit_event("restart_failed", message="Failed to stop system")
                return False

        # Start again
        if not self.start():
            self._emit_event("restart_failed", message="Failed to start system")
            return False

        self._emit_event("restart_completed", message="SENTI OS restart completed")
        return True

    def get_status(self) -> Dict[str, Any]:
        """
        Get complete system status.

        Returns:
            Dictionary with comprehensive system status.
        """
        return {
            "system": {
                "state": self.state.value,
                "boot_started_at": self.boot_started_at.isoformat() if self.boot_started_at else None,
                "boot_completed_at": self.boot_completed_at.isoformat() if self.boot_completed_at else None,
                "uptime_seconds": (
                    (datetime.now() - self.boot_completed_at).total_seconds()
                    if self.boot_completed_at and self.state == BootState.RUNNING
                    else None
                ),
            },
            "stacks": {
                stack_name: {
                    "status": stack_info.status.value,
                    "enabled": self.enabled_stacks[stack_name],
                    "error": stack_info.error,
                    "initialized_at": (
                        stack_info.initialized_at.isoformat()
                        if stack_info.initialized_at else None
                    ),
                    "started_at": (
                        stack_info.started_at.isoformat()
                        if stack_info.started_at else None
                    ),
                    "stopped_at": (
                        stack_info.stopped_at.isoformat()
                        if stack_info.stopped_at else None
                    ),
                }
                for stack_name, stack_info in self.stacks.items()
            },
            "health": {
                "total_stacks": len(self.stacks),
                "enabled_stacks": sum(1 for e in self.enabled_stacks.values() if e),
                "running_stacks": sum(
                    1 for s in self.stacks.values()
                    if s.status == StackStatus.RUNNING
                ),
                "error_stacks": sum(
                    1 for s in self.stacks.values()
                    if s.status == StackStatus.ERROR
                ),
            },
            "events": {
                "total": len(self.boot_events),
                "recent": [
                    {
                        "type": e.event_type,
                        "timestamp": e.timestamp.isoformat(),
                        "stack": e.stack_name,
                        "status": e.status,
                        "message": e.message,
                        "error": e.error,
                    }
                    for e in self.boot_events[-10:]
                ]
            }
        }

    def get_stack(self, stack_name: str) -> Optional[Any]:
        """
        Get a specific stack instance.

        Args:
            stack_name: Name of stack (e.g., "faza21").

        Returns:
            Stack instance or None if not loaded.
        """
        stack_info = self.stacks.get(stack_name)
        if stack_info:
            return stack_info.instance
        return None

    def is_running(self) -> bool:
        """Check if system is running."""
        return self.state == BootState.RUNNING

    def is_healthy(self) -> bool:
        """
        Check if system is healthy.

        Returns:
            True if all enabled stacks are running without errors.
        """
        if self.state != BootState.RUNNING:
            return False

        for stack_name, enabled in self.enabled_stacks.items():
            if not enabled:
                continue

            stack_info = self.stacks[stack_name]
            if stack_info.status in [StackStatus.ERROR, StackStatus.STOPPED]:
                return False

        return True
