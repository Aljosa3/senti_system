"""
Episodic Memory - FAZA 12
Location: senti_core_module/senti_memory/episodic_memory.py

Time-ordered event storage for system history.
- Chronologically organized events
- Category/type filtering
- Persistent storage via MemoryStore
"""

import threading
from typing import Any, Dict, List, Optional
from datetime import datetime


class EpisodicMemory:
    """
    Event-based chronological memory.
    Records system events in time order.
    """

    def __init__(self, memory_store):
        """
        Initialize episodic memory.

        Args:
            memory_store: MemoryStore instance for persistence
        """
        self.store = memory_store
        self.lock = threading.Lock()

        # Load existing events from storage
        self.events = self.store.load_episodic_events()

    # =====================================================
    # CORE OPERATIONS
    # =====================================================

    def record(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Record new event to episodic memory.

        Args:
            event_type: Type/category of event
            payload: Event data

        Returns:
            Success status
        """
        with self.lock:
            try:
                event = {
                    "event_type": event_type,
                    "timestamp": datetime.now().isoformat(),
                    "payload": payload
                }

                self.events.append(event)

                # Persist to storage
                return self.store.save_episodic_events(self.events)
            except Exception as e:
                print(f"[EpisodicMemory] Failed to record event: {e}")
                return False

    def get_events(
        self,
        since: Optional[str] = None,
        filter_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events with optional filters.

        Args:
            since: ISO timestamp - only return events after this time
            filter_type: Only return events of this type
            limit: Maximum number of events to return

        Returns:
            List of events (most recent first)
        """
        with self.lock:
            filtered_events = self.events.copy()

            # Filter by timestamp
            if since:
                try:
                    since_dt = datetime.fromisoformat(since)
                    filtered_events = [
                        e for e in filtered_events
                        if datetime.fromisoformat(e["timestamp"]) >= since_dt
                    ]
                except Exception as e:
                    print(f"[EpisodicMemory] Invalid since timestamp: {e}")

            # Filter by type
            if filter_type:
                filtered_events = [
                    e for e in filtered_events
                    if e["event_type"] == filter_type
                ]

            # Sort by timestamp (most recent first)
            filtered_events.sort(
                key=lambda e: e["timestamp"],
                reverse=True
            )

            # Apply limit
            if limit:
                filtered_events = filtered_events[:limit]

            return filtered_events

    def get_event_types(self) -> List[str]:
        """
        Get all unique event types.

        Returns:
            List of event type strings
        """
        with self.lock:
            types = set(e["event_type"] for e in self.events)
            return sorted(list(types))

    # =====================================================
    # MANAGEMENT OPERATIONS
    # =====================================================

    def prune_old_events(self, keep_count: int = 1000) -> int:
        """
        Remove oldest events, keeping only recent ones.

        Args:
            keep_count: Number of most recent events to keep

        Returns:
            Number of events removed
        """
        with self.lock:
            original_count = len(self.events)

            if original_count <= keep_count:
                return 0

            # Sort by timestamp (newest first)
            self.events.sort(
                key=lambda e: e["timestamp"],
                reverse=True
            )

            # Keep only the most recent
            self.events = self.events[:keep_count]

            # Persist
            self.store.save_episodic_events(self.events)

            return original_count - len(self.events)

    def prune_by_age(self, days: int) -> int:
        """
        Remove events older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of events removed
        """
        with self.lock:
            from datetime import timedelta

            cutoff_time = datetime.now() - timedelta(days=days)
            original_count = len(self.events)

            self.events = [
                e for e in self.events
                if datetime.fromisoformat(e["timestamp"]) >= cutoff_time
            ]

            # Persist
            self.store.save_episodic_events(self.events)

            return original_count - len(self.events)

    def clear(self) -> int:
        """
        Clear all episodic memory.

        Returns:
            Number of events cleared
        """
        with self.lock:
            count = len(self.events)
            self.events = []
            self.store.clear_episodic()
            return count

    def clear_by_type(self, event_type: str) -> int:
        """
        Clear all events of specific type.

        Args:
            event_type: Type to remove

        Returns:
            Number of events removed
        """
        with self.lock:
            original_count = len(self.events)

            self.events = [
                e for e in self.events
                if e["event_type"] != event_type
            ]

            # Persist
            self.store.save_episodic_events(self.events)

            return original_count - len(self.events)

    # =====================================================
    # QUERY & STATISTICS
    # =====================================================

    def get_stats(self) -> Dict[str, Any]:
        """
        Get episodic memory statistics.

        Returns:
            Stats dictionary
        """
        with self.lock:
            if not self.events:
                return {
                    "total_events": 0,
                    "event_types": 0,
                    "oldest_event": None,
                    "newest_event": None
                }

            type_counts = {}
            for event in self.events:
                event_type = event["event_type"]
                type_counts[event_type] = type_counts.get(event_type, 0) + 1

            timestamps = [e["timestamp"] for e in self.events]

            return {
                "total_events": len(self.events),
                "event_types": len(type_counts),
                "type_distribution": type_counts,
                "oldest_event": min(timestamps),
                "newest_event": max(timestamps)
            }

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search events by text in payload.

        Args:
            query: Search string

        Returns:
            Matching events
        """
        with self.lock:
            query_lower = query.lower()
            results = []

            for event in self.events:
                # Search in event_type
                if query_lower in event["event_type"].lower():
                    results.append(event)
                    continue

                # Search in payload (convert to string)
                payload_str = str(event["payload"]).lower()
                if query_lower in payload_str:
                    results.append(event)

            # Return most recent first
            results.sort(key=lambda e: e["timestamp"], reverse=True)
            return results
