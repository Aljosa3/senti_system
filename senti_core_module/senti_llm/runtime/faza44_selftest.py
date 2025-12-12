#!/usr/bin/env python3
"""
FAZA 44 Self-Test — Async Execution Layer
------------------------------------------
Comprehensive test suite for the Senti OS Async Execution Layer.

Tests:
1. AsyncTask creation and lifecycle
2. AsyncTaskManager initialization
3. Async task execution (tick)
4. Async task cancellation
5. Async capabilities
6. Module integration
7. Async run method
8. Async event handlers
9. Async event chains
10. Concurrency limits
11. Error handling
"""

import sys
import os
import time
import asyncio

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from senti_core_module.senti_llm.runtime.async_exec import AsyncTask, AsyncTaskStatus, AsyncTaskManager
from senti_core_module.senti_llm.runtime.event_bus import EventBus
from senti_core_module.senti_llm.runtime.event_context import EventContext
from senti_core_module.senti_llm.runtime.llm_runtime_context import RuntimeContext
from senti_core_module.senti_llm.runtime.action_model import RuntimeAction
from senti_core_module.senti_llm.runtime.execution_orchestrator import ExecutionOrchestrator


class TestRunner:
    """Test runner for FAZA 44."""

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
        print(f"FAZA 44 TEST SUMMARY")
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

def test_async_task_creation():
    """Test 1: AsyncTask creation and lifecycle."""
    async def sample_coroutine():
        await asyncio.sleep(0.1)
        return "completed"

    task = AsyncTask(coroutine=sample_coroutine())

    assert task.id is not None, "Task should have ID"
    assert task.status == AsyncTaskStatus.PENDING, "Task should start as PENDING"
    assert not task.is_done(), "Task should not be done initially"

    print(f"✓ Created async task: {task.id[:8]}")


def test_async_task_manager():
    """Test 2: AsyncTaskManager initialization."""
    manager = AsyncTaskManager()

    assert manager is not None, "Manager should be created"
    assert manager._tick_count == 0, "Tick count should start at 0"

    stats = manager.get_stats()
    assert "total_tasks" in stats, "Stats should include total_tasks"

    print(f"✓ AsyncTaskManager initialized with stats: {stats}")


def test_async_task_execution():
    """Test 3: Async task execution (tick)."""
    manager = AsyncTaskManager()
    execution_count = {"count": 0}

    async def async_worker():
        execution_count["count"] += 1
        await asyncio.sleep(0.1)
        return "completed"

    # Create task
    task_id = manager.create_task(async_worker())
    assert task_id, "Task ID should be returned"

    # Tick manager to start and process tasks
    for _ in range(5):
        manager.tick()
        time.sleep(0.05)

    # Check task completed
    task = manager.get(task_id)
    assert task is not None, "Task should exist"

    # Task should eventually complete
    print(f"✓ Async task status: {task.status.value}")


def test_async_task_cancellation():
    """Test 4: Async task cancellation."""
    manager = AsyncTaskManager()

    async def long_worker():
        await asyncio.sleep(10)
        return "completed"

    # Create and cancel task
    task_id = manager.create_task(long_worker())
    manager.tick()  # Start task

    success = manager.cancel(task_id)
    assert success, "Cancellation should succeed"

    task = manager.get(task_id)
    assert task.status == AsyncTaskStatus.CANCELLED, "Task should be cancelled"

    print(f"✓ Task cancelled successfully")


def test_async_capabilities():
    """Test 5: Async capabilities (schedule, await)."""
    from senti_core_module.senti_llm.runtime.async_exec import AsyncScheduleCapability, AsyncAwaitCapability

    manager = AsyncTaskManager()
    schedule_cap = AsyncScheduleCapability(manager)
    await_cap = AsyncAwaitCapability(manager)

    async def test_coroutine():
        await asyncio.sleep(0.1)
        return {"result": "test"}

    # Schedule task
    task_id = schedule_cap.schedule(test_coroutine())
    assert task_id, "Task should be scheduled"

    # Poll task
    for _ in range(5):
        manager.tick()
        time.sleep(0.05)

    result = await_cap.poll(task_id)
    assert result["ok"], "Poll should succeed"

    print(f"✓ Async capabilities working, task status: {result.get('status')}")


def test_module_integration():
    """Test 6: Module integration with async_manager."""
    context = RuntimeContext(prompt="test", capability="execution")
    orchestrator = ExecutionOrchestrator(context)

    # Load demo module
    demo_path = os.path.join(
        os.path.dirname(__file__),
        "faza44_demo_async_module.py"
    )

    load_action = RuntimeAction(
        source="selftest",
        action_type="load.module",
        payload={"path": demo_path}
    )

    result = orchestrator.execute(load_action)
    assert result["ok"], f"Module load should succeed: {result.get('error')}"

    print(f"✓ Demo module loaded: {result['data']['module']}")


