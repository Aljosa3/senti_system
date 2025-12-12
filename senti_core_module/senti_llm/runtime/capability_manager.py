"""
FAZA 44 — Capability Manager
-----------------------------
Upravlja z validacijo in injekcijo capabilities v module.

Funkcionalnosti:
- Validira capability requirements iz manifesta
- Kreira safe proxy objekte za capabilities
- Injicira capabilities v module instances
- FAZA 38: Integration z ModuleStorage za secure file operations
- FAZA 41: Event capabilities (event.publish, event.subscribe)
- FAZA 43: Task scheduling capabilities (task.schedule.*, task.cancel)
- FAZA 44: Async execution capabilities (async.schedule, async.await)
- FAZA D.1.1: Logging capabilities (log.basic, log.advanced)
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, TYPE_CHECKING
import time
import hashlib

from .capability_registry import CapabilityRegistry
from .module_storage import ModuleStorage
from .logging_manager import get_global_logging_manager

if TYPE_CHECKING:
    from .event_bus import EventBus
    from .scheduler import Scheduler
    from .async_exec import AsyncTaskManager


class CapabilityManager:
    """
    Manager za validacijo in injekcijo capabilities v module.
    """

    def __init__(self, context=None, module_name: Optional[str] = None, event_bus: Optional['EventBus'] = None, scheduler: Optional['Scheduler'] = None, async_manager: Optional['AsyncTaskManager'] = None):
        self.registry = CapabilityRegistry()
        self.context = context
        self.module_name = module_name
        self.event_bus = event_bus  # FAZA 41
        self.scheduler = scheduler  # FAZA 43
        self.async_manager = async_manager  # FAZA 44

    def validate_manifest_capabilities(self, manifest: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validira capabilities iz MODULE_MANIFEST.

        Manifest format:
        {
            "capabilities": {
                "requires": ["log.basic", "storage.read"],
                "optional": ["network"]
            }
        }

        Returns:
            (success: bool, message: str)
        """
        if "capabilities" not in manifest:
            # Capabilities niso zahtevani
            return True, "No capabilities requested."

        cap_spec = manifest["capabilities"]

        if not isinstance(cap_spec, dict):
            return False, "Capabilities must be a dict with 'requires' and/or 'optional' keys."

        # Validate 'requires' capabilities
        if "requires" in cap_spec:
            requires = cap_spec["requires"]
            success, msg = self.registry.validate_capability_list(requires)
            if not success:
                return False, f"Required capabilities validation failed: {msg}"

        # Validate 'optional' capabilities
        if "optional" in cap_spec:
            optional = cap_spec["optional"]
            success, msg = self.registry.validate_capability_list(optional)
            if not success:
                return False, f"Optional capabilities validation failed: {msg}"

        return True, "Capabilities validated successfully."

    def create_capability_map(
        self,
        manifest: Dict[str, Any],
        module_name: str,
        event_bus: Optional['EventBus'] = None,
        scheduler: Optional['Scheduler'] = None,
        async_manager: Optional['AsyncTaskManager'] = None
    ) -> Dict[str, Any]:
        """
        Kreira capability injection map iz manifesta.

        FAZA 38: Capabilities ki potrebujejo storage dobijo ModuleStorage instance.
        FAZA 41: Event capabilities dobijo EventBus instance.
        FAZA 43: Task scheduling capabilities dobijo Scheduler instance.
        FAZA 44: Async execution capabilities dobijo AsyncTaskManager instance.

        Args:
            manifest: Module manifest
            module_name: Name of module (for storage isolation)
            event_bus: EventBus instance (for event capabilities)
            scheduler: Scheduler instance (for task capabilities)
            async_manager: AsyncTaskManager instance (for async capabilities)

        Returns:
            Dict mapping capability name -> capability object
        """
        cap_map = {}

        # FAZA 38: Create ModuleStorage for this module if needed
        storage = None
        needs_storage = False

        if "capabilities" in manifest:
            cap_spec = manifest["capabilities"]
            all_caps = cap_spec.get("requires", []) + cap_spec.get("optional", [])
            if "storage.read" in all_caps or "storage.write" in all_caps:
                needs_storage = True

        if needs_storage:
            storage = ModuleStorage(module_name)

        # FAZA 41: Store event_bus for event capabilities
        if event_bus:
            self.event_bus = event_bus

        # FAZA 43: Store scheduler for task capabilities
        if scheduler:
            self.scheduler = scheduler

        # FAZA 44: Store async_manager for async capabilities
        if async_manager:
            self.async_manager = async_manager

        if "capabilities" not in manifest:
            # Add default module.run capability
            cap_map["module.run"] = self._create_capability_object("module.run", storage, module_name)
            return cap_map

        cap_spec = manifest["capabilities"]

        # Process required capabilities
        if "requires" in cap_spec:
            for cap_name in cap_spec["requires"]:
                cap_map[cap_name] = self._create_capability_object(cap_name, storage, module_name)

        # Process optional capabilities
        if "optional" in cap_spec:
            for cap_name in cap_spec["optional"]:
                if self.registry.has_capability(cap_name):
                    cap_map[cap_name] = self._create_capability_object(cap_name, storage, module_name)

        # Always add module.run if not present
        if "module.run" not in cap_map:
            cap_map["module.run"] = self._create_capability_object("module.run", storage, module_name)

        return cap_map

    def _create_capability_object(
        self,
        cap_name: str,
        storage: Optional[ModuleStorage] = None,
        module_name: Optional[str] = None
    ) -> Any:
        """
        Kreira safe proxy object za capability.

        FAZA 38: Storage capabilities receive ModuleStorage instance.
        FAZA 41: Event capabilities receive EventBus instance.

        Args:
            cap_name: Name of capability
            storage: ModuleStorage instance (for storage capabilities)
            module_name: Module name (for event capabilities)

        Returns:
            Capability object (safe proxy)
        """
        cap_def = self.registry.get_capability(cap_name)
        if not cap_def:
            return None

        # Create capability proxy based on type
        # FAZA D.1.1: Logging capabilities with LoggingManager
        if cap_name == "log.basic":
            return LogBasicCapability(module_name or "unknown")
        elif cap_name == "log.advanced":
            return LogAdvancedCapability(module_name or "unknown")
        elif cap_name == "storage.read":
            # FAZA 38: Use real storage
            if storage is None:
                raise ValueError("StorageReadCapability requires ModuleStorage instance")
            return StorageReadCapability(storage)
        elif cap_name == "storage.write":
            # FAZA 38: Use real storage
            if storage is None:
                raise ValueError("StorageWriteCapability requires ModuleStorage instance")
            return StorageWriteCapability(storage)
        elif cap_name == "network":
            return NetworkCapability()
        elif cap_name == "crypto":
            return CryptoCapability()
        elif cap_name == "time":
            return TimeCapability()
        elif cap_name == "module.run":
            return ModuleRunCapability()
        # FAZA 41: Event capabilities
        elif cap_name == "event.publish":
            if self.event_bus is None:
                raise ValueError("EventPublishCapability requires EventBus instance")
            return EventPublishCapability(self.event_bus, module_name or "unknown")
        elif cap_name == "event.subscribe":
            if self.event_bus is None:
                raise ValueError("EventSubscribeCapability requires EventBus instance")
            return EventSubscribeCapability(self.event_bus, module_name or "unknown")
        # FAZA 43: Task scheduling capabilities
        elif cap_name == "task.schedule.interval":
            if self.scheduler is None:
                raise ValueError("TaskScheduleIntervalCapability requires Scheduler instance")
            return TaskScheduleIntervalCapability(self.scheduler)
        elif cap_name == "task.schedule.oneshot":
            if self.scheduler is None:
                raise ValueError("TaskScheduleOneshotCapability requires Scheduler instance")
            return TaskScheduleOneshotCapability(self.scheduler)
        elif cap_name == "task.schedule.event":
            if self.scheduler is None:
                raise ValueError("TaskScheduleEventCapability requires Scheduler instance")
            return TaskScheduleEventCapability(self.scheduler)
        elif cap_name == "task.cancel":
            if self.scheduler is None:
                raise ValueError("TaskCancelCapability requires Scheduler instance")
            return TaskCancelCapability(self.scheduler)
        # FAZA 44: Async execution capabilities
        elif cap_name == "async.schedule":
            if self.async_manager is None:
                raise ValueError("AsyncScheduleCapability requires AsyncTaskManager instance")
            from .async_exec import AsyncScheduleCapability
            return AsyncScheduleCapability(self.async_manager)
        elif cap_name == "async.await":
            if self.async_manager is None:
                raise ValueError("AsyncAwaitCapability requires AsyncTaskManager instance")
            from .async_exec import AsyncAwaitCapability
            return AsyncAwaitCapability(self.async_manager)
        else:
            # Generic capability
            return GenericCapability(cap_name, cap_def)


