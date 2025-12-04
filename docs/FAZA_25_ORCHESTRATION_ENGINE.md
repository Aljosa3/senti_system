# FAZA 25 - Orchestration Execution Engine (OEE)

## Overview

FAZA 25 is the central orchestration and execution engine for Senti OS. It provides a sophisticated task management system that coordinates execution of complex operations across all FAZA modules (16-24), with special integration for FAZA 17 Pipeline Manager.

**Key Capabilities:**
- Asynchronous task execution with configurable worker pool
- Priority-based task queuing using heap-based priority queue
- Thread-safe operations for concurrent task submission
- Event-driven task lifecycle management
- Pipeline integration with FAZA 17
- Real-time system monitoring and status tracking

## Architecture

### Core Components

```
FAZA 25 Architecture
├── Task Model (task_model.py)
│   ├── Task: Core task data structure
│   └── TaskStatus: Lifecycle states
│
├── Priority Queue (task_queue.py)
│   └── PriorityTaskQueue: Thread-safe heapq implementation
│
├── Workers (worker.py)
│   ├── TaskWorker: Individual worker for task execution
│   └── WorkerPool: Manages multiple workers
│
├── Orchestrator (orchestrator.py)
│   └── OrchestratorManager: Main API and coordination
│
└── Pipeline Integration (pipeline_integration.py)
    └── Integration with FAZA 17 Pipeline Manager
```

### Task Lifecycle

```
┌──────────┐
│  QUEUED  │ ←─ Task submitted
└────┬─────┘
     │
     ↓
┌──────────┐
│ RUNNING  │ ←─ Worker picks up task
└────┬─────┘
     │
     ├────────┐
     ↓        ↓
┌──────┐  ┌───────┐
│ DONE │  │ ERROR │
└──────┘  └───────┘
     ↑
     │
┌───────────┐
│ CANCELLED │ ←─ Task cancelled before/during execution
└───────────┘
```

## Installation & Setup

FAZA 25 is part of Senti OS core and requires no additional installation.

### Dependencies
- Python 3.10+
- asyncio (standard library)
- threading (standard library)
- heapq (standard library)

## Usage

### 1. Basic Task Execution

```python
import asyncio
from senti_os.core.faza25 import get_orchestrator, Task

# Define a task executor
async def my_task_executor(task: Task):
    """Your task logic here"""
    print(f"Executing: {task.name}")
    # Do work...
    return "result"

async def main():
    # Get orchestrator instance
    orchestrator = get_orchestrator()

    # Start orchestrator
    await orchestrator.start()

    # Submit task
    task_id = orchestrator.submit_task(
        name="My Task",
        executor=my_task_executor,
        priority=5,
        task_type="custom",
        context={"key": "value"}
    )

    # Wait for completion
    await asyncio.sleep(1)

    # Get result
    status = orchestrator.get_task_status(task_id)
    print(f"Status: {status}")

    # Stop orchestrator
    await orchestrator.stop()

asyncio.run(main())
```

### 2. Priority-Based Execution

Tasks with higher priority (0-10) are executed first:

```python
# High priority task (executed first)
high_priority_task = orchestrator.submit_task(
    name="Critical Task",
    executor=my_executor,
    priority=9
)

# Low priority task (executed later)
low_priority_task = orchestrator.submit_task(
    name="Background Task",
    executor=my_executor,
    priority=2
)
```

### 3. Pipeline Integration (FAZA 17)

Execute FAZA 17 pipelines as orchestrated tasks:

```python
from senti_os.core.faza25 import submit_pipeline_task

# Submit pipeline
task_id = submit_pipeline_task(
    pipeline_id="my_pipeline",
    stages=[
        {"name": "Stage 1", "model_id": "model1"},
        {"name": "Stage 2", "model_id": "model2"}
    ],
    strategy="LOCAL_FAST_PRECISE",
    max_time=300,
    max_cost=10.0,
    priority=8
)

# Get result
result = get_pipeline_task_result(task_id)
```

### 4. System Monitoring

