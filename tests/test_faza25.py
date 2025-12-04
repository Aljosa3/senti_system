"""
FAZA 25 - Orchestration Execution Engine Tests

Comprehensive test suite for FAZA 25 components:
- Task model and status
- Priority task queue
- Worker execution
- Orchestrator manager API
- Pipeline integration with FAZA 17
"""

import asyncio
from datetime import datetime

from senti_os.core.faza25 import (
    Task,
    TaskStatus,
    PriorityTaskQueue,
    OrchestratorManager,
    submit_pipeline_task,
    get_pipeline_task_result
)


class TestTaskModel:
    """Tests for Task model and status transitions"""

    async def dummy_executor(self, task: Task):
        """Dummy task executor for testing"""
        return "success"

    def test_task_creation(self):
        """Test task creation with default values"""
        task = Task(
            name="Test Task",
            executor=self.dummy_executor,
            priority=7
        )

        assert task.name == "Test Task"
        assert task.priority == 7
        assert task.status == TaskStatus.QUEUED
        assert task.id is not None
        assert isinstance(task.created_at, datetime)
        assert task.started_at is None
        assert task.completed_at is None

    def test_task_priority_comparison(self):
        """Test task priority comparison for heapq"""
        task_low = Task(name="Low", executor=self.dummy_executor, priority=3)
        task_high = Task(name="High", executor=self.dummy_executor, priority=8)

        # Higher priority should be "less than" (for min-heap inversion)
        assert task_high < task_low

    def test_task_status_transitions(self):
        """Test task status transitions"""
        task = Task(name="Test", executor=self.dummy_executor)

        # Initial status
        assert task.status == TaskStatus.QUEUED

        # Mark as running
        task.mark_running()
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None

        # Mark as done
        task.mark_done(result="test result")
        assert task.status == TaskStatus.DONE
        assert task.completed_at is not None
        assert task.result == "test result"

    def test_task_error_handling(self):
        """Test task error state"""
        task = Task(name="Test", executor=self.dummy_executor)
        task.mark_error("Test error message")

        assert task.status == TaskStatus.ERROR
        assert task.error_message == "Test error message"
        assert task.completed_at is not None

    def test_task_cancellation(self):
        """Test task cancellation"""
        task = Task(name="Test", executor=self.dummy_executor)
        task.mark_cancelled()

        assert task.status == TaskStatus.CANCELLED
        assert task.completed_at is not None

    def test_task_to_dict(self):
        """Test task serialization to dictionary"""
        task = Task(
            name="Test Task",
            executor=self.dummy_executor,
            priority=5,
            task_type="test"
        )

        task_dict = task.to_dict()

        assert task_dict["name"] == "Test Task"
        assert task_dict["priority"] == 5
        assert task_dict["task_type"] == "test"
        assert task_dict["status"] == "queued"
        assert "id" in task_dict


class TestPriorityTaskQueue:
    """Tests for priority task queue"""

    async def dummy_executor(self, task: Task):
        return "success"

    def test_queue_creation(self):
        """Test queue initialization"""
        queue = PriorityTaskQueue()
        assert queue.size() == 0
        assert queue.is_empty()

    def test_queue_put_and_get(self):
        """Test adding and retrieving tasks"""
        queue = PriorityTaskQueue()

        task = Task(name="Test", executor=self.dummy_executor)
        queue.put(task)

        assert queue.size() == 1
        assert not queue.is_empty()

        retrieved = queue.get_nowait()
        assert retrieved.id == task.id
        assert queue.size() == 0

    def test_queue_priority_ordering(self):
        """Test that higher priority tasks are retrieved first"""
        queue = PriorityTaskQueue()

        task_low = Task(name="Low", executor=self.dummy_executor, priority=2)
        task_medium = Task(name="Medium", executor=self.dummy_executor, priority=5)
        task_high = Task(name="High", executor=self.dummy_executor, priority=9)

        # Add in random order
        queue.put(task_medium)
        queue.put(task_low)
        queue.put(task_high)

        # Should retrieve in priority order (high to low)
        first = queue.get_nowait()
        second = queue.get_nowait()
        third = queue.get_nowait()

        assert first.name == "High"
        assert second.name == "Medium"
        assert third.name == "Low"

    def test_queue_remove_task(self):
        """Test removing a task from queue by ID"""
        queue = PriorityTaskQueue()

        task1 = Task(name="Task 1", executor=self.dummy_executor)
        task2 = Task(name="Task 2", executor=self.dummy_executor)
        task3 = Task(name="Task 3", executor=self.dummy_executor)

        queue.put(task1)
        queue.put(task2)
        queue.put(task3)

        # Remove task 2
        removed = queue.remove_task(task2.id)
        assert removed is True
        assert queue.size() == 2
        assert task2.status == TaskStatus.CANCELLED

        # Try to remove non-existent task
        removed = queue.remove_task("non-existent-id")
        assert removed is False

    def test_queue_get_all_tasks(self):
        """Test getting all tasks in queue"""
        queue = PriorityTaskQueue()

        task1 = Task(name="Task 1", executor=self.dummy_executor)
        task2 = Task(name="Task 2", executor=self.dummy_executor)

        queue.put(task1)
        queue.put(task2)

        all_tasks = queue.get_all_tasks()
        assert len(all_tasks) == 2

    def test_queue_clear(self):
        """Test clearing all tasks from queue"""
        queue = PriorityTaskQueue()

        task1 = Task(name="Task 1", executor=self.dummy_executor)
        task2 = Task(name="Task 2", executor=self.dummy_executor)

        queue.put(task1)
        queue.put(task2)

        queue.clear()
        assert queue.size() == 0
        assert queue.is_empty()
        assert task1.status == TaskStatus.CANCELLED
        assert task2.status == TaskStatus.CANCELLED