# ================================================================
#  CAPABILITY PROXY IMPLEMENTATIONS
# ================================================================

class GenericCapability:
    """Generic capability proxy."""
    def __init__(self, name: str, definition: Dict):
        self.name = name
        self.definition = definition

    def __repr__(self):
        return f"<Capability:{self.name}>"


class LogBasicCapability:
    """
    FAZA D.1.1: Basic logging capability using LoggingManager.

    Provides single log() method that logs at INFO level.
    """
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._logging_manager = get_global_logging_manager()
        self._logger = self._logging_manager.get_logger(module_name, "FAZA 42")

    def log(self, message: str):
        """Log message at INFO level."""
        try:
            self._logger.info(message)
            # Also print for backwards compatibility
            print(f"[MODULE LOG] {message}")
        except Exception:
            # Never throw from logging
            pass

    def __repr__(self):
        return f"<Capability:log.basic module={self.module_name}>"


class LogAdvancedCapability:
    """
    FAZA D.1.1: Advanced logging capability using LoggingManager.

    Provides debug(), info(), warn(), error() methods.
    """
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._logging_manager = get_global_logging_manager()
        self._logger = self._logging_manager.get_logger(module_name, "FAZA 42")

    def debug(self, message: str, **metadata):
        """Log DEBUG level message."""
        try:
            self._logger.debug(message, **metadata)
        except Exception:
            pass

    def info(self, message: str, **metadata):
        """Log INFO level message."""
        try:
            self._logger.info(message, **metadata)
            # Also print for backwards compatibility
            print(f"[MODULE LOG] {message}")
        except Exception:
            pass

    def warn(self, message: str, **metadata):
        """Log WARN level message."""
        try:
            self._logger.warn(message, **metadata)
        except Exception:
            pass

    def error(self, message: str, **metadata):
        """Log ERROR level message."""
        try:
            self._logger.error(message, **metadata)
        except Exception:
            pass

    def log(self, message: str, **metadata):
        """Log at INFO level (alias for compatibility)."""
        self.info(message, **metadata)

    def __repr__(self):
        return f"<Capability:log.advanced module={self.module_name}>"