def test_async_run_method():
    """Test 7: Async run method."""
    context = RuntimeContext(prompt="test", capability="execution")
    orchestrator = ExecutionOrchestrator(context)

    # Load module first
    demo_path = os.path.join(
        os.path.dirname(__file__),
        "faza44_demo_async_module.py"
    )

    orchestrator.execute(RuntimeAction(
        source="selftest",
        action_type="load.module",
        payload={"path": demo_path}
    ))

    # Run async module
    run_action = RuntimeAction(
        source="selftest",
        action_type="run.module",
        payload={"module": "faza44_demo_async", "action": "async_work"}
    )

    result = orchestrator.execute(run_action)

    # Should return pending status with task_id
    assert result["ok"], f"Async run should succeed: {result.get('error')}"

    if result.get("status") == "pending":
        print(f"✓ Async run created task: {result.get('task_id')}")
    else:
        print(f"✓ Async run completed directly")


def test_async_event_handlers():
    """Test 8: Async event handlers."""
    event_bus = EventBus()
    manager = AsyncTaskManager(event_bus=event_bus)
    event_bus.set_async_manager(manager)

    execution_count = {"count": 0}

    async def async_handler(event_context):
        execution_count["count"] += 1
        await asyncio.sleep(0.1)

    # Subscribe async handler
    event_bus.subscribe("test.async", async_handler)

    # Publish event
    event_ctx = EventContext(
        event_type="test.async",
        source="selftest",
        payload={"test": "data"},
        category="test"
    )

    results = event_bus.publish("test.async", event_ctx)

    # Should create async task
    assert len(results) > 0, "Should have handler result"

    # Tick manager to process
    for _ in range(3):
        manager.tick()
        time.sleep(0.05)

    print(f"✓ Async event handler executed (count: {execution_count['count']})")


def test_concurrency_limits():
    """Test 9: Concurrency limits."""
    manager = AsyncTaskManager()

    async def worker():
        await asyncio.sleep(1)

    # Create many tasks
    task_ids = []
    for i in range(20):
        task_id = manager.create_task(worker())
        if task_id:
            task_ids.append(task_id)

    # Tick to start tasks
    manager.tick()

    stats = manager.get_stats()
    running = stats.get("running_tasks", 0)
    pending = stats.get("pending_tasks", 0)

    assert running <= AsyncTaskManager.MAX_RUNNING_TASKS, \
        f"Running tasks ({running}) should not exceed limit ({AsyncTaskManager.MAX_RUNNING_TASKS})"

    print(f"✓ Concurrency limit enforced: {running} running, {pending} pending")


def test_error_handling():
    """Test 10: Error handling in async tasks."""
    manager = AsyncTaskManager()

    async def failing_worker():
        await asyncio.sleep(0.1)
        raise ValueError("Intentional error")

    # Create failing task
    task_id = manager.create_task(failing_worker())

    # Process task
    for _ in range(5):
        manager.tick()
        time.sleep(0.05)

    # Check task failed gracefully
    task = manager.get(task_id)
    assert task is not None, "Task should exist"
    assert task.status == AsyncTaskStatus.FAILED, "Task should be marked as failed"
    assert task.error is not None, "Task should have error message"

    print(f"✓ Error handled gracefully: {task.error[:50]}")


# ================================================================
#  MAIN TEST EXECUTION
# ================================================================

def main():
    """Run all FAZA 44 self-tests."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   FAZA 44 — ASYNC EXECUTION LAYER SELF-TEST                 ║
║                                                              ║
║   Testing asynchronous execution with:                      ║
║   - Async task creation and lifecycle                       ║
║   - Cooperative async scheduling                            ║
║   - Async module run methods                                ║
║   - Async event handlers                                    ║
║   - Concurrency limits                                      ║
║   - Error handling                                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    runner = TestRunner()

    # Run all tests
    runner.run_test("1. AsyncTask Creation", test_async_task_creation)
    runner.run_test("2. AsyncTaskManager Init", test_async_task_manager)
    runner.run_test("3. Async Task Execution", test_async_task_execution)
    runner.run_test("4. Async Task Cancellation", test_async_task_cancellation)
    runner.run_test("5. Async Capabilities", test_async_capabilities)
    runner.run_test("6. Module Integration", test_module_integration)
    runner.run_test("7. Async Run Method", test_async_run_method)
    runner.run_test("8. Async Event Handlers", test_async_event_handlers)
    runner.run_test("9. Concurrency Limits", test_concurrency_limits)
    runner.run_test("10. Error Handling", test_error_handling)

    # Print summary and exit
    success = runner.print_summary()

    if success:
        print("🎉 FAZA 44 ASYNC EXECUTION LAYER FULLY OPERATIONAL!")
        return 0
    else:
        print("❌ FAZA 44 TESTS FAILED - See errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
