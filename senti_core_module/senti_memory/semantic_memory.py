"""
Semantic Memory - FAZA 12
Location: senti_core_module/senti_memory/semantic_memory.py

Long-term consolidated knowledge storage.
- Structured fact storage
- Deduplication and merging
- Persistent via MemoryStore
"""

import threading
import re
from typing import Any, Dict, List, Optional
from datetime import datetime


class SemanticMemory:
    """
    Long-term memory for consolidated knowledge and facts.
    """

    def __init__(self, memory_store):
        """
        Initialize semantic memory.

        Args:
            memory_store: MemoryStore instance for persistence
        """
        self.store = memory_store
        self.lock = threading.Lock()

        # Load existing facts from storage
        self.facts = self.store.load_semantic_facts()

    # =====================================================
    # CORE OPERATIONS
    # =====================================================

    def save_fact(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """
        Save a fact to semantic memory.

        Args:
            key: Fact key/identifier
            value: Fact value
            metadata: Optional metadata (source, confidence, etc.)

        Returns:
            Success status
        """
        with self.lock:
            try:
                fact_entry = {
                    "value": value,
                    "updated_at": datetime.now().isoformat(),
                    "metadata": metadata or {}
                }

                # If fact already exists, merge metadata
                if key in self.facts:
                    existing_metadata = self.facts[key].get("metadata", {})
                    fact_entry["metadata"] = {**existing_metadata, **(metadata or {})}
                    fact_entry["created_at"] = self.facts[key].get("created_at")
                else:
                    fact_entry["created_at"] = datetime.now().isoformat()

                self.facts[key] = fact_entry

                # Persist to storage
                return self.store.save_semantic_facts(self.facts)
            except Exception as e:
                print(f"[SemanticMemory] Failed to save fact: {e}")
                return False

    def get_fact(self, key: str) -> Optional[Any]:
        """
        Retrieve a fact from semantic memory.

        Args:
            key: Fact key

        Returns:
            Fact value or None
        """
        with self.lock:
            if key in self.facts:
                return self.facts[key]["value"]
            return None

    def get_fact_with_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve fact with full metadata.

        Args:
            key: Fact key

        Returns:
            Complete fact entry or None
        """
        with self.lock:
            return self.facts.get(key)

    def fact_exists(self, key: str) -> bool:
        """
        Check if fact exists.

        Args:
            key: Fact key

        Returns:
            True if exists
        """
        with self.lock:
            return key in self.facts

    def delete_fact(self, key: str) -> bool:
        """
        Delete a fact.

        Args:
            key: Fact key

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if key in self.facts:
                del self.facts[key]
                self.store.save_semantic_facts(self.facts)
                return True
            return False

    # =====================================================
    # SEARCH & QUERY
    # =====================================================

    def search(self, pattern: str) -> Dict[str, Any]:
        """
        Search facts by key pattern (regex supported).

        Args:
            pattern: Search pattern (can be regex)

        Returns:
            Dictionary of matching facts
        """
        with self.lock:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
                results = {}

                for key, fact_entry in self.facts.items():
                    # Search in key
                    if regex.search(key):
                        results[key] = fact_entry["value"]
                        continue

                    # Search in value (if string)
                    if isinstance(fact_entry["value"], str):
                        if regex.search(fact_entry["value"]):
                            results[key] = fact_entry["value"]

                return results
            except Exception as e:
                print(f"[SemanticMemory] Search failed: {e}")
                return {}

    def get_all_keys(self) -> List[str]:
        """
        Get all fact keys.

        Returns:
            List of keys
        """
        with self.lock:
            return list(self.facts.keys())

    def get_facts_by_metadata(self, metadata_key: str, metadata_value: Any) -> Dict[str, Any]:
        """
        Find facts by metadata attribute.

        Args:
            metadata_key: Metadata field to search
            metadata_value: Value to match

        Returns:
            Dictionary of matching facts
        """
        with self.lock:
            results = {}

            for key, fact_entry in self.facts.items():
                metadata = fact_entry.get("metadata", {})
                if metadata.get(metadata_key) == metadata_value:
                    results[key] = fact_entry["value"]

            return results

    # =====================================================
    # BULK OPERATIONS
    # =====================================================

    def save_facts_batch(self, facts_dict: Dict[str, Any]) -> bool:
        """
        Save multiple facts at once.

        Args:
            facts_dict: Dictionary of key-value pairs

        Returns:
            Success status
        """
        with self.lock:
            try:
                timestamp = datetime.now().isoformat()

                for key, value in facts_dict.items():
                    fact_entry = {
                        "value": value,
                        "updated_at": timestamp,
                        "metadata": {}
                    }

                    if key in self.facts:
                        fact_entry["created_at"] = self.facts[key].get("created_at")
                    else:
                        fact_entry["created_at"] = timestamp

                    self.facts[key] = fact_entry

                return self.store.save_semantic_facts(self.facts)
            except Exception as e:
                print(f"[SemanticMemory] Batch save failed: {e}")
                return False

    def merge_facts(self, source_key: str, target_key: str, delete_source: bool = True) -> bool:
        """
        Merge two facts (combines metadata, keeps target value).

        Args:
            source_key: Source fact key
            target_key: Target fact key
            delete_source: Whether to delete source after merge

        Returns:
            Success status
        """
        with self.lock:
            if source_key not in self.facts or target_key not in self.facts:
                return False

            try:
                source_fact = self.facts[source_key]
                target_fact = self.facts[target_key]

                # Merge metadata
                merged_metadata = {
                    **source_fact.get("metadata", {}),
                    **target_fact.get("metadata", {})
                }

                target_fact["metadata"] = merged_metadata
                target_fact["updated_at"] = datetime.now().isoformat()

                if delete_source:
                    del self.facts[source_key]

                return self.store.save_semantic_facts(self.facts)
            except Exception as e:
                print(f"[SemanticMemory] Merge failed: {e}")
                return False

    # =====================================================
    # MANAGEMENT
    # =====================================================

    def clear(self) -> int:
        """
        Clear all semantic memory.

        Returns:
            Number of facts cleared
        """
        with self.lock:
            count = len(self.facts)
            self.facts = {}
            self.store.clear_semantic()
            return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get semantic memory statistics.

        Returns:
            Stats dictionary
        """
        with self.lock:
            if not self.facts:
                return {
                    "total_facts": 0,
                    "oldest_fact": None,
                    "newest_fact": None
                }

            timestamps = []
            for fact_entry in self.facts.values():
                if "created_at" in fact_entry:
                    timestamps.append(fact_entry["created_at"])

            return {
                "total_facts": len(self.facts),
                "oldest_fact": min(timestamps) if timestamps else None,
                "newest_fact": max(timestamps) if timestamps else None,
                "keys_sample": list(self.facts.keys())[:10]
            }

    def export_facts(self) -> Dict[str, Any]:
        """
        Export all facts (with metadata).

        Returns:
            Complete facts dictionary
        """
        with self.lock:
            return self.facts.copy()
