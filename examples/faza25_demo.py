"""
FAZA 25 - Orchestration Execution Engine Demo

Demonstrates the usage of FAZA 25 OEE for task orchestration,
including basic tasks, priority handling, and pipeline integration.
"""

import asyncio
import logging
from senti_os.core.faza25 import (
    get_orchestrator,
    submit_pipeline_task,
    Task
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Example task executors
async def simple_computation_task(task: Task):
    """Simple computation task"""
    logger.info(f"Starting computation: {task.name}")
    await asyncio.sleep(0.5)
    result = task.context.get("value", 0) * 2
    logger.info(f"Computation complete: {result}")
    return result


async def data_processing_task(task: Task):
    """Data processing task"""
    logger.info(f"Processing data: {task.name}")
    data = task.context.get("data", [])
    await asyncio.sleep(0.3)
    processed = [item.upper() if isinstance(item, str) else item for item in data]
    logger.info(f"Processed {len(processed)} items")
    return processed


async def model_inference_task(task: Task):
    """Simulated ML model inference"""
    logger.info(f"Running model inference: {task.name}")
    model_name = task.context.get("model", "default")
    await asyncio.sleep(0.8)
    logger.info(f"Model {model_name} inference complete")
    return {"model": model_name, "confidence": 0.95, "prediction": "positive"}


async def demo_basic_tasks():
    """Demo 1: Basic task submission and execution"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Task Submission and Execution")
    print("="*70)

    orchestrator = get_orchestrator()
    await orchestrator.start()

    # Submit multiple tasks
    task1 = orchestrator.submit_task(
        name="Computation Task",
        executor=simple_computation_task,
        priority=5,
        context={"value": 42}
    )

    task2 = orchestrator.submit_task(
        name="Data Processing Task",
        executor=data_processing_task,
        priority=7,
        context={"data": ["hello", "world", "faza25"]}
    )

    task3 = orchestrator.submit_task(
        name="Model Inference Task",
        executor=model_inference_task,
        priority=3,
        context={"model": "gpt-4"}
    )

    print(f"Submitted 3 tasks: {task1[:8]}, {task2[:8]}, {task3[:8]}")

    # Wait for completion
    await asyncio.sleep(2)

    # Check results
    for task_id in [task1, task2, task3]:
        status = orchestrator.get_task_status(task_id)
        print(f"Task {task_id[:8]}: {status['status']} - {status['name']}")
        if status['status'] == 'done':
            print(f"  → Result available: {status['has_result']}")

    await orchestrator.stop()


async def demo_priority_handling():
    """Demo 2: Priority-based task execution"""
    print("\n" + "="*70)
    print("DEMO 2: Priority-Based Task Execution")
    print("="*70)

    orchestrator = get_orchestrator()
    await orchestrator.start()

    # Submit tasks with different priorities
    tasks = []
    priorities = [3, 8, 1, 9, 5, 2, 7]

    for i, priority in enumerate(priorities):
        task_id = orchestrator.submit_task(
            name=f"Task P{priority}",
            executor=simple_computation_task,
            priority=priority,
            context={"value": i}
        )
        tasks.append((task_id, priority))
        print(f"Submitted: Task P{priority} (id: {task_id[:8]})")

    print("\nHigher priority tasks should complete first...")
    await asyncio.sleep(2)

    print("\nExecution order:")
    all_tasks = orchestrator.list_tasks()
    completed = [t for t in all_tasks if t['status'] == 'done']
    for i, task in enumerate(completed, 1):
        print(f"{i}. {task['name']} (Priority: {task['priority']})")

    await orchestrator.stop()


async def demo_pipeline_integration():
    """Demo 3: Pipeline integration with FAZA 17"""
    print("\n" + "="*70)
    print("DEMO 3: Pipeline Integration with FAZA 17")
    print("="*70)

    orchestrator = get_orchestrator()
    await orchestrator.start()

    # Submit a pipeline task
    task_id = submit_pipeline_task(
        pipeline_id="demo_pipeline",
        stages=[
            {"name": "Data Ingestion", "model_id": "local_model_1"},
            {"name": "Feature Engineering", "model_id": "local_model_2"},
            {"name": "Model Training", "model_id": "cloud_model_1"},
            {"name": "Evaluation", "model_id": "local_model_3"}
        ],
        strategy="LOCAL_FAST_PRECISE",
        max_time=300,
        max_cost=5.0,
        priority=9
    )

    print(f"Submitted pipeline task: {task_id[:8]}")
    print("Pipeline stages: Data Ingestion → Feature Engineering → Training → Evaluation")

    # Wait for pipeline to complete
    await asyncio.sleep(1)

    # Get pipeline result
    result = orchestrator.get_task_status(task_id)
    print(f"\nPipeline Status: {result['status']}")

    if result['status'] == 'done':
        print("Pipeline completed successfully!")
        print(f"  → Has result: {result['has_result']}")

    await orchestrator.stop()


async def demo_system_monitoring():
    """Demo 4: System status and monitoring"""
    print("\n" + "="*70)
    print("DEMO 4: System Status and Monitoring")
    print("="*70)

    orchestrator = get_orchestrator()
    await orchestrator.start()

    # Submit multiple tasks
    for i in range(5):
        orchestrator.submit_task(
            name=f"Background Task {i+1}",
            executor=simple_computation_task,
            priority=5,
            context={"value": i * 10}
        )

    print("Submitted 5 background tasks\n")

    # Monitor system status
    for _ in range(3):
        status = orchestrator.get_system_status()

        print(f"System Status:")
        print(f"  Running: {status['is_running']}")
        print(f"  Workers: {status['num_workers']}")
        print(f"  Queue size: {status['queue']['queue_size']}")
        print(f"  Total tasks: {status['queue']['total_tasks']}")
        print(f"  Status breakdown:")
        for status_name, count in status['queue']['tasks_by_status'].items():
            if count > 0:
                print(f"    - {status_name}: {count}")

        await asyncio.sleep(0.5)
        print()

    await orchestrator.stop()


async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("FAZA 25 - Orchestration Execution Engine")
    print("Demo Suite")
    print("="*70)

    await demo_basic_tasks()
    await asyncio.sleep(0.5)

    await demo_priority_handling()
    await asyncio.sleep(0.5)

    await demo_pipeline_integration()
    await asyncio.sleep(0.5)

    await demo_system_monitoring()

    print("\n" + "="*70)
    print("All demos completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