class StorageReadCapability:
    """
    FAZA 38: Storage read capability using ModuleStorage.

    Provides safe, sandboxed file operations.
    """
    def __init__(self, storage: ModuleStorage):
        self.storage = storage

    def read_text(self, path: str) -> str:
        """Read text file."""
        return self.storage.read_text(path)

    def read_json(self, path: str) -> Dict[str, Any]:
        """Read JSON file."""
        return self.storage.read_json(path)

    def exists(self, path: str) -> bool:
        """Check if file exists."""
        return self.storage.exists(path)

    def list_files(self, path: str = "") -> List[str]:
        """List files in directory."""
        return self.storage.list_files(path)

    def __repr__(self):
        return f"<Capability:storage.read module={self.storage.module_name}>"


class StorageWriteCapability(StorageReadCapability):
    """
    FAZA 38: Storage write capability using ModuleStorage.

    Inherits read operations from StorageReadCapability.
    Adds write operations.
    """
    def write_text(self, path: str, data: str) -> None:
        """Write text file (atomic)."""
        self.storage.write_text(path, data)

    def write_json(self, path: str, data: Dict[str, Any]) -> None:
        """Write JSON file (atomic)."""
        self.storage.write_json(path, data)

    def __repr__(self):
        return f"<Capability:storage.write module={self.storage.module_name}>"


class NetworkCapability:
    """Network capability (HTTP/HTTPS only)."""
    def request(self, url: str, method: str = "GET") -> Dict[str, Any]:
        # Mock implementation
        return {
            "status": 200,
            "data": f"[MOCK] Response from {url}",
            "method": method
        }

    def __repr__(self):
        return "<Capability:network>"


