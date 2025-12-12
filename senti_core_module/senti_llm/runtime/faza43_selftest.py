#!/usr/bin/env python3
"""
FAZA 43 Self-Test — Internal Scheduler System
----------------------------------------------
Comprehensive test suite for the Senti OS Scheduler.

Tests:
1. Scheduler initialization
2. Task creation (interval, oneshot, event)
3. Task execution (tick)
4. Event-triggered tasks
5. Task cancellation
6. Task auto-disable on failures
7. Scheduler stats
8. Module integration
9. Demo module execution
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from senti_core_module.senti_llm.runtime.scheduler import Scheduler, Task, TaskType, TaskRegistry
from senti_core_module.senti_llm.runtime.event_bus import EventBus
from senti_core_module.senti_llm.runtime.event_context import EventContext
from senti_core_module.senti_llm.runtime.llm_runtime_context import RuntimeContext
from senti_core_module.senti_llm.runtime.action_model import RuntimeAction
from senti_core_module.senti_llm.runtime.execution_orchestrator import ExecutionOrchestrator


class TestRunner:
    """Test runner for FAZA 43."""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def run_test(self, test_name: str, test_fn: callable):
        """Run a single test."""
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")

        try:
            test_fn()
            self.tests_passed += 1
            self.test_results.append((test_name, "PASS", None))
            print(f"✓ PASS: {test_name}")
        except AssertionError as e:
            self.tests_failed += 1
            self.test_results.append((test_name, "FAIL", str(e)))
            print(f"✗ FAIL: {test_name}")
            print(f"  Error: {e}")
        except Exception as e:
            self.tests_failed += 1
            self.test_results.append((test_name, "ERROR", str(e)))
            print(f"✗ ERROR: {test_name}")
            print(f"  Exception: {e}")

    def print_summary(self):
        """Print test summary."""
        print(f"\n{'='*60}")
        print(f"FAZA 43 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total: {self.tests_passed + self.tests_failed}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")

        if self.tests_failed > 0:
            print(f"\nFailed tests:")
            for name, status, error in self.test_results:
                if status in ["FAIL", "ERROR"]:
                    print(f"  - {name}: {error}")

        print(f"{'='*60}\n")

        return self.tests_failed == 0


# ================================================================
#  TEST FUNCTIONS
# ================================================================

def test_scheduler_initialization():
    """Test 1: Scheduler initialization."""
    scheduler = Scheduler()

    assert scheduler is not None, "Scheduler should be created"
    assert scheduler.registry is not None, "Scheduler should have registry"
    assert scheduler._tick_count == 0, "Tick count should start at 0"

    print("✓ Scheduler initialized successfully")


def test_task_creation():
    """Test 2: Task creation (interval, oneshot, event)."""
    # Create test tasks
    interval_task = Task(
        task_type=TaskType.INTERVAL,
        callable_fn=lambda: None,
        interval=5.0
    )

    oneshot_task = Task(
        task_type=TaskType.ONESHOT,
        callable_fn=lambda: None,
        next_run=time.time() + 10.0
    )

    event_task = Task(
        task_type=TaskType.EVENT,
        callable_fn=lambda ctx: None,
        event_type="test.event"
    )

    assert interval_task.type == TaskType.INTERVAL, "Interval task type should be INTERVAL"
    assert interval_task.interval == 5.0, "Interval should be 5.0 seconds"
    assert interval_task.enabled, "Task should be enabled by default"

    assert oneshot_task.type == TaskType.ONESHOT, "Oneshot task type should be ONESHOT"
    assert oneshot_task.enabled, "Task should be enabled by default"

    assert event_task.type == TaskType.EVENT, "Event task type should be EVENT"
    assert event_task.event_type == "test.event", "Event type should be test.event"

    print(f"✓ Created 3 tasks: {interval_task.id[:8]}, {oneshot_task.id[:8]}, {event_task.id[:8]}")


def test_task_registry():
    """Test 3: Task registry operations."""
    registry = TaskRegistry()

    # Register tasks
    task1 = Task(TaskType.INTERVAL, lambda: None, interval=1.0)
    task2 = Task(TaskType.ONESHOT, lambda: None)
    task3 = Task(TaskType.EVENT, lambda ctx: None, event_type="test.event")

    registry.register(task1)
    registry.register(task2)
    registry.register(task3)

    # Test counts
    assert registry.count() == 3, "Registry should have 3 tasks"
    assert registry.count_enabled() == 3, "All tasks should be enabled"

    # Test retrieval
    retrieved = registry.get(task1.id)
    assert retrieved is not None, "Should retrieve task by ID"
    assert retrieved.id == task1.id, "Retrieved task should match"

    # Test event handler listing
    handlers = registry.list_event_handlers("test.event")
    assert len(handlers) == 1, "Should have 1 event handler for test.event"

    # Test unregister
    success = registry.unregister(task1.id)
    assert success, "Unregister should succeed"
    assert registry.count() == 2, "Registry should have 2 tasks after unregister"

    print(f"✓ Task registry operations verified")


def test_scheduler_interval_tasks():
    """Test 4: Scheduler interval task execution."""
    scheduler = Scheduler()
    execution_count = {"count": 0}

    def interval_callback():
        execution_count["count"] += 1

    # Schedule interval task with 1 second interval
    task_id = scheduler.schedule_interval(interval_callback, interval=1.0)
    assert task_id, "Task ID should be returned"

    # Tick scheduler at intervals
    now = time.time()

    # First tick: not due yet (just scheduled)
    scheduler.tick(now)
    assert execution_count["count"] == 0, "Task should not execute immediately"

    # Tick after 1.5 seconds: should execute
    scheduler.tick(now + 1.5)
    assert execution_count["count"] == 1, "Task should execute after interval"

    # Tick after another 1 second: should execute again
    scheduler.tick(now + 2.5)
    assert execution_count["count"] == 2, "Task should execute again"

    print(f"✓ Interval task executed {execution_count['count']} times")


def test_scheduler_oneshot_tasks():
    """Test 5: Scheduler oneshot task execution."""
    scheduler = Scheduler()
    execution_count = {"count": 0}

    def oneshot_callback():
        execution_count["count"] += 1

    # Schedule oneshot task with 1 second delay
    task_id = scheduler.schedule_oneshot(oneshot_callback, delay=1.0)
    assert task_id, "Task ID should be returned"

    now = time.time()

    # Tick before delay: should not execute
    scheduler.tick(now + 0.5)
    assert execution_count["count"] == 0, "Oneshot should not execute before delay"

    # Tick after delay: should execute
    scheduler.tick(now + 1.5)
    assert execution_count["count"] == 1, "Oneshot should execute after delay"

    # Tick again: should not execute (disabled after execution)
    scheduler.tick(now + 2.5)
    assert execution_count["count"] == 1, "Oneshot should only execute once"

    print(f"✓ Oneshot task executed once and disabled")


def test_scheduler_event_tasks():
    """Test 6: Scheduler event-triggered task execution."""
    event_bus = EventBus()
    scheduler = Scheduler(event_bus=event_bus)
    execution_count = {"count": 0}

    def event_callback(event_context):
        execution_count["count"] += 1

    # Schedule event-triggered task
    task_id = scheduler.schedule_event("test.trigger", event_callback)
    assert task_id, "Task ID should be returned"

    # Trigger event
    event_ctx = EventContext(
        event_type="test.trigger",
        source="selftest",
        payload={"message": "test"},
        category="test"
    )

    scheduler.trigger_event("test.trigger", event_ctx)
    assert execution_count["count"] == 1, "Event task should execute on trigger"

    # Trigger again
    scheduler.trigger_event("test.trigger", event_ctx)
    assert execution_count["count"] == 2, "Event task should execute again"

    print(f"✓ Event-triggered task executed {execution_count['count']} times")


def test_task_cancellation():
    """Test 7: Task cancellation."""
    scheduler = Scheduler()
    execution_count = {"count": 0}

    def callback():
        execution_count["count"] += 1

    # Schedule task
    task_id = scheduler.schedule_interval(callback, interval=1.0)

    # Cancel task
    success = scheduler.cancel(task_id)
    assert success, "Cancellation should succeed"

    # Tick scheduler: task should not execute
    now = time.time()
    scheduler.tick(now + 2.0)
    assert execution_count["count"] == 0, "Cancelled task should not execute"

    print(f"✓ Task cancelled successfully")


def test_task_auto_disable():
    """Test 8: Task auto-disable after 3 failures."""
    scheduler = Scheduler()
    execution_count = {"count": 0}

    def failing_callback():
        execution_count["count"] += 1
        raise ValueError("Intentional failure")

    # Schedule failing task
    task_id = scheduler.schedule_interval(failing_callback, interval=1.0)

    now = time.time()

    # Execute 3 times (should fail and auto-disable)
    for i in range(5):
        scheduler.tick(now + (i + 1) * 1.5)

    # Task should only execute 3 times before auto-disable
    assert execution_count["count"] == 3, f"Task should execute 3 times before auto-disable (got {execution_count['count']})"

    print(f"✓ Task auto-disabled after 3 failures")


def test_scheduler_stats():
    """Test 9: Scheduler statistics."""
    scheduler = Scheduler()

    # Schedule multiple tasks
    scheduler.schedule_interval(lambda: None, interval=1.0)
    scheduler.schedule_oneshot(lambda: None, delay=1.0)
    scheduler.schedule_event("test", lambda ctx: None)

    # Get stats
    stats = scheduler.get_stats()

    assert "tick_count" in stats, "Stats should include tick_count"
    assert "total_tasks" in stats, "Stats should include total_tasks"
    assert stats["total_tasks"] == 3, "Should have 3 tasks"
    assert stats["enabled_tasks"] == 3, "All tasks should be enabled"

    print(f"✓ Scheduler stats: {stats}")


def test_module_integration():
    """Test 10: Module integration with scheduler."""
    # Create runtime context and orchestrator
    context = RuntimeContext(prompt="test", capability="execution")
    orchestrator = ExecutionOrchestrator(context)

    # Load demo module
    demo_path = os.path.join(
        os.path.dirname(__file__),
        "faza43_demo_scheduler_module.py"
    )

    load_action = RuntimeAction(
        source="selftest",
        action_type="load.module",
        payload={"path": demo_path}
    )

    result = orchestrator.execute(load_action)
    assert result["ok"], f"Module load should succeed: {result.get('error')}"

    print(f"✓ Demo module loaded: {result['data']['module']}")

    # Run module with status action
    run_action = RuntimeAction(
        source="selftest",
        action_type="run.module",
        payload={"module": "faza43_demo_scheduler", "action": "status"}
    )

    result = orchestrator.execute(run_action)
    assert result["ok"], f"Module run should succeed: {result.get('error')}"

    demo_state = result["data"].get("demo_state", {})
    assert "scheduled_tasks" in demo_state, "Demo state should include scheduled_tasks"
    assert demo_state["scheduled_tasks"] == 3, "Demo should have 3 scheduled tasks"

    print(f"✓ Demo module status: {demo_state}")


def test_event_bus_scheduler_integration():
    """Test 11: EventBus + Scheduler integration."""
    event_bus = EventBus()
    scheduler = Scheduler(event_bus=event_bus)
    event_bus.set_scheduler(scheduler)

    execution_count = {"count": 0}

    def event_handler(event_context):
        execution_count["count"] += 1

    # Schedule event task via scheduler
    scheduler.schedule_event("integration.test", event_handler)

    # Publish event via event bus (should trigger scheduler)
    event_ctx = EventContext(
        event_type="integration.test",
        source="selftest",
        payload={"test": "data"},
        category="test"
    )

    event_bus.publish("integration.test", event_ctx)

    assert execution_count["count"] == 1, "Event task should execute when event published"

    print(f"✓ EventBus + Scheduler integration working")


# ================================================================
#  MAIN TEST EXECUTION
# ================================================================

def main():
    """Run all FAZA 43 self-tests."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   FAZA 43 — INTERNAL SCHEDULER SYSTEM SELF-TEST             ║