```python
# Get complete system status
status = orchestrator.get_system_status()
print(f"Workers: {status['num_workers']}")
print(f"Queue size: {status['queue']['queue_size']}")
print(f"Tasks by status: {status['queue']['tasks_by_status']}")

# List all tasks
all_tasks = orchestrator.list_tasks()

# Filter by status
from senti_os.core.faza25 import TaskStatus
completed = orchestrator.list_tasks(status_filter=TaskStatus.DONE)

# Filter by type
pipelines = orchestrator.list_tasks(task_type_filter="pipeline")
```

### 5. Task Cancellation

```python
# Submit task
task_id = orchestrator.submit_task(...)

# Cancel task (only works if still queued)
cancelled = orchestrator.cancel_task(task_id)
if cancelled:
    print("Task cancelled successfully")
```

## API Reference

### OrchestratorManager

Main orchestration manager class.

#### Methods

**`__init__(num_workers: int = 3)`**
- Initialize orchestrator with specified number of workers
- Default: 3 workers

**`async start()`**
- Start the orchestrator and all workers
- Must be called before submitting tasks

**`async stop()`**
- Stop the orchestrator gracefully
- Waits for current tasks to complete

**`submit_task(name, executor, priority=5, task_type="generic", context=None) -> str`**
- Submit a new task for execution
- Returns: Task ID
- Parameters:
  - `name`: Human-readable task name
  - `executor`: Async function that executes the task
  - `priority`: Priority level (0-10, higher = more important)
  - `task_type`: Type of task (e.g., "pipeline", "generic")
  - `context`: Additional parameters for task execution

**`cancel_task(task_id: str) -> bool`**
- Cancel a task by ID
- Returns: True if cancelled, False if not found or already running

**`get_task_status(task_id: str) -> Optional[Dict]`**
- Get status of a specific task
- Returns: Task status dictionary or None

**`list_tasks(status_filter=None, task_type_filter=None) -> List[Dict]`**
- List all tasks with optional filters
- Returns: List of task status dictionaries

**`get_queue_status() -> Dict`**
- Get current queue status
- Returns: Dictionary with queue information

**`get_system_status() -> Dict`**
- Get complete system status
- Returns: Orchestrator, queue, and worker status

**`clear_completed_tasks(keep_recent: int = 100) -> int`**
- Clear old completed tasks from registry
- Returns: Number of tasks cleared

### Task Model

#### Task Properties

- `id`: Unique task identifier (UUID)
- `name`: Human-readable task name
- `status`: Current execution status (TaskStatus enum)
- `priority`: Priority level (0-10)
- `created_at`: Task creation timestamp
- `started_at`: Execution start timestamp
- `completed_at`: Completion timestamp
- `error_message`: Error description (if failed)
- `context`: Additional parameters
- `task_type`: Type of task
- `executor`: Async function to execute
- `result`: Task execution result

#### TaskStatus Enum

- `QUEUED`: Task is waiting in queue
- `RUNNING`: Task is being executed
- `DONE`: Task completed successfully
- `ERROR`: Task failed with error
- `CANCELLED`: Task was cancelled

## Integration with Other FAZA Modules

### FAZA 17 - Pipeline Manager

FAZA 25 provides seamless integration with FAZA 17:

```python
from senti_os.core.faza25 import submit_pipeline_task

# Submit FAZA 17 pipeline as FAZA 25 task
task_id = submit_pipeline_task(
    pipeline_id="ai_pipeline",
    stages=[...],
    strategy="LOCAL_FAST_PRECISE",
    priority=9
)
```

Supported pipeline strategies:
- `LOCAL_FAST_PRECISE`
- `PARALLEL_ENSEMBLE`
- `SEQUENTIAL_VALIDATION`
- `COST_OPTIMIZED`
- `QUALITY_FIRST`

### Future FAZA Module Integration

FAZA 25 is designed to orchestrate tasks from FAZA 16-24:

- **FAZA 16**: Step planning and execution
- **FAZA 17**: Pipeline management (✓ implemented)
- **FAZA 18**: Priority management
- **FAZA 19**: Reliability tracking
- **FAZA 20**: Model ensemble coordination
- **FAZA 21**: Explainability generation
- **FAZA 22**: Boot manager coordination
- **FAZA 23**: Dashboard updates
- **FAZA 24**: Web server request handling

## Performance Characteristics

### Scalability

- **Workers**: Configurable (default: 3)
- **Queue**: Unlimited size (memory-limited)
- **Throughput**: Dependent on task complexity
- **Latency**: Minimal overhead (<1ms for task submission)

### Thread Safety

All operations are thread-safe:
- Task submission
- Queue operations
- Status queries
- Cancellation

### Resource Usage

- **Memory**: ~100KB base + task data
- **CPU**: Minimal overhead, scales with worker count
- **I/O**: Async I/O for non-blocking operations

## Examples

See `examples/faza25_demo.py` for comprehensive demonstrations:

1. Basic task submission and execution
2. Priority-based task execution
3. Pipeline integration with FAZA 17
4. System status monitoring

Run the demo:

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 examples/faza25_demo.py
```

## Testing

Run comprehensive test suite:

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 tests/test_faza25.py
```

Test coverage:
- Task model and status transitions
- Priority queue operations
- Worker execution and error handling
- Orchestrator API
- Pipeline integration
- System monitoring

## Best Practices

### 1. Task Design

- Keep tasks focused and single-purpose
- Use async/await for I/O-bound operations
- Store results in task.result for retrieval
- Use context for passing parameters

### 2. Priority Management

- Reserve 9-10 for critical tasks
- Use 5 for normal priority
- Use 1-3 for background tasks
- Don't abuse high priorities

### 3. Error Handling

```python
async def robust_task_executor(task: Task):
    try:
        # Your logic here
        result = do_work()
        return result
    except Exception as e:
        # Error will be captured automatically
        raise
```

### 4. Resource Management

```python
# Always start and stop orchestrator
orchestrator = get_orchestrator()
await orchestrator.start()

try:
    # Submit tasks...
    pass
finally:
    await orchestrator.stop()
```

### 5. Monitoring

```python
# Periodic monitoring
while True:
    status = orchestrator.get_queue_status()
    if status['queue_size'] > 100:
        logger.warning("Queue backlog detected")
    await asyncio.sleep(5)
```

## Troubleshooting

### Task Not Executing

1. Check orchestrator is started: `orchestrator._is_running`
2. Verify workers are running: `orchestrator.get_worker_status()`
3. Check task status: `orchestrator.get_task_status(task_id)`

### Task Failed with Error

```python
status = orchestrator.get_task_status(task_id)
if status['status'] == 'error':
    print(f"Error: {status['error_message']}")
```

### Queue Backlog

- Increase worker count: `OrchestratorManager(num_workers=10)`
- Optimize task executors
- Clear completed tasks: `orchestrator.clear_completed_tasks()`

## Future Enhancements

Planned features for FAZA 25:

1. **Task Dependencies**: DAG-based task execution
2. **Scheduling**: Cron-like task scheduling
3. **Retries**: Automatic retry on failure
4. **Callbacks**: Event-based task callbacks
5. **Persistence**: Task state persistence
6. **Distributed**: Multi-node orchestration
7. **Metrics**: Detailed performance metrics
8. **Quotas**: Resource quota management

## Version History

- **v1.0.0** (2024-12-04): Initial implementation
  - Core task model and lifecycle
  - Priority-based queue with heapq
  - Async worker pool
  - Orchestrator manager API
  - FAZA 17 pipeline integration
  - Comprehensive test suite

## Contributing

FAZA 25 is part of Senti OS core. For modifications:

1. Update relevant modules in `senti_os/core/faza25/`
2. Add tests to `tests/test_faza25.py`
3. Update documentation
4. Run test suite to verify

## License

Part of Senti System - Proprietary

---

**FAZA 25 - Orchestration Execution Engine**
*Coordinating the execution of complex operations across Senti OS*
