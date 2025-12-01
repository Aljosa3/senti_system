"""
FAZA 12 Memory Engine Test Suite
Location: tests/test_faza12_memory.py

Comprehensive tests for the adaptive memory system.
"""

import unittest
import tempfile
import time
from pathlib import Path

# Import memory components
from senti_core_module.senti_memory import (
    MemoryManager,
    MemoryEngine,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    MemoryStore,
    MemoryRules,
    MemoryEvents,
    ConsolidationService
)

# Mock EventBus for testing
class MockEventBus:
    def __init__(self):
        self.events = []
        self.handlers = {}

    def publish(self, event_type, payload):
        self.events.append({"type": event_type, "payload": payload})

    def subscribe(self, event_type, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        if event_type in self.handlers:
            self.handlers[event_type].remove(handler)


class TestWorkingMemory(unittest.TestCase):
    """Test working memory functionality."""

    def setUp(self):
        self.working = WorkingMemory(default_ttl_seconds=2)

    def test_add_retrieve(self):
        """Test adding and retrieving items."""
        self.working.add("key1", "value1")
        value = self.working.get("key1")
        self.assertEqual(value, "value1")

    def test_expiration(self):
        """Test TTL expiration."""
        self.working.add("key1", "value1", ttl_seconds=1)

        # Should exist immediately
        self.assertIsNotNone(self.working.get("key1"))

        # Wait for expiration
        time.sleep(1.5)

        # Should be None after expiration
        self.assertIsNone(self.working.get("key1"))

    def test_cleanup_expired(self):
        """Test cleanup of expired items."""
        self.working.add("key1", "value1", ttl_seconds=1)
        self.working.add("key2", "value2", ttl_seconds=10)

        time.sleep(1.5)

        removed = self.working.cleanup_expired()
        self.assertEqual(removed, 1)

        # key2 should still exist
        self.assertIsNotNone(self.working.get("key2"))


class TestEpisodicMemory(unittest.TestCase):
    """Test episodic memory functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(Path(self.temp_dir))
        self.episodic = EpisodicMemory(self.store)

    def test_record_retrieve(self):
        """Test recording and retrieving events."""
        self.episodic.record("test_event", {"data": "value"})

        events = self.episodic.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "test_event")

    def test_filter_by_type(self):
        """Test filtering events by type."""
        self.episodic.record("type1", {"data": "a"})
        self.episodic.record("type2", {"data": "b"})
        self.episodic.record("type1", {"data": "c"})

        type1_events = self.episodic.get_events(filter_type="type1")
        self.assertEqual(len(type1_events), 2)

    def test_prune_old_events(self):
        """Test pruning old events."""
        for i in range(100):
            self.episodic.record(f"event_{i}", {"index": i})

        pruned = self.episodic.prune_old_events(keep_count=50)
        self.assertEqual(pruned, 50)

        remaining = self.episodic.get_events()
        self.assertEqual(len(remaining), 50)


class TestSemanticMemory(unittest.TestCase):
    """Test semantic memory functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(Path(self.temp_dir))
        self.semantic = SemanticMemory(self.store)

    def test_save_retrieve(self):
        """Test saving and retrieving facts."""
        self.semantic.save_fact("key1", "value1")
        value = self.semantic.get_fact("key1")
        self.assertEqual(value, "value1")

    def test_search(self):
        """Test pattern search."""
        self.semantic.save_fact("user_name", "John")
        self.semantic.save_fact("user_age", 30)
        self.semantic.save_fact("system_version", "1.0")

        results = self.semantic.search("user")
        self.assertEqual(len(results), 2)

    def test_batch_save(self):
        """Test batch saving facts."""
        facts = {
            "fact1": "value1",
            "fact2": "value2",
            "fact3": "value3"
        }

        self.semantic.save_facts_batch(facts)

        self.assertEqual(self.semantic.get_fact("fact1"), "value1")
        self.assertEqual(self.semantic.get_fact("fact2"), "value2")


class TestMemoryRules(unittest.TestCase):
    """Test memory security rules."""

    def setUp(self):
        self.rules = MemoryRules(strict_mode=True)

    def test_size_validation(self):
        """Test size limit validation."""
        small_data = "x" * 100
        large_data = "x" * (2 * 1024 * 1024)  # 2MB

        is_valid, _ = self.rules.validate_size(small_data, "working")
        self.assertTrue(is_valid)

        is_valid, _ = self.rules.validate_size(large_data, "working")
        self.assertFalse(is_valid)

    def test_sensitive_data_detection(self):
        """Test sensitive data detection."""
        safe_data = "This is safe data"
        sensitive_data = "My password is secret123"

        has_sensitive, _ = self.rules.contains_sensitive_data(safe_data)
        self.assertFalse(has_sensitive)

        has_sensitive, _ = self.rules.contains_sensitive_data(sensitive_data)
        self.assertTrue(has_sensitive)

    def test_action_validation(self):
        """Test action whitelisting."""
        is_valid, _ = self.rules.validate_action("add")
        self.assertTrue(is_valid)

        is_valid, _ = self.rules.validate_action("hack_system")
        self.assertFalse(is_valid)


class TestMemoryEvents(unittest.TestCase):
    """Test EventBus integration."""

    def setUp(self):
        self.event_bus = MockEventBus()
        self.events = MemoryEvents(self.event_bus)

    def test_publish_memory_added(self):
        """Test memory added event."""
        self.events.publish_memory_added("working", "test_key", 100)

        self.assertEqual(len(self.event_bus.events), 1)
        event = self.event_bus.events[0]
        self.assertEqual(event["type"], "memory.added")
        self.assertEqual(event["payload"]["key"], "test_key")

    def test_publish_consolidation(self):
        """Test consolidation event."""
        self.events.publish_memory_consolidated(50, 10, 123.45)

        self.assertEqual(len(self.event_bus.events), 1)
        event = self.event_bus.events[0]
        self.assertEqual(event["type"], "memory.consolidated")


class TestConsolidationService(unittest.TestCase):
    """Test memory consolidation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(Path(self.temp_dir))
        self.episodic = EpisodicMemory(self.store)
        self.semantic = SemanticMemory(self.store)
        self.event_bus = MockEventBus()
        self.events = MemoryEvents(self.event_bus)

        self.consolidation = ConsolidationService(
            self.episodic,
            self.semantic,
            self.events
        )

    def test_consolidation_creates_semantic_entries(self):
        """Test that consolidation creates semantic facts."""
        # Add episodic events
        for i in range(20):
            self.episodic.record("test_event", {"data": f"value_{i}"})

        # Consolidate
        result = self.consolidation.consolidate(min_events=10)

        self.assertEqual(result["status"], "success")
        self.assertGreater(result["facts_created"], 0)

        # Check semantic memory has facts
        facts = self.semantic.get_all_keys()
        self.assertGreater(len(facts), 0)


class TestMemoryEngine(unittest.TestCase):
    """Test high-level memory engine API."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(Path(self.temp_dir))
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory(self.store)
        self.semantic = SemanticMemory(self.store)
        self.event_bus = MockEventBus()
        self.events = MemoryEvents(self.event_bus)
        self.rules = MemoryRules()

        self.consolidation = ConsolidationService(
            self.episodic,
            self.semantic,
            self.events
        )

        self.engine = MemoryEngine(
            self.working,
            self.episodic,
            self.semantic,
            self.consolidation,
            self.rules,
            self.events
        )

    def test_remember_recall(self):
        """Test unified remember/recall API."""
        # Remember in working memory
        result = self.engine.remember("test_value", memory_type="working", key="test_key")
        self.assertEqual(result["status"], "success")

        # Recall from working memory
        result = self.engine.recall("test_key", memory_type="working")
        self.assertTrue(result["found"])
        self.assertEqual(result["data"], "test_value")

    def test_consolidate(self):
        """Test engine consolidation."""
        # Add episodic events
        for i in range(15):
            self.engine.remember(
                {"index": i},
                memory_type="episodic",
                event_type="test"
            )

        # Consolidate
        result = self.engine.consolidate(min_events=10)
        self.assertEqual(result["status"], "success")

    def test_memory_stats(self):
        """Test memory statistics."""
        self.engine.remember("value1", memory_type="working", key="key1")
        self.engine.remember({"data": "test"}, memory_type="episodic", event_type="test")
        self.engine.remember("fact_value", memory_type="semantic", key="fact1")

        stats = self.engine.get_memory_stats()
        self.assertEqual(stats["status"], "success")
        self.assertIn("working_memory", stats)
        self.assertIn("episodic_memory", stats)
        self.assertIn("semantic_memory", stats)


class TestMemoryManager(unittest.TestCase):
    """Test memory manager integration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.event_bus = MockEventBus()
        self.manager = MemoryManager(
            Path(self.temp_dir),
            self.event_bus
        )

    def test_initialization(self):
        """Test manager initialization."""
        result = self.manager.start()
        self.assertEqual(result["status"], "success")
        self.assertTrue(self.manager.is_initialized())

    def test_get_engine(self):
        """Test getting engine instance."""
        self.manager.start()
        engine = self.manager.get_engine()
        self.assertIsNotNone(engine)
        self.assertIsInstance(engine, MemoryEngine)

    def test_maintenance(self):
        """Test maintenance operation."""
        self.manager.start()

        # Add some memory
        engine = self.manager.get_engine()
        for i in range(15):
            engine.remember({"index": i}, memory_type="episodic", event_type="test")

        # Run maintenance
        result = self.manager.perform_maintenance()
        self.assertEqual(result["status"], "success")

    def test_shutdown(self):
        """Test graceful shutdown."""
        self.manager.start()
        result = self.manager.stop()
        self.assertEqual(result["status"], "success")
        self.assertFalse(self.manager.is_initialized())


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWorkingMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestEpisodicMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestSemanticMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryRules))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryEvents))
    suite.addTests(loader.loadTestsFromTestCase(TestConsolidationService))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryManager))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
