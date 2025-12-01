"""
Consolidation Service - FAZA 12
Location: senti_core_module/senti_memory/consolidation_service.py

Converts episodic memory to semantic memory.
- Summarizes episodic events
- Extracts key facts
- Stores in semantic memory
- Prunes old episodic data
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter


class ConsolidationService:
    """
    Service for consolidating episodic memory into semantic memory.
    Runs periodically via FAZA 6 or manual invocation.
    """

    def __init__(
        self,
        episodic_memory,
        semantic_memory,
        memory_events,
        logger=None
    ):
        """
        Initialize consolidation service.

        Args:
            episodic_memory: EpisodicMemory instance
            semantic_memory: SemanticMemory instance
            memory_events: MemoryEvents publisher
            logger: Optional logger
        """
        self.episodic = episodic_memory
        self.semantic = semantic_memory
        self.events = memory_events
        self.logger = logger

        self.last_consolidation = None

    # =====================================================
    # MAIN CONSOLIDATION
    # =====================================================

    def consolidate(self, min_events: int = 10) -> Dict[str, Any]:
        """
        Perform memory consolidation.

        Args:
            min_events: Minimum events needed to trigger consolidation

        Returns:
            Consolidation result dictionary
        """
        start_time = time.time()

        try:
            # Get episodic events
            events = self.episodic.get_events()

            if len(events) < min_events:
                self._log("info", f"Not enough events for consolidation ({len(events)} < {min_events})")
                return {
                    "status": "skipped",
                    "reason": "insufficient_events",
                    "event_count": len(events)
                }

            # Extract facts from events
            facts = self._extract_facts(events)

            # Save facts to semantic memory
            facts_saved = 0
            for key, value in facts.items():
                if self.semantic.save_fact(key, value, metadata={"source": "consolidation"}):
                    facts_saved += 1

            # Prune old episodic events (keep last 50%)
            keep_count = len(events) // 2
            pruned_count = self.episodic.prune_old_events(keep_count=keep_count)

            duration_ms = (time.time() - start_time) * 1000

            # Publish event
            self.events.publish_memory_consolidated(
                episodic_count=len(events),
                semantic_count=facts_saved,
                duration_ms=duration_ms
            )

            self.last_consolidation = datetime.now().isoformat()

            self._log("info", f"Consolidation complete: {len(events)} events -> {facts_saved} facts (pruned {pruned_count})")

            return {
                "status": "success",
                "events_processed": len(events),
                "facts_created": facts_saved,
                "events_pruned": pruned_count,
                "duration_ms": duration_ms,
                "timestamp": self.last_consolidation
            }

        except Exception as e:
            error_msg = f"Consolidation failed: {e}"
            self._log("error", error_msg)
            self.events.publish_memory_error("consolidation", "consolidate", str(e))

            return {
                "status": "error",
                "error": str(e)
            }

    # =====================================================
    # FACT EXTRACTION
    # =====================================================

    def _extract_facts(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract semantic facts from episodic events.

        Args:
            events: List of episodic events

        Returns:
            Dictionary of facts
        """
        facts = {}

        # Event type frequency
        event_types = [e["event_type"] for e in events]
        type_counts = Counter(event_types)

        facts["event_type_frequency"] = dict(type_counts)
        facts["most_common_event_type"] = type_counts.most_common(1)[0][0] if type_counts else None

        # Time range
        if events:
            timestamps = [e["timestamp"] for e in events]
            facts["memory_time_range"] = {
                "start": min(timestamps),
                "end": max(timestamps)
            }

        # Extract patterns from event payloads
        pattern_facts = self._extract_patterns(events)
        facts.update(pattern_facts)

        # System activity summary
        activity_facts = self._summarize_activity(events)
        facts.update(activity_facts)

        return facts

    def _extract_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract patterns from event payloads.

        Args:
            events: List of events

        Returns:
            Dictionary of pattern facts
        """
        patterns = {}

        # Count specific event categories
        module_events = [e for e in events if "module" in str(e.get("payload", "")).lower()]
        error_events = [e for e in events if "error" in str(e.get("payload", "")).lower()]
        success_events = [e for e in events if "success" in str(e.get("payload", "")).lower()]

        if module_events:
            patterns["module_activity_count"] = len(module_events)

        if error_events:
            patterns["error_count"] = len(error_events)
            patterns["has_errors"] = True

        if success_events:
            patterns["success_count"] = len(success_events)

        return patterns

    def _summarize_activity(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize system activity from events.

        Args:
            events: List of events

        Returns:
            Dictionary of activity facts
        """
        activity = {}

        # Events per hour (rough estimate)
        if events:
            time_range = self._calculate_time_range(events)
            if time_range > 0:
                events_per_hour = len(events) / time_range
                activity["events_per_hour"] = round(events_per_hour, 2)

        # Recent activity burst detection
        recent_events = [
            e for e in events
            if self._is_recent(e["timestamp"], hours=1)
        ]

        if recent_events:
            activity["recent_activity_count"] = len(recent_events)
            activity["recent_activity_percentage"] = round(len(recent_events) / len(events) * 100, 2)

        return activity

    # =====================================================
    # UTILITY METHODS
    # =====================================================

    def _calculate_time_range(self, events: List[Dict[str, Any]]) -> float:
        """
        Calculate time range of events in hours.

        Args:
            events: List of events

        Returns:
            Time range in hours
        """
        if not events:
            return 0

        try:
            timestamps = [datetime.fromisoformat(e["timestamp"]) for e in events]
            time_diff = max(timestamps) - min(timestamps)
            return time_diff.total_seconds() / 3600
        except Exception:
            return 0

    def _is_recent(self, timestamp: str, hours: int = 1) -> bool:
        """
        Check if timestamp is within recent hours.

        Args:
            timestamp: ISO timestamp string
            hours: Hours threshold

        Returns:
            True if recent
        """
        try:
            event_time = datetime.fromisoformat(timestamp)
            cutoff = datetime.now() - timedelta(hours=hours)
            return event_time >= cutoff
        except Exception:
            return False

    def _log(self, level: str, message: str) -> None:
        """Log message if logger available."""
        if self.logger:
            getattr(self.logger, level, self.logger.info)(f"[ConsolidationService] {message}")
        else:
            print(f"[ConsolidationService][{level.upper()}] {message}")

    # =====================================================
    # MANUAL CONSOLIDATION OPTIONS
    # =====================================================

    def consolidate_by_type(self, event_type: str) -> Dict[str, Any]:
        """
        Consolidate specific event type.

        Args:
            event_type: Event type to consolidate

        Returns:
            Result dictionary
        """
        try:
            events = self.episodic.get_events(filter_type=event_type)

            if not events:
                return {
                    "status": "skipped",
                    "reason": "no_events_of_type",
                    "event_type": event_type
                }

            facts = self._extract_facts(events)

            # Prefix facts with event type
            prefixed_facts = {
                f"{event_type}_{key}": value
                for key, value in facts.items()
            }

            facts_saved = 0
            for key, value in prefixed_facts.items():
                if self.semantic.save_fact(key, value, metadata={"source": event_type}):
                    facts_saved += 1

            return {
                "status": "success",
                "event_type": event_type,
                "events_processed": len(events),
                "facts_created": facts_saved
            }

        except Exception as e:
            return {
                "status": "error",
                "event_type": event_type,
                "error": str(e)
            }

    def get_consolidation_stats(self) -> Dict[str, Any]:
        """
        Get consolidation service statistics.

        Returns:
            Stats dictionary
        """
        return {
            "last_consolidation": self.last_consolidation,
            "episodic_events": len(self.episodic.get_events()),
            "semantic_facts": len(self.semantic.get_all_keys())
        }
