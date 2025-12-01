"""
FAZA 12 - Adaptive Memory Engine
Location: senti_core_module/senti_memory/

Three-layer memory system for Senti OS:
1. Working Memory - Short-term, volatile (TTL-based)
2. Episodic Memory - Event-based, chronological
3. Semantic Memory - Consolidated long-term knowledge

Usage:
    from senti_core_module.senti_memory import MemoryManager

    # Initialize
    manager = MemoryManager(project_root, event_bus, logger)
    manager.start()

    # Get engine for AI layer
    engine = manager.get_engine()

    # Use memory
    engine.remember({"key": "value"}, memory_type="semantic", key="my_fact")
    result = engine.recall("my_fact", memory_type="semantic")

    # Maintenance
    manager.perform_maintenance()
"""

__version__ = "1.0.0"
__author__ = "Senti OS Team"

# Public exports
from .memory_manager import MemoryManager
from .memory_engine import MemoryEngine
from .memory_store import MemoryStore
from .working_memory import WorkingMemory
from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory
from .memory_rules import MemoryRules
from .memory_events import MemoryEvents, MemoryEventListener
from .consolidation_service import ConsolidationService

__all__ = [
    "MemoryManager",
    "MemoryEngine",
    "MemoryStore",
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "MemoryRules",
    "MemoryEvents",
    "MemoryEventListener",
    "ConsolidationService",
]