class CryptoCapability:
    """Cryptographic operations capability."""
    def hash_sha256(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def __repr__(self):
        return "<Capability:crypto>"


class TimeCapability:
    """Time and date operations capability."""
    def now(self) -> float:
        return time.time()

    def format(self, timestamp: float = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        import datetime
        ts = timestamp if timestamp else time.time()
        return datetime.datetime.fromtimestamp(ts).strftime(fmt)

    def __repr__(self):
        return "<Capability:time>"


class ModuleRunCapability:
    """Module execution permission capability."""
    def __init__(self):
        self.granted = True

    def __repr__(self):
        return "<Capability:module.run>"


# ================================================================
#  FAZA 41: EVENT CAPABILITY PROXIES
# ================================================================

class EventPublishCapability:
    """
    FAZA 41: Event publishing capability.

    Allows modules to publish events to the EventBus.
    """
    def __init__(self, event_bus: 'EventBus', module_name: str):
        self.event_bus = event_bus
        self.module_name = module_name

    def publish(self, event_type: str, payload: Dict[str, Any], category: str = "general", priority: int = 5):
        """
        Publish an event to the EventBus.

        Args:
            event_type: Event type identifier
            payload: Event data
            category: Event category (default: "general")
            priority: Event priority 1-10 (default: 5)

        Returns:
            List of handler results
        """
        from .event_context import EventContext

        context = EventContext(
            event_type=event_type,
            source=self.module_name,
            payload=payload,
            category=category,
            priority=priority
        )

        return self.event_bus.publish(event_type, context)

    def __repr__(self):
        return f"<Capability:event.publish module={self.module_name}>"


class EventSubscribeCapability:
    """
    FAZA 41: Event subscription capability.

    Allows modules to subscribe to events from the EventBus.
    """
    def __init__(self, event_bus: 'EventBus', module_name: str):
        self.event_bus = event_bus
        self.module_name = module_name
        self._subscriptions = []  # Track subscriptions for cleanup

    def subscribe(self, event_type: str, handler: callable):
        """
        Subscribe to an event type.

        Args:
            event_type: Event type to subscribe to
            handler: Callable that receives EventContext
        """
        self.event_bus.subscribe(event_type, handler)
        self._subscriptions.append((event_type, handler))

    def unsubscribe(self, event_type: str, handler: callable):
        """
        Unsubscribe from an event type.

        Args:
            event_type: Event type to unsubscribe from
            handler: Handler to remove
        """
        self.event_bus.unsubscribe(event_type, handler)
        if (event_type, handler) in self._subscriptions:
            self._subscriptions.remove((event_type, handler))

    def list_subscriptions(self) -> List[str]:
        """
        List all subscriptions made by this module.

        Returns:
            List of event types this module is subscribed to
        """
        return [event_type for event_type, _ in self._subscriptions]

    def __repr__(self):
        return f"<Capability:event.subscribe module={self.module_name}>"


# ================================================================
#  FAZA 43: TASK SCHEDULING CAPABILITY PROXIES
# ================================================================

class TaskScheduleIntervalCapability:
    """
    FAZA 43: Interval task scheduling capability.

    Allows modules to schedule repeating interval tasks.
    """
    def __init__(self, scheduler: 'Scheduler'):
        self.scheduler = scheduler

    def schedule(self, callable_fn: callable, interval: float, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Schedule a repeating interval task.

        Args:
            callable_fn: Function to execute
            interval: Interval in seconds
            metadata: Optional task metadata

        Returns:
            Task ID
        """
        try:
            return self.scheduler.schedule_interval(callable_fn, interval, metadata)
        except Exception:
            return ""

    def __repr__(self):
        return "<Capability:task.schedule.interval>"


class TaskScheduleOneshotCapability:
    """
    FAZA 43: Oneshot task scheduling capability.

    Allows modules to schedule one-time tasks after a delay.
    """
    def __init__(self, scheduler: 'Scheduler'):
        self.scheduler = scheduler

    def schedule(self, callable_fn: callable, delay: float, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Schedule a one-time task after delay.

        Args:
            callable_fn: Function to execute
            delay: Delay in seconds
            metadata: Optional task metadata

        Returns:
            Task ID
        """
        try:
            return self.scheduler.schedule_oneshot(callable_fn, delay, metadata)
        except Exception:
            return ""

    def __repr__(self):
        return "<Capability:task.schedule.oneshot>"


class TaskScheduleEventCapability:
    """
    FAZA 43: Event-triggered task scheduling capability.

    Allows modules to schedule event-triggered tasks.
    """
    def __init__(self, scheduler: 'Scheduler'):
        self.scheduler = scheduler

    def schedule(self, event_type: str, callable_fn: callable, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Schedule an event-triggered task.

        Args:
            event_type: Event type to listen for
            callable_fn: Function to execute (receives event_context)
            metadata: Optional task metadata

        Returns:
            Task ID
        """
        try:
            return self.scheduler.schedule_event(event_type, callable_fn, metadata)
        except Exception:
            return ""

    def __repr__(self):
        return "<Capability:task.schedule.event>"


class TaskCancelCapability:
    """
    FAZA 43: Task cancellation capability.

    Allows modules to cancel scheduled tasks.
    """
    def __init__(self, scheduler: 'Scheduler'):
        self.scheduler = scheduler

    def cancel(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if task was cancelled
        """
        try:
            return self.scheduler.cancel(task_id)
        except Exception:
            return False

    def __repr__(self):
        return "<Capability:task.cancel>"