║                                                              ║
║   Testing cooperative task scheduling with:                 ║
║   - Interval tasks (repeating)                              ║
║   - Oneshot tasks (single execution)                        ║
║   - Event-triggered tasks                                   ║
║   - Task cancellation                                       ║
║   - Auto-disable on failures                                ║
║   - Module integration                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    runner = TestRunner()

    # Run all tests
    runner.run_test("1. Scheduler Initialization", test_scheduler_initialization)
    runner.run_test("2. Task Creation", test_task_creation)
    runner.run_test("3. Task Registry Operations", test_task_registry)
    runner.run_test("4. Interval Task Execution", test_scheduler_interval_tasks)
    runner.run_test("5. Oneshot Task Execution", test_scheduler_oneshot_tasks)
    runner.run_test("6. Event-Triggered Tasks", test_scheduler_event_tasks)
    runner.run_test("7. Task Cancellation", test_task_cancellation)
    runner.run_test("8. Task Auto-Disable", test_task_auto_disable)
    runner.run_test("9. Scheduler Statistics", test_scheduler_stats)
    runner.run_test("10. Module Integration", test_module_integration)
    runner.run_test("11. EventBus Integration", test_event_bus_scheduler_integration)

    # Print summary and exit
    success = runner.print_summary()

    if success:
        print("🎉 FAZA 43 SCHEDULER SYSTEM FULLY OPERATIONAL!")
        return 0
    else:
        print("❌ FAZA 43 TESTS FAILED - See errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