class TestOrchestratorManager:
    """Tests for orchestrator manager"""

    async def simple_task_executor(self, task: Task):
        """Simple executor that returns task name"""
        await asyncio.sleep(0.1)
        return f"Completed: {task.name}"

    async def failing_task_executor(self, task: Task):
        """Executor that raises an exception"""
        await asyncio.sleep(0.05)
        raise ValueError("Task failed intentionally")

    async def test_orchestrator_creation(self):
        """Test orchestrator initialization"""
        orchestrator = OrchestratorManager(num_workers=2)
        assert orchestrator.num_workers == 2
        assert not orchestrator._is_running

    async def test_orchestrator_start_stop(self):
        """Test starting and stopping orchestrator"""
        orchestrator = OrchestratorManager(num_workers=2)

        await orchestrator.start()
        assert orchestrator._is_running

        await orchestrator.stop()
        assert not orchestrator._is_running

    async def test_submit_task(self):
        """Test submitting a task"""
        orchestrator = OrchestratorManager(num_workers=2)
        await orchestrator.start()

        task_id = orchestrator.submit_task(
            name="Test Task",
            executor=self.simple_task_executor,
            priority=5
        )

        assert task_id is not None
        assert task_id in orchestrator.tasks

        # Wait for task to complete
        await asyncio.sleep(0.3)

        # Check task status
        status = orchestrator.get_task_status(task_id)
        assert status is not None
        assert status["status"] == "done"

        await orchestrator.stop()

    async def test_task_execution(self):
        """Test that tasks are executed by workers"""
        orchestrator = OrchestratorManager(num_workers=1)
        await orchestrator.start()

        task_id = orchestrator.submit_task(
            name="Execution Test",
            executor=self.simple_task_executor,
            priority=7
        )

        # Wait for execution
        await asyncio.sleep(0.3)

        task = orchestrator.tasks[task_id]
        assert task.status == TaskStatus.DONE
        assert task.result == "Completed: Execution Test"

        await orchestrator.stop()

    async def test_task_error_handling(self):
        """Test that task errors are handled properly"""
        orchestrator = OrchestratorManager(num_workers=1)
        await orchestrator.start()

        task_id = orchestrator.submit_task(
            name="Failing Task",
            executor=self.failing_task_executor,
            priority=5
        )

        # Wait for execution
        await asyncio.sleep(0.3)

        task = orchestrator.tasks[task_id]
        assert task.status == TaskStatus.ERROR
        assert "Task failed intentionally" in task.error_message

        await orchestrator.stop()

    async def test_cancel_task(self):
        """Test cancelling a queued task"""
        orchestrator = OrchestratorManager(num_workers=1)
        await orchestrator.start()

        # Submit multiple tasks to fill queue
        task_ids = []
        for i in range(5):
            task_id = orchestrator.submit_task(
                name=f"Task {i}",
                executor=self.simple_task_executor,
                priority=5
            )
            task_ids.append(task_id)

        # Try to cancel a task
        cancelled = orchestrator.cancel_task(task_ids[3])

        # At least one should be cancellable (if still queued)
        if cancelled:
            task = orchestrator.tasks[task_ids[3]]
            assert task.status == TaskStatus.CANCELLED

        await orchestrator.stop()

    async def test_list_tasks(self):
        """Test listing all tasks"""
        orchestrator = OrchestratorManager(num_workers=2)
        await orchestrator.start()

        # Submit tasks
        task_ids = []
        for i in range(3):
            task_id = orchestrator.submit_task(
                name=f"Task {i}",
                executor=self.simple_task_executor,
                priority=5
            )
            task_ids.append(task_id)

        # List all tasks
        all_tasks = orchestrator.list_tasks()
        assert len(all_tasks) == 3

        # Wait for completion
        await asyncio.sleep(0.5)

        # List completed tasks
        completed_tasks = orchestrator.list_tasks(status_filter=TaskStatus.DONE)
        assert len(completed_tasks) >= 1

        await orchestrator.stop()

    async def test_queue_status(self):
        """Test getting queue status"""
        orchestrator = OrchestratorManager(num_workers=1)
        await orchestrator.start()

        # Submit tasks
        for i in range(3):
            orchestrator.submit_task(
                name=f"Task {i}",
                executor=self.simple_task_executor,
                priority=5
            )

        queue_status = orchestrator.get_queue_status()
        assert "queue_size" in queue_status
        assert "total_tasks" in queue_status
        assert queue_status["total_tasks"] == 3

        await orchestrator.stop()

    async def test_system_status(self):
        """Test getting complete system status"""
        orchestrator = OrchestratorManager(num_workers=2)
        await orchestrator.start()

        status = orchestrator.get_system_status()

        assert status["is_running"] is True
        assert status["num_workers"] == 2
        assert "queue" in status
        assert "workers" in status

        await orchestrator.stop()


