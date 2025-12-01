"""
Memory Manager - FAZA 12
Location: senti_core_module/senti_memory/memory_manager.py

Lifecycle manager for memory system.
- Initializes all memory components
- Registers as OS service
- Connects to EventBus
- Provides memory_engine to AI layer
"""

from pathlib import Path
from typing import Optional

from .memory_store import MemoryStore
from .working_memory import WorkingMemory
from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory
from .memory_rules import MemoryRules
from .memory_events import MemoryEvents
from .consolidation_service import ConsolidationService
from .memory_engine import MemoryEngine


class MemoryManager:
    """
    FAZA 12 Memory Manager.
    Orchestrates entire memory system lifecycle.
    """

    def __init__(
        self,
        project_root: Path,
        event_bus,
        logger=None,
        storage_subdir: str = "memory_data"
    ):
        """
        Initialize memory manager.

        Args:
            project_root: Project root directory
            event_bus: EventBus instance from Senti Core
            logger: Optional logger
            storage_subdir: Subdirectory for memory storage
        """
        self.project_root = Path(project_root)
        self.event_bus = event_bus
        self.logger = logger
        self.storage_dir = self.project_root / storage_subdir

        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Components (initialized in start())
        self.store = None
        self.working = None
        self.episodic = None
        self.semantic = None
        self.rules = None
        self.events = None
        self.consolidation = None
        self.engine = None

        self._initialized = False

        self._log("info", f"MemoryManager created (storage: {self.storage_dir})")

    # =====================================================
    # LIFECYCLE MANAGEMENT
    # =====================================================

    def start(self) -> dict:
        """
        Initialize and start memory system.

        Returns:
            Initialization result
        """
        try:
            self._log("info", "Initializing FAZA 12 Memory System...")

            # 1. Initialize storage layer
            self.store = MemoryStore(self.storage_dir)
            self._log("info", "Memory store initialized")

            # 2. Initialize memory layers
            self.working = WorkingMemory(default_ttl_seconds=180)
            self.episodic = EpisodicMemory(self.store)
            self.semantic = SemanticMemory(self.store)
            self._log("info", "Memory layers initialized (working, episodic, semantic)")

            # 3. Initialize security rules
            self.rules = MemoryRules(strict_mode=True)
            self._log("info", "Memory rules initialized (FAZA 8 integration)")

            # 4. Initialize event publisher
            self.events = MemoryEvents(self.event_bus)
            self._log("info", "Memory events connected to EventBus")

            # 5. Initialize consolidation service
            self.consolidation = ConsolidationService(
                episodic_memory=self.episodic,
                semantic_memory=self.semantic,
                memory_events=self.events,
                logger=self.logger
            )
            self._log("info", "Consolidation service initialized")

            # 6. Initialize memory engine (high-level API)
            self.engine = MemoryEngine(
                working_memory=self.working,
                episodic_memory=self.episodic,
                semantic_memory=self.semantic,
                consolidation_service=self.consolidation,
                memory_rules=self.rules,
                memory_events=self.events,
                logger=self.logger
            )
            self._log("info", "Memory engine initialized")

            self._initialized = True

            # Publish initialization event
            self.events.event_bus.publish("system.memory_initialized", {
                "status": "success",
                "storage_dir": str(self.storage_dir)
            })

            self._log("info", "FAZA 12 Memory System ready")

            return {
                "status": "success",
                "message": "Memory system initialized",
                "storage_dir": str(self.storage_dir)
            }

        except Exception as e:
            self._log("error", f"Memory system initialization failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def stop(self) -> dict:
        """
        Gracefully shutdown memory system.

        Returns:
            Shutdown result
        """
        try:
            self._log("info", "Shutting down memory system...")

            # Clear working memory (volatile)
            if self.working:
                cleared = self.working.clear()
                self._log("info", f"Working memory cleared ({cleared} items)")

            # Ensure all data is persisted
            if self.episodic and self.store:
                self.store.save_episodic_events(self.episodic.events)

            if self.semantic and self.store:
                self.store.save_semantic_facts(self.semantic.facts)

            self._log("info", "Memory data persisted")

            self._initialized = False

            return {
                "status": "success",
                "message": "Memory system shut down successfully"
            }

        except Exception as e:
            self._log("error", f"Memory system shutdown failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    # =====================================================
    # PUBLIC API
    # =====================================================

    def get_engine(self) -> Optional[MemoryEngine]:
        """
        Get memory engine instance.
        Used by AI layer and other components.

        Returns:
            MemoryEngine instance or None
        """
        if not self._initialized:
            self._log("warning", "Memory system not initialized")
            return None

        return self.engine

    def get_stats(self) -> dict:
        """
        Get memory system statistics.

        Returns:
            Stats dictionary
        """
        if not self._initialized:
            return {
                "status": "error",
                "error": "Memory system not initialized"
            }

        try:
            return self.engine.get_memory_stats()
        except Exception as e:
            self._log("error", f"Stats retrieval failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_health(self) -> dict:
        """
        Get memory system health.

        Returns:
            Health status dictionary
        """
        if not self._initialized:
            return {
                "status": "error",
                "health": "not_initialized"
            }

        try:
            return self.engine.get_memory_health()
        except Exception as e:
            self._log("error", f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    # =====================================================
    # MAINTENANCE OPERATIONS
    # =====================================================

    def perform_maintenance(self) -> dict:
        """
        Perform routine memory maintenance.
        Should be called periodically by Autonomous Task Loop.

        Returns:
            Maintenance result
        """
        if not self._initialized:
            return {
                "status": "error",
                "error": "Memory system not initialized"
            }

        try:
            self._log("info", "Starting memory maintenance...")

            results = {}

            # 1. Cleanup working memory
            cleanup_result = self.engine.cleanup_working()
            results["cleanup"] = cleanup_result

            # 2. Consolidate episodic to semantic
            consolidation_result = self.engine.consolidate(min_events=10)
            results["consolidation"] = consolidation_result

            # 3. Get health status
            health_result = self.engine.get_memory_health()
            results["health"] = health_result

            self._log("info", "Memory maintenance complete")

            return {
                "status": "success",
                "results": results
            }

        except Exception as e:
            self._log("error", f"Memory maintenance failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    # =====================================================
    # UTILITY
    # =====================================================

    def _log(self, level: str, message: str) -> None:
        """Log message if logger available."""
        if self.logger:
            getattr(self.logger, level, self.logger.info)(f"[MemoryManager] {message}")
        else:
            print(f"[MemoryManager][{level.upper()}] {message}")

    def is_initialized(self) -> bool:
        """Check if memory system is initialized."""
        return self._initialized

    def get_storage_stats(self) -> dict:
        """
        Get storage layer statistics.

        Returns:
            Storage stats dictionary
        """
        if not self.store:
            return {"status": "error", "error": "Store not initialized"}

        try:
            return {
                "status": "success",
                "stats": self.store.get_storage_stats()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
