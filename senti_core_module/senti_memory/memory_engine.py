"""
Memory Engine - FAZA 12
Location: senti_core_module/senti_memory/memory_engine.py

High-level memory API for AI agents and system components.
Unified interface for all memory operations.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class MemoryEngine:
    """
    High-level memory API.
    Used by AI Agents, Autonomous Task Loop, and FAZA 15.
    """

    def __init__(
        self,
        working_memory,
        episodic_memory,
        semantic_memory,
        consolidation_service,
        memory_rules,
        memory_events,
        logger=None
    ):
        """
        Initialize memory engine.

        Args:
            working_memory: WorkingMemory instance
            episodic_memory: EpisodicMemory instance
            semantic_memory: SemanticMemory instance
            consolidation_service: ConsolidationService instance
            memory_rules: MemoryRules instance
            memory_events: MemoryEvents publisher
            logger: Optional logger
        """
        self.working = working_memory
        self.episodic = episodic_memory
        self.semantic = semantic_memory
        self.consolidation = consolidation_service
        self.rules = memory_rules
        self.events = memory_events
        self.logger = logger

    # =====================================================
    # UNIFIED REMEMBER API
    # =====================================================

    def remember(
        self,
        data: Any,
        memory_type: str = "working",
        key: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        event_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Store data in memory (unified interface).

        Args:
            data: Data to remember
            memory_type: Type ("working", "episodic", "semantic")
            key: Key for working/semantic memory
            ttl_seconds: TTL for working memory
            event_type: Type for episodic memory
            metadata: Optional metadata

        Returns:
            Result dictionary
        """
        try:
            # Validate operation
            is_valid, error = self.rules.validate_memory_operation(
                action="add",
                memory_type=memory_type,
                key=key,
                data=data
            )

            if not is_valid:
                self._log("warning", f"Remember validation failed: {error}")
                return {"status": "error", "error": error}

            # Route to appropriate memory type
            if memory_type == "working":
                if not key:
                    key = f"auto_{datetime.now().timestamp()}"

                success = self.working.add(key, data, ttl_seconds)

                if success:
                    self.events.publish_memory_added("working", key)

                return {
                    "status": "success" if success else "error",
                    "memory_type": "working",
                    "key": key
                }

            elif memory_type == "episodic":
                if not event_type:
                    event_type = "general"

                success = self.episodic.record(event_type, data if isinstance(data, dict) else {"value": data})

                if success:
                    self.events.publish_memory_added("episodic", event_type)

                return {
                    "status": "success" if success else "error",
                    "memory_type": "episodic",
                    "event_type": event_type
                }

            elif memory_type == "semantic":
                if not key:
                    return {"status": "error", "error": "Key required for semantic memory"}

                success = self.semantic.save_fact(key, data, metadata)

                if success:
                    self.events.publish_memory_added("semantic", key)

                return {
                    "status": "success" if success else "error",
                    "memory_type": "semantic",
                    "key": key
                }

            else:
                return {"status": "error", "error": f"Unknown memory type: {memory_type}"}

        except Exception as e:
            self._log("error", f"Remember failed: {e}")
            self.events.publish_memory_error(memory_type, "remember", str(e))
            return {"status": "error", "error": str(e)}

    # =====================================================
    # UNIFIED RECALL API
    # =====================================================

    def recall(
        self,
        query: Any,
        memory_type: str = "working",
        event_type_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve data from memory (unified interface).

        Args:
            query: Query (key for working/semantic, search for episodic)
            memory_type: Type of memory to search
            event_type_filter: Filter for episodic memory
            limit: Limit results

        Returns:
            Result dictionary with data
        """
        try:
            if memory_type == "working":
                value = self.working.get(query)
                found = value is not None

                self.events.publish_memory_retrieved("working", str(query), found)

                return {
                    "status": "success",
                    "memory_type": "working",
                    "found": found,
                    "data": value
                }

            elif memory_type == "episodic":
                events = self.episodic.get_events(
                    filter_type=event_type_filter,
                    limit=limit
                )

                # Search events if query is string
                if isinstance(query, str) and query:
                    events = self.episodic.search(query)

                return {
                    "status": "success",
                    "memory_type": "episodic",
                    "found": len(events) > 0,
                    "count": len(events),
                    "data": events
                }

            elif memory_type == "semantic":
                if isinstance(query, str):
                    # Try exact match first
                    value = self.semantic.get_fact(query)

                    if value is not None:
                        self.events.publish_memory_retrieved("semantic", query, True)
                        return {
                            "status": "success",
                            "memory_type": "semantic",
                            "found": True,
                            "data": value
                        }

                    # Try pattern search
                    results = self.semantic.search(query)

                    return {
                        "status": "success",
                        "memory_type": "semantic",
                        "found": len(results) > 0,
                        "count": len(results),
                        "data": results
                    }

                return {"status": "error", "error": "Query must be string for semantic memory"}

            else:
                return {"status": "error", "error": f"Unknown memory type: {memory_type}"}

        except Exception as e:
            self._log("error", f"Recall failed: {e}")
            return {"status": "error", "error": str(e)}

    # =====================================================
    # CONSOLIDATION
    # =====================================================

    def consolidate(self, min_events: int = 10) -> Dict[str, Any]:
        """
        Trigger memory consolidation.

        Args:
            min_events: Minimum events needed

        Returns:
            Consolidation result
        """
        try:
            self._log("info", "Starting memory consolidation...")
            result = self.consolidation.consolidate(min_events=min_events)
            return result
        except Exception as e:
            self._log("error", f"Consolidation failed: {e}")
            return {"status": "error", "error": str(e)}

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup_working(self) -> Dict[str, Any]:
        """
        Clean up expired working memory items.

        Returns:
            Cleanup result
        """
        try:
            removed = self.working.cleanup_expired()

            if removed > 0:
                self.events.publish_memory_cleaned("working", removed, "expired")

            self._log("info", f"Working memory cleanup: {removed} items removed")

            return {
                "status": "success",
                "memory_type": "working",
                "items_removed": removed
            }
        except Exception as e:
            self._log("error", f"Cleanup failed: {e}")
            return {"status": "error", "error": str(e)}

    # =====================================================
    # STATISTICS & INSPECTION
    # =====================================================

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics.

        Returns:
            Stats dictionary
        """
        try:
            working_stats = self.working.get_stats()
            episodic_stats = self.episodic.get_stats()
            semantic_stats = self.semantic.get_stats()
            consolidation_stats = self.consolidation.get_consolidation_stats()

            # Publish stats event
            self.events.publish_memory_stats(
                working_items=working_stats.get("valid_items", 0),
                episodic_events=episodic_stats.get("total_events", 0),
                semantic_facts=semantic_stats.get("total_facts", 0)
            )

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "working_memory": working_stats,
                "episodic_memory": episodic_stats,
                "semantic_memory": semantic_stats,
                "consolidation": consolidation_stats
            }
        except Exception as e:
            self._log("error", f"Stats retrieval failed: {e}")
            return {"status": "error", "error": str(e)}

    def get_memory_health(self) -> Dict[str, Any]:
        """
        Get memory system health status.

        Returns:
            Health status dictionary
        """
        try:
            stats = self.get_memory_stats()

            if stats["status"] != "success":
                return {"status": "error", "health": "unknown"}

            working = stats["working_memory"]
            episodic = stats["episodic_memory"]
            semantic = stats["semantic_memory"]

            # Calculate health score
            issues = []

            # Check working memory expiration
            if working.get("expired_items", 0) > working.get("valid_items", 0):
                issues.append("high_expiration_rate")

            # Check episodic memory size
            if episodic.get("total_events", 0) > 10000:
                issues.append("episodic_needs_consolidation")

            # Check semantic memory size
            if semantic.get("total_facts", 0) > 5000:
                issues.append("semantic_memory_large")

            health = "healthy" if not issues else "needs_attention"

            return {
                "status": "success",
                "health": health,
                "issues": issues,
                "recommendations": self._get_recommendations(issues)
            }

        except Exception as e:
            self._log("error", f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}

    def _get_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []

        if "high_expiration_rate" in issues:
            recommendations.append("Run cleanup_working() to remove expired items")

        if "episodic_needs_consolidation" in issues:
            recommendations.append("Run consolidate() to move episodic events to semantic memory")

        if "semantic_memory_large" in issues:
            recommendations.append("Consider pruning old semantic facts")

        return recommendations

    # =====================================================
    # UTILITY
    # =====================================================

    def _log(self, level: str, message: str) -> None:
        """Log message if logger available."""
        if self.logger:
            getattr(self.logger, level, self.logger.info)(f"[MemoryEngine] {message}")
        else:
            print(f"[MemoryEngine][{level.upper()}] {message}")