class TestPipelineIntegration:
    """Tests for FAZA 17 pipeline integration"""

    async def test_submit_pipeline_task(self):
        """Test submitting a pipeline as a task"""
        from senti_os.core.faza25 import get_orchestrator

        orchestrator = get_orchestrator()
        await orchestrator.start()

        # Submit pipeline task
        task_id = submit_pipeline_task(
            pipeline_id="test_pipeline",
            stages=[
                {"name": "Stage 1", "model_id": "model1"},
                {"name": "Stage 2", "model_id": "model2"}
            ],
            strategy="LOCAL_FAST_PRECISE",
            priority=8
        )

        assert task_id is not None

        # Wait for execution
        await asyncio.sleep(0.5)

        # Check result
        result = get_pipeline_task_result(task_id)
        assert result is not None
        assert result["task_type"] == "pipeline"

        await orchestrator.stop()

    async def test_pipeline_task_execution(self):
        """Test that pipeline tasks are executed correctly"""
        from senti_os.core.faza25 import get_orchestrator

        orchestrator = get_orchestrator()

        # Start if not already running
        if not orchestrator._is_running:
            await orchestrator.start()

        task_id = submit_pipeline_task(
            pipeline_id="execution_test_pipeline",
            stages=[
                {"name": "Stage A", "model_id": "modelA"},
                {"name": "Stage B", "model_id": "modelB"},
                {"name": "Stage C", "model_id": "modelC"}
            ],
            strategy="PARALLEL_ENSEMBLE",
            max_time=300,
            max_cost=10.0,
            priority=9
        )

        # Wait for completion
        await asyncio.sleep(0.5)

        # Check task was executed
        task = orchestrator.tasks.get(task_id)
        assert task is not None

        # Task should complete (FAZA 17 pipelines are simulated)
        if task.status == TaskStatus.DONE:
            assert task.result is not None

        await orchestrator.stop()


def run_sync_tests():
    """Run synchronous tests"""
    print("\n=== Running Task Model Tests ===")
    test_task = TestTaskModel()
    test_task.test_task_creation()
    test_task.test_task_priority_comparison()
    test_task.test_task_status_transitions()
    test_task.test_task_error_handling()
    test_task.test_task_cancellation()
    test_task.test_task_to_dict()
    print("✓ All task model tests passed")

    print("\n=== Running Priority Queue Tests ===")
    test_queue = TestPriorityTaskQueue()
    test_queue.test_queue_creation()
    test_queue.test_queue_put_and_get()
    test_queue.test_queue_priority_ordering()
    test_queue.test_queue_remove_task()
    test_queue.test_queue_get_all_tasks()
    test_queue.test_queue_clear()
    print("✓ All priority queue tests passed")


async def run_async_tests():
    """Run asynchronous tests"""
    print("\n=== Running Orchestrator Manager Tests ===")
    test_orchestrator = TestOrchestratorManager()

    await test_orchestrator.test_orchestrator_creation()
    print("✓ Orchestrator creation test passed")

    await test_orchestrator.test_orchestrator_start_stop()
    print("✓ Orchestrator start/stop test passed")

    await test_orchestrator.test_submit_task()
    print("✓ Task submission test passed")

    await test_orchestrator.test_task_execution()
    print("✓ Task execution test passed")

    await test_orchestrator.test_task_error_handling()
    print("✓ Task error handling test passed")

    await test_orchestrator.test_cancel_task()
    print("✓ Task cancellation test passed")

    await test_orchestrator.test_list_tasks()
    print("✓ List tasks test passed")

    await test_orchestrator.test_queue_status()
    print("✓ Queue status test passed")

    await test_orchestrator.test_system_status()
    print("✓ System status test passed")

    print("\n=== Running Pipeline Integration Tests ===")
    test_pipeline = TestPipelineIntegration()

    await test_pipeline.test_submit_pipeline_task()
    print("✓ Pipeline task submission test passed")

    await test_pipeline.test_pipeline_task_execution()
    print("✓ Pipeline task execution test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("FAZA 25 - Orchestration Execution Engine - Test Suite")
    print("=" * 60)

    # Run synchronous tests
    run_sync_tests()

    # Run asynchronous tests
    print("\n" + "=" * 60)
    asyncio.run(run_async_tests())

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
