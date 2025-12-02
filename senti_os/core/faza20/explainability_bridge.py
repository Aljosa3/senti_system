"""
FAZA 20 - Explainability Bridge

Merges explainability streams from FAZA 16 (LLM Control), FAZA 17 (Orchestration),
and FAZA 19 (Events) into normalized explainability output for UI.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import threading


class ExplainabilitySource(Enum):
    """Source of explainability data."""
    LLM_CONTROL = "llm_control"           # FAZA 16
    ORCHESTRATION = "orchestration"       # FAZA 17
    EVENT_BUS = "event_bus"              # FAZA 19
    SYSTEM = "system"                    # FAZA 20


class ExplainabilityLevel(Enum):
    """Level of explainability detail."""
    BASIC = "basic"           # High-level summary
    DETAILED = "detailed"     # Detailed explanation
    TECHNICAL = "technical"   # Technical details


@dataclass
class ExplainabilityEntry:
    """Single explainability entry."""
    entry_id: str
    source: ExplainabilitySource
    level: ExplainabilityLevel
    timestamp: datetime
    title: str
    description: str
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ExplainabilitySnapshot:
    """Complete explainability snapshot."""
    timestamp: datetime
    entries: List[ExplainabilityEntry]
    sources_active: List[ExplainabilitySource]
    entry_count: int
    metadata: Dict[str, Any]


class ExplainabilityBridge:
    """
    Unified explainability bridge for SENTI OS.

    Aggregates and normalizes explainability data from:
    - FAZA 16: LLM routing decisions
    - FAZA 17: Orchestration steps
    - FAZA 19: System events
    - FAZA 20: System operations

    Provides user-friendly explanations of system behavior.
    """

    def __init__(self, max_entries: int = 100):
        """
        Initialize explainability bridge.

        Args:
            max_entries: Maximum entries to keep in buffer.
        """
        self.max_entries = max_entries
        self._entries: List[ExplainabilityEntry] = []
        self._entry_counter = 0
        self._lock = threading.Lock()

        # Module references
        self._faza16_llm_control = None
        self._faza17_orchestration = None
        self._faza19_event_bus = None

        # Statistics
        self._entries_by_source: Dict[ExplainabilitySource, int] = {
            source: 0 for source in ExplainabilitySource
        }

    def register_modules(
        self,
        faza16_llm_control=None,
        faza17_orchestration=None,
        faza19_event_bus=None
    ):
        """
        Register module references for explainability collection.

        Args:
            faza16_llm_control: FAZA 16 LLM control layer.
            faza17_orchestration: FAZA 17 orchestration layer.
            faza19_event_bus: FAZA 19 event bus.
        """
        self._faza16_llm_control = faza16_llm_control
        self._faza17_orchestration = faza17_orchestration
        self._faza19_event_bus = faza19_event_bus

        # Subscribe to event bus if available
        if self._faza19_event_bus and hasattr(self._faza19_event_bus, 'subscribe'):
            # Subscribe to explainability-relevant categories
            for category in ["LLM_ROUTING", "ORCHESTRATION_STEP", "EXPLAINABILITY"]:
                try:
                    self._faza19_event_bus.subscribe(
                        category,
                        lambda event: self._handle_event_bus_entry(event)
                    )
                except Exception:
                    pass

    def add_entry(
        self,
        source: ExplainabilitySource,
        level: ExplainabilityLevel,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an explainability entry.

        Args:
            source: Source of explanation.
            level: Detail level.
            title: Entry title.
            description: Detailed description.
            metadata: Optional additional data.

        Returns:
            Entry ID.
        """
        with self._lock:
            self._entry_counter += 1
            entry_id = f"explain_{self._entry_counter}"

            entry = ExplainabilityEntry(
                entry_id=entry_id,
                source=source,
                level=level,
                timestamp=datetime.utcnow(),
                title=title,
                description=description,
                metadata=metadata or {}
            )

            self._entries.append(entry)
            self._entries_by_source[source] += 1

            # Keep only last max_entries
            if len(self._entries) > self.max_entries:
                removed = self._entries[0]
                self._entries = self._entries[-self.max_entries:]
                if removed.source in self._entries_by_source:
                    self._entries_by_source[removed.source] -= 1

            return entry_id

    def get_entries(
        self,
        source: Optional[ExplainabilitySource] = None,
        level: Optional[ExplainabilityLevel] = None,
        limit: int = 50
    ) -> List[ExplainabilityEntry]:
        """
        Get explainability entries with optional filtering.

        Args:
            source: Filter by source.
            level: Filter by detail level.
            limit: Maximum entries to return.

        Returns:
            List of ExplainabilityEntries.
        """
        with self._lock:
            filtered = self._entries.copy()

            if source is not None:
                filtered = [e for e in filtered if e.source == source]

            if level is not None:
                filtered = [e for e in filtered if e.level == level]

            # Return most recent first
            filtered.reverse()

            return filtered[:limit]

    def get_snapshot(self) -> ExplainabilitySnapshot:
        """
        Get complete explainability snapshot.

        Returns:
            ExplainabilitySnapshot with all current entries.
        """
        with self._lock:
            # Determine active sources
            active_sources = [
                source for source, count in self._entries_by_source.items()
                if count > 0
            ]

            return ExplainabilitySnapshot(
                timestamp=datetime.utcnow(),
                entries=self._entries.copy(),
                sources_active=active_sources,
                entry_count=len(self._entries),
                metadata={
                    "max_entries": self.max_entries,
                    "total_entries_created": self._entry_counter,
                    "entries_by_source": {
                        source.value: count
                        for source, count in self._entries_by_source.items()
                    }
                }
            )

    def get_recent_summary(self, count: int = 10) -> List[str]:
        """
        Get summary of recent explainability entries.

        Args:
            count: Number of recent entries to summarize.

        Returns:
            List of summary strings.
        """
        entries = self.get_entries(limit=count)
        return [
            f"[{e.source.value}] {e.title}"
            for e in entries
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get explainability statistics."""
        with self._lock:
            return {
                "total_entries": len(self._entries),
                "total_entries_created": self._entry_counter,
                "max_entries": self.max_entries,
                "entries_by_source": {
                    source.value: count
                    for source, count in self._entries_by_source.items()
                },
                "active_sources": [
                    source.value for source, count in self._entries_by_source.items()
                    if count > 0
                ]
            }

    def explain_llm_routing(
        self,
        task_description: str,
        selected_model: str,
        reasoning: str
    ):
        """
        Add LLM routing explanation from FAZA 16.

        Args:
            task_description: Description of task.
            selected_model: Model selected for task.
            reasoning: Why this model was selected.
        """
        self.add_entry(
            source=ExplainabilitySource.LLM_CONTROL,
            level=ExplainabilityLevel.DETAILED,
            title=f"LLM Routing: {selected_model}",
            description=f"Selected {selected_model} for '{task_description}'. {reasoning}",
            metadata={
                "task": task_description,
                "model": selected_model,
                "reasoning": reasoning
            }
        )

    def explain_orchestration_step(
        self,
        step_name: str,
        step_description: str,
        models_involved: List[str]
    ):
        """
        Add orchestration step explanation from FAZA 17.

        Args:
            step_name: Name of orchestration step.
            step_description: Description of what step does.
            models_involved: Models used in this step.
        """
        self.add_entry(
            source=ExplainabilitySource.ORCHESTRATION,
            level=ExplainabilityLevel.DETAILED,
            title=f"Orchestration: {step_name}",
            description=f"{step_description}. Models: {', '.join(models_involved)}",
            metadata={
                "step": step_name,
                "description": step_description,
                "models": models_involved
            }
        )

    def explain_system_operation(
        self,
        operation: str,
        description: str,
        level: ExplainabilityLevel = ExplainabilityLevel.BASIC
    ):
        """
        Add system operation explanation from FAZA 20.

        Args:
            operation: Operation name.
            description: What the system is doing.
            level: Detail level.
        """
        self.add_entry(
            source=ExplainabilitySource.SYSTEM,
            level=level,
            title=f"System: {operation}",
            description=description,
            metadata={"operation": operation}
        )

    def clear_entries(self, source: Optional[ExplainabilitySource] = None) -> int:
        """
        Clear explainability entries.

        Args:
            source: Optional source filter. If None, clear all.

        Returns:
            Number of entries cleared.
        """
        with self._lock:
            if source is None:
                count = len(self._entries)
                self._entries = []
                for src in ExplainabilitySource:
                    self._entries_by_source[src] = 0
                return count
            else:
                original_count = len(self._entries)
                self._entries = [e for e in self._entries if e.source != source]
                self._entries_by_source[source] = 0
                return original_count - len(self._entries)

    def _handle_event_bus_entry(self, event: Dict[str, Any]):
        """
        Handle explainability entry from event bus.

        Args:
            event: Event data from FAZA 19.
        """
        # Extract explainability info from event
        event_type = event.get("type", "unknown")
        category = event.get("category", "")

        if category == "LLM_ROUTING":
            self.add_entry(
                source=ExplainabilitySource.LLM_CONTROL,
                level=ExplainabilityLevel.BASIC,
                title=f"LLM Event: {event_type}",
                description=event.get("message", "LLM routing event"),
                metadata=event
            )
        elif category == "ORCHESTRATION_STEP":
            self.add_entry(
                source=ExplainabilitySource.ORCHESTRATION,
                level=ExplainabilityLevel.BASIC,
                title=f"Orchestration Event: {event_type}",
                description=event.get("message", "Orchestration step event"),
                metadata=event
            )
        elif category == "EXPLAINABILITY":
            self.add_entry(
                source=ExplainabilitySource.EVENT_BUS,
                level=ExplainabilityLevel.DETAILED,
                title=event.get("title", "System Event"),
                description=event.get("description", ""),
                metadata=event
            )


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "explainability_bridge",
        "faza": "20",
        "version": "1.0.0",
        "description": "Unified explainability aggregation from FAZA 16/17/19"
    }
