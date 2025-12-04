"""
FAZA 26 - Intelligent Action Layer Demo

Demonstrates the usage of FAZA 26 for natural language command processing,
semantic planning, policy enforcement, and integration with FAZA 25.
"""

import asyncio
import logging
from senti_os.core.faza26 import get_action_layer
from senti_os.core.faza25 import get_orchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_commands():
    """Demo 1: Basic command execution"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Command Execution")
    print("="*70)

    orchestrator = get_orchestrator()
    await orchestrator.start()

    action_layer = get_action_layer()

    # Example commands
    commands = [
        "analyze sentiment count=200 dataset=articles",
        "compute statistics",
        "generate plot format=png"
    ]

    for command in commands:
        print(f"\nExecuting: {command}")
        result = await action_layer.execute_command(command)

        if result["status"] == "ok":
            print(f"✓ Success: {result['intent']}")
            print(f"  Tasks submitted: {result['count']}")
            print(f"  Task IDs: {[tid[:8] for tid in result['tasks_submitted']]}")
        else:
            print(f"✗ Error: {result['message']}")

    await orchestrator.stop()


async def demo_sentiment_analysis_workflow():
    """Demo 2: Sentiment analysis with plot generation"""
    print("\n" + "="*70)
    print("DEMO 2: Sentiment Analysis Workflow")
    print("="*70)

    orchestrator = get_orchestrator()
    await orchestrator.start()

    action_layer = get_action_layer()

    # Execute sentiment analysis with plot
    command = "analyze sentiment count=500 dataset=reviews with plot"
    print(f"\nCommand: {command}")

    result = await action_layer.execute_command(command)

    if result["status"] == "ok":
        print(f"\n✓ Workflow started successfully")
        print(f"Intent: {result['intent']}")
        print(f"Parameters: {result['parameters']}")
        print(f"Tasks submitted: {result['count']}")

        # Monitor task execution
        print("\nTask Execution Flow:")
        for i, task_id in enumerate(result['tasks_submitted'], 1):
            await asyncio.sleep(0.3)  # Wait for task to start
            status = orchestrator.get_task_status(task_id)
            print(f"  {i}. {status['name']} (Priority: {status['priority']}) - {status['status']}")

    await orchestrator.stop()


async def demo_policy_enforcement():
    """Demo 3: Policy enforcement and heavy task limiting"""
    print("\n" + "="*70)
    print("DEMO 3: Policy Enforcement")
    print("="*70)

    orchestrator = get_orchestrator()
    await orchestrator.start()

    action_layer = get_action_layer()

    # Check policy status
    status = action_layer.get_status()
    print("\nPolicy Configuration:")
    print(f"  Max parallel heavy tasks: {status['policy_status']['max_parallel_heavy']}")
    print(f"  Default retry count: {status['policy_status']['default_retry_count']}")
    print(f"  Priority range: {status['policy_status']['priority_range']}")

    # Execute multiple compute-intensive tasks
    commands = [
        "run model model=bert-base",
        "run model model=gpt-2",
        "run model model=t5-large"
    ]

    print("\nSubmitting multiple heavy tasks:")
    for command in commands:
        print(f"  → {command}")
        result = await action_layer.execute_command(command)
        if result["status"] == "ok":
            print(f"    ✓ Submitted {result['count']} tasks")

    # Check queue status
    await asyncio.sleep(0.5)
    queue_status = orchestrator.get_queue_status()
    print(f"\nQueue Status:")
    print(f"  Total tasks: {queue_status['total_tasks']}")
    print(f"  By status: {queue_status['tasks_by_status']}")

    await orchestrator.stop()


async def demo_batch_execution():
    """Demo 4: Batch command execution"""
    print("\n" + "="*70)
    print("DEMO 4: Batch Command Execution")
    print("="*70)

    orchestrator = get_orchestrator()
    await orchestrator.start()

    action_layer = get_action_layer()

    # Batch of commands
    commands = [
        "analyze sentiment count=100 dataset=tweets",
        "analyze sentiment count=100 dataset=reviews",
        "analyze sentiment count=100 dataset=articles with plot",
        "generate plot format=svg",
        "compute statistics"
    ]

    print(f"\nExecuting batch of {len(commands)} commands...")

    result = await action_layer.execute_batch(commands)

    print(f"\nBatch Execution Complete:")
    print(f"  Total commands: {result['total_commands']}")
    print(f"  Successful: {result['successful']}")
    print(f"  Failed: {result['failed']}")

    # Show individual results
    print("\nIndividual Results:")
    for i, cmd_result in enumerate(result['results'], 1):
        if cmd_result['status'] == 'ok':
            print(f"  {i}. ✓ {cmd_result['intent']} ({cmd_result['count']} tasks)")
        else:
            print(f"  {i}. ✗ Error: {cmd_result['message']}")

    await orchestrator.stop()


def demo_command_validation():
    """Demo 5: Command validation"""
    print("\n" + "="*70)
    print("DEMO 5: Command Validation")
    print("="*70)

    action_layer = get_action_layer()

    # Test various commands
    test_commands = [
        "analyze sentiment count=200",
        "invalid nonsense command",
        "compute statistics",
        "xyz abc def",
        "generate plot format=png output=chart.png"
    ]

    print("\nValidating commands (without execution):")
    for command in test_commands:
        validation = action_layer.validate_command(command)

        print(f"\nCommand: {command}")
        if validation['valid']:
            print(f"  ✓ Valid")
            print(f"    Intent: {validation['intent']}")
            print(f"    Will generate {validation['planned_tasks']} tasks")
            if validation.get('parameters'):
                print(f"    Parameters: {validation['parameters']}")
        else:
            print(f"  ✗ Invalid")
            print(f"    Error: {validation['message']}")


async def demo_error_handling():
    """Demo 6: Error handling"""
    print("\n" + "="*70)
    print("DEMO 6: Error Handling")
    print("="*70)

    # Don't start orchestrator to demonstrate error handling
    action_layer = get_action_layer()

    print("\n1. Testing with orchestrator not running:")
    result = await action_layer.execute_command("analyze sentiment")
    print(f"   Status: {result['status']}")
    print(f"   Error type: {result.get('error_type', 'N/A')}")
    print(f"   Message: {result.get('message', 'N/A')}")

    print("\n2. Testing with invalid command:")
    orchestrator = get_orchestrator()
    await orchestrator.start()

    result = await action_layer.execute_command("this is completely invalid")
    print(f"   Status: {result['status']}")
    print(f"   Error type: {result.get('error_type', 'N/A')}")
    print(f"   Message: {result.get('message', 'N/A')}")

    print("\n3. Testing with empty command:")
    result = await action_layer.execute_command("")
    print(f"   Status: {result['status']}")
    print(f"   Error type: {result.get('error_type', 'N/A')}")
    print(f"   Message: {result.get('message', 'N/A')}")

    await orchestrator.stop()


async def demo_supported_intents():
    """Demo 7: Supported intents and capabilities"""
    print("\n" + "="*70)
    print("DEMO 7: Supported Intents and Capabilities")
    print("="*70)

    action_layer = get_action_layer()

    # Get system status
    status = action_layer.get_status()

    print("\nSupported Intents:")
    for intent in status['parser_intents']:
        print(f"  • {intent}")

    print("\nComponents:")
    for component, name in status['components'].items():
        print(f"  • {component}: {name}")

    print("\nPolicy Status:")
    policy = status['policy_status']
    print(f"  • Max parallel heavy tasks: {policy['max_parallel_heavy']}")
    print(f"  • Current heavy tasks: {policy['current_heavy_tasks']}")
    print(f"  • Heavy quota available: {policy['heavy_quota_available']}")
    print(f"  • Default retry count: {policy['default_retry_count']}")
    print(f"  • Priority range: {policy['priority_range']}")


async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("FAZA 26 - Intelligent Action Layer")
    print("Demo Suite")
    print("="*70)

    await demo_basic_commands()
    await asyncio.sleep(0.5)

    await demo_sentiment_analysis_workflow()
    await asyncio.sleep(0.5)

    await demo_policy_enforcement()
    await asyncio.sleep(0.5)

    await demo_batch_execution()
    await asyncio.sleep(0.5)

    demo_command_validation()
    await asyncio.sleep(0.5)

    await demo_error_handling()
    await asyncio.sleep(0.5)

    await demo_supported_intents()

    print("\n" + "="*70)
    print("All demos completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
