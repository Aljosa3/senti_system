"""
FAZA 30.9 – Event Hooks
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """FAZA 30.9 event types."""
    EXTRACTION_STARTED = "extraction_started"
    EXTRACTION_COMPLETED = "extraction_completed"
    GENERATION_STARTED = "generation_started"
    GENERATION_COMPLETED = "generation_completed"
    SANITIZATION_STARTED = "sanitization_started"
    SANITIZATION_COMPLETED = "sanitization_completed"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    VALIDATION_BLOCKED = "validation_blocked"
    PROMPT_BUILD_STARTED = "prompt_build_started"
    PROMPT_BUILD_COMPLETED = "prompt_build_completed"
    PLAN_BUILD_STARTED = "plan_build_started"
    PLAN_BUILD_COMPLETED = "plan_build_completed"
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Event:
    """Event data structure."""

    event_type: EventType
    timestamp: str
    data: Dict[str, Any]
    source: str = "faza30_9"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self.data
        }


class EventHooks:
    """
    Event hooks for FAZA 30.9 integration.

    Emits events to system EventBus for monitoring,
    logging, and integration with other phases.
    """

    def __init__(self) -> None:
        """Initialize event hooks."""
        self.event_bus: Optional[Any] = None
        self.event_handlers: Dict[EventType, list[Callable]] = {}
        self.events_emitted: list[Event] = []

    def set_event_bus(self, event_bus: Any) -> None:
        """
        Set EventBus instance.

        Args:
            event_bus: EventBus instance
        """
        self.event_bus = event_bus

    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[Event], None]
    ) -> None:
        """
        Register event handler.

        Args:
            event_type: Type of event
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)

    def emit_event(
        self,
        event_type: EventType,
        data: Dict[str, Any]
    ) -> None:
        """
        Emit event.

        Args:
            event_type: Type of event
            data: Event data
        """
        event = Event(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data
        )

        # Store event
        self.events_emitted.append(event)

        # Call registered handlers
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                # Don't let handler errors affect main flow
                pass

        # Emit to EventBus if available
        if self.event_bus is not None:
            try:
                self.event_bus.emit(
                    f"faza30_9.{event_type.value}",
                    event.to_dict()
                )
            except Exception:
                # Don't let EventBus errors affect main flow
                pass

    def on_extraction_started(self, input_text: str) -> None:
        """Emit extraction started event."""
        self.emit_event(
            EventType.EXTRACTION_STARTED,
            {"input_length": len(input_text)}
        )

    def on_extraction_completed(self, extracted_spec: Dict[str, Any]) -> None:
        """Emit extraction completed event."""
        self.emit_event(
            EventType.EXTRACTION_COMPLETED,
            {
                "requirements_count": len(extracted_spec.get("requirements", [])),
                "constraints_count": len(extracted_spec.get("constraints", []))
            }
        )

    def on_generation_started(self, component_name: str) -> None:
        """Emit generation started event."""
        self.emit_event(
            EventType.GENERATION_STARTED,
            {"component_name": component_name}
        )

    def on_generation_completed(self, spec: Dict[str, Any]) -> None:
        """Emit generation completed event."""
        self.emit_event(
            EventType.GENERATION_COMPLETED,
            {
                "component_name": spec.get("name", "unknown"),
                "api_count": len(spec.get("api_definitions", []))
            }
        )

    def on_sanitization_started(self) -> None:
        """Emit sanitization started event."""
        self.emit_event(EventType.SANITIZATION_STARTED, {})

    def on_sanitization_completed(self, redaction_count: int) -> None:
        """Emit sanitization completed event."""
        self.emit_event(
            EventType.SANITIZATION_COMPLETED,
            {"redaction_count": redaction_count}
        )

    def on_validation_started(self) -> None:
        """Emit validation started event."""
        self.emit_event(EventType.VALIDATION_STARTED, {})

    def on_validation_completed(
        self,
        result: str,
        errors: int,
        warnings: int
    ) -> None:
        """Emit validation completed event."""
        self.emit_event(
            EventType.VALIDATION_COMPLETED,
            {
                "result": result,
                "errors": errors,
                "warnings": warnings
            }
        )

    def on_validation_blocked(self, errors: list[str]) -> None:
        """Emit validation blocked event."""
        self.emit_event(
            EventType.VALIDATION_BLOCKED,
            {"errors": errors}
        )

    def on_prompt_build_started(self) -> None:
        """Emit prompt build started event."""
        self.emit_event(EventType.PROMPT_BUILD_STARTED, {})

    def on_prompt_build_completed(self, prompt_length: int) -> None:
        """Emit prompt build completed event."""
        self.emit_event(
            EventType.PROMPT_BUILD_COMPLETED,
            {"prompt_length": prompt_length}
        )

    def on_plan_build_started(self) -> None:
        """Emit plan build started event."""
        self.emit_event(EventType.PLAN_BUILD_STARTED, {})

    def on_plan_build_completed(self, plan: Dict[str, Any]) -> None:
        """Emit plan build completed event."""
        self.emit_event(
            EventType.PLAN_BUILD_COMPLETED,
            {
                "steps_count": len(
                    plan.get("compile_plan", {}).get("compilation_steps", [])
                )
            }
        )

    def on_pipeline_started(self, input_text: str) -> None:
        """Emit pipeline started event."""
        self.emit_event(
            EventType.PIPELINE_STARTED,
            {"input_length": len(input_text)}
        )

    def on_pipeline_completed(self, success: bool) -> None:
        """Emit pipeline completed event."""
        self.emit_event(
            EventType.PIPELINE_COMPLETED,
            {"success": success}
        )

    def on_pipeline_failed(self, stage: str, error: str) -> None:
        """Emit pipeline failed event."""
        self.emit_event(
            EventType.PIPELINE_FAILED,
            {"stage": stage, "error": error}
        )

    def on_error(self, stage: str, error: str) -> None:
        """Emit error event."""
        self.emit_event(
            EventType.ERROR_OCCURRED,
            {"stage": stage, "error": error}
        )

    def get_event_history(self) -> list[Event]:
        """Get event history."""
        return self.events_emitted.copy()

    def clear_event_history(self) -> None:
        """Clear event history."""
        self.events_emitted.clear()

    def get_event_summary(self) -> Dict[str, Any]:
        """Get event summary statistics."""
        summary: Dict[str, int] = {}

        for event in self.events_emitted:
            event_type = event.event_type.value
            summary[event_type] = summary.get(event_type, 0) + 1

        return {
            "total_events": len(self.events_emitted),
            "by_type": summary
        }


# Global event hooks instance
_event_hooks: Optional[EventHooks] = None


def get_event_hooks() -> EventHooks:
    """
    Get global event hooks instance.

    Returns:
        EventHooks singleton
    """
    global _event_hooks

    if _event_hooks is None:
        _event_hooks = EventHooks()

    return _event_hooks


def initialize_event_hooks(event_bus: Optional[Any] = None) -> EventHooks:
    """
    Initialize event hooks with EventBus.

    Args:
        event_bus: Optional EventBus instance

    Returns:
        EventHooks instance
    """
    hooks = get_event_hooks()

    if event_bus is not None:
        hooks.set_event_bus(event_bus)

    return hooks
