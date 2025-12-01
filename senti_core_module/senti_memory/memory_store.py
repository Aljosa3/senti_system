"""
Memory Store - FAZA 12
Location: senti_core_module/senti_memory/memory_store.py

Physical storage layer for episodic and semantic memory.
- File-based JSON storage
- Atomic writes
- Thread-safe operations
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class MemoryStore:
    """
    File-based storage for memory systems.
    Ensures atomic writes and thread safety.
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize memory store.

        Args:
            storage_dir: Directory for storing memory files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.lock = threading.Lock()

        # Storage files
        self.episodic_file = self.storage_dir / "episodic_memory.json"
        self.semantic_file = self.storage_dir / "semantic_memory.json"

    # =====================================================
    # EPISODIC MEMORY STORAGE
    # =====================================================

    def save_episodic_events(self, events: List[Dict[str, Any]]) -> bool:
        """
        Save episodic events to storage.

        Args:
            events: List of event dictionaries

        Returns:
            Success status
        """
        with self.lock:
            try:
                self._atomic_write(self.episodic_file, events)
                return True
            except Exception as e:
                print(f"[MemoryStore] Failed to save episodic events: {e}")
                return False

    def load_episodic_events(self) -> List[Dict[str, Any]]:
        """
        Load episodic events from storage.

        Returns:
            List of event dictionaries
        """
        with self.lock:
            try:
                if not self.episodic_file.exists():
                    return []

                with open(self.episodic_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[MemoryStore] Failed to load episodic events: {e}")
                return []

    def append_episodic_event(self, event: Dict[str, Any]) -> bool:
        """
        Append single event to episodic storage.

        Args:
            event: Event dictionary

        Returns:
            Success status
        """
        events = self.load_episodic_events()
        events.append(event)
        return self.save_episodic_events(events)

    # =====================================================
    # SEMANTIC MEMORY STORAGE
    # =====================================================

    def save_semantic_facts(self, facts: Dict[str, Any]) -> bool:
        """
        Save semantic facts to storage.

        Args:
            facts: Dictionary of key-value facts

        Returns:
            Success status
        """
        with self.lock:
            try:
                self._atomic_write(self.semantic_file, facts)
                return True
            except Exception as e:
                print(f"[MemoryStore] Failed to save semantic facts: {e}")
                return False

    def load_semantic_facts(self) -> Dict[str, Any]:
        """
        Load semantic facts from storage.

        Returns:
            Dictionary of facts
        """
        with self.lock:
            try:
                if not self.semantic_file.exists():
                    return {}

                with open(self.semantic_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[MemoryStore] Failed to load semantic facts: {e}")
                return {}

    def save_semantic_fact(self, key: str, value: Any) -> bool:
        """
        Save single semantic fact.

        Args:
            key: Fact key
            value: Fact value

        Returns:
            Success status
        """
        facts = self.load_semantic_facts()
        facts[key] = value
        return self.save_semantic_facts(facts)

    # =====================================================
    # UTILITY METHODS
    # =====================================================

    def _atomic_write(self, file_path: Path, data: Any) -> None:
        """
        Write data atomically using temp file + rename.

        Args:
            file_path: Target file path
            data: Data to write (will be JSON serialized)
        """
        temp_file = file_path.with_suffix('.tmp')

        try:
            # Write to temp file
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            # Atomic rename
            temp_file.replace(file_path)
        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise e

    def clear_episodic(self) -> bool:
        """Clear all episodic memory."""
        return self.save_episodic_events([])

    def clear_semantic(self) -> bool:
        """Clear all semantic memory."""
        return self.save_semantic_facts({})

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Stats dictionary
        """
        stats = {
            "episodic_count": len(self.load_episodic_events()),
            "semantic_count": len(self.load_semantic_facts()),
            "storage_dir": str(self.storage_dir)
        }

        if self.episodic_file.exists():
            stats["episodic_size_bytes"] = self.episodic_file.stat().st_size

        if self.semantic_file.exists():
            stats["semantic_size_bytes"] = self.semantic_file.stat().st_size

        return stats
