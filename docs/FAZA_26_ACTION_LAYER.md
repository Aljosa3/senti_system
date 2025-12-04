# FAZA 26 - Intelligent Action Layer

## Overview

FAZA 26 is the intelligent action layer for Senti OS that provides a high-level interface for processing user commands into orchestrated tasks. It sits on top of FAZA 25 (Orchestration Execution Engine) and provides natural language intent parsing, semantic planning, policy enforcement, and seamless task mapping.

**Key Capabilities:**
- Natural language command parsing with rule-based patterns
- Semantic task planning from high-level intents
- Policy enforcement (priority, resource limits, retry)
- Automatic mapping to FAZA 25 orchestrator tasks
- Comprehensive error handling and validation
- Batch command execution

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FAZA 26 - Action Layer                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Command: "analyze sentiment count=200 with plot"     │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐                                          │
│  │IntentParser  │ ──→ Intent + Parameters                  │
│  └──────────────┘                                          │
│         │                                                   │
│         ↓                                                   │
│  ┌─────────────────┐                                       │
│  │SemanticPlanner  │ ──→ Task Specifications               │
│  └─────────────────┘                                       │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐                                          │
│  │PolicyEngine  │ ──→ Policy-Applied Tasks                 │
│  └──────────────┘                                          │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐                                          │
│  │ActionMapper  │ ──→ FAZA 25 Task IDs                     │
│  └──────────────┘                                          │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────────────────────────┐                      │
│  │    FAZA 25 Orchestrator          │                      │
│  │  (Task Execution Engine)         │                      │
│  └──────────────────────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. IntentParser
- **Purpose**: Parse natural language commands into structured intents
- **Input**: Text command (e.g., "analyze sentiment count=200")
- **Output**: Intent + Parameters dictionary
- **Features**:
  - Rule-based pattern matching
  - Parameter extraction (numbers, strings, flags)
  - Boolean flag detection
  - Intent validation

#### 2. SemanticPlanner
- **Purpose**: Convert intents into actionable task sequences
- **Input**: Parsed intent dictionary
- **Output**: List of task specifications
- **Features**:
  - Multi-step workflow planning
  - Priority assignment
  - Metadata enrichment
  - Task dependency awareness

#### 3. PolicyEngine
- **Purpose**: Enforce execution policies and resource constraints
- **Input**: Task specifications
- **Output**: Policy-applied tasks
- **Features**:
  - Priority validation and clamping (0-10)
  - Heavy task limiting (max 2 parallel by default)
  - Retry policy injection
  - Task validation

#### 4. ActionMapper
- **Purpose**: Map planned tasks to FAZA 25 orchestrator
- **Input**: Policy-applied tasks
- **Output**: FAZA 25 task IDs
- **Features**:
  - Task executor creation
  - FAZA 25 integration
  - Async task submission
  - Result tracking

#### 5. ActionLayer
- **Purpose**: Main interface orchestrating the complete flow
- **Input**: User command string
- **Output**: Execution status with task IDs
- **Features**:
  - End-to-end pipeline orchestration
  - Error handling and recovery
  - Batch command execution
  - Command validation

## Installation & Setup

FAZA 26 is part of Senti OS core and requires FAZA 25 to be running.

### Dependencies
- Python 3.10+
- FAZA 25 (Orchestration Execution Engine)
- asyncio (standard library)

## Usage

### 1. Basic Command Execution

```python
import asyncio
from senti_os.core.faza26 import get_action_layer
from senti_os.core.faza25 import get_orchestrator

async def main():
    # Start FAZA 25 orchestrator
    orchestrator = get_orchestrator()
    await orchestrator.start()

    # Get action layer
    action_layer = get_action_layer()

    # Execute command
    result = await action_layer.execute_command(
        "analyze sentiment count=200 dataset=articles with plot"
    )

    print(result)
    # {
    #     "status": "ok",
    #     "intent": "analyze_sentiment",
    #     "tasks_submitted": ["uuid-1", "uuid-2", "uuid-3", "uuid-4"],
    #     "count": 4,
    #     "parameters": {"count": 200, "dataset": "articles", "generate_plot": true}
    # }

    # Stop orchestrator
    await orchestrator.stop()

asyncio.run(main())
```

### 2. Supported Commands

#### Sentiment Analysis
```python
# Basic sentiment analysis
result = await action_layer.execute_command("analyze sentiment")

# With parameters
result = await action_layer.execute_command(
    "analyze sentiment count=500 dataset=reviews with plot"
)

# Generated tasks:
# 1. fetch_data (priority: 7)
# 2. compute_sentiment (priority: 8)
# 3. aggregate_results (priority: 6)
# 4. generate_plot (priority: 5) - if requested
```

#### Computation
```python
# Generic computation
result = await action_layer.execute_command("compute statistics")

# Generated tasks:
# 1. compute (priority: 7)
```

#### Plot Generation
```python
# Generate plot
result = await action_layer.execute_command("generate plot format=png")

# Generated tasks:
# 1. generate_plot (priority: 5)
```

#### Data Processing
```python
# Process data
result = await action_layer.execute_command(
    "process data dataset=users save"
)

# Generated tasks:
# 1. load_data (priority: 7)
# 2. transform_data (priority: 6)
# 3. validate_data (priority: 5)
# 4. save_data (priority: 4) - if save flag present
```

#### Model Inference
```python
# Run model inference
result = await action_layer.execute_command("run model model=bert-large")

# Generated tasks:
# 1. load_model (priority: 8)
# 2. preprocess_input (priority: 7)
# 3. run_inference (priority: 9)
# 4. postprocess_output (priority: 6)
```

#### Pipeline Execution
```python
# Execute FAZA 17 pipeline
result = await action_layer.execute_command("run pipeline")

# Generated tasks:
# 1. execute_pipeline (priority: 9)
# This integrates with FAZA 17 Pipeline Manager via FAZA 25
```

### 3. Command Validation

```python
# Validate command without executing
validation = action_layer.validate_command(
    "analyze sentiment count=200"
)

print(validation)
# {
#     "valid": true,
#     "intent": "analyze_sentiment",
#     "planned_tasks": 3,
#     "parameters": {"count": 200},
#     "message": "Command is valid and will generate 3 tasks"
# }

# Invalid command
validation = action_layer.validate_command("invalid nonsense")
# {
#     "valid": false,
#     "message": "Could not determine intent from command: invalid nonsense"
# }
```

### 4. Batch Execution

```python
# Execute multiple commands
commands = [
    "analyze sentiment count=100",
    "generate plot format=png",
    "compute statistics"
]

result = await action_layer.execute_batch(commands)

print(result)
# {
#     "status": "batch_complete",
#     "total_commands": 3,
#     "successful": 3,
#     "failed": 0,
#     "results": [...]
# }
```

### 5. Status Monitoring

```python
# Get action layer status
status = action_layer.get_status()

print(status)
# {
#     "action_layer": "operational",
#     "parser_intents": ["analyze_sentiment", "compute", ...],
#     "planner_intents": ["analyze_sentiment", "compute", ...],
#     "policy_status": {
#         "max_parallel_heavy": 2,
#         "current_heavy_tasks": 0,
#         "heavy_quota_available": 2,
#         "default_retry_count": 1,
#         "priority_range": [0, 10]
#     },
#     "components": {...}
# }
```

## Command Syntax

### Parameter Formats

| Parameter | Format | Example |
|-----------|--------|---------|
| count | `count=<number>` | `count=200` |
| limit | `limit=<number>` | `limit=500` |
| dataset | `dataset=<name>` | `dataset=articles` |
| model | `model=<name>` | `model=bert-large` |
| file | `file=<path>` | `file=data.csv` |
| output | `output=<path>` | `output=result.json` |
| format | `format=<type>` | `format=png` |

### Boolean Flags

| Flag | Syntax | Example |
|------|--------|---------|
| plot | `with plot`, `plot`, `visualize` | `analyze sentiment with plot` |
| verbose | `verbose`, `--verbose`, `-v` | `compute verbose` |
| debug | `debug`, `--debug` | `process data debug` |
| save | `save`, `--save` | `transform data save` |

## Intent → Task Mapping

### analyze_sentiment
**Workflow**: Fetch → Compute → Aggregate → Plot (optional)

| Task | Priority | Type |
|------|----------|------|
| fetch_data | 7 | data_fetch |
| compute_sentiment | 8 | computation |
| aggregate_results | 6 | aggregation |
| generate_plot | 5 | visualization |

### compute
**Workflow**: Single computation task

| Task | Priority | Type |
|------|----------|------|
| compute | 7 | computation |

### generate_plot
**Workflow**: Single visualization task

| Task | Priority | Type |
|------|----------|------|
| generate_plot | 5 | visualization |

### process_data
**Workflow**: Load → Transform → Validate → Save (optional)

| Task | Priority | Type |
|------|----------|------|
| load_data | 7 | data_io |
| transform_data | 6 | transformation |
| validate_data | 5 | validation |
| save_data | 4 | data_io |

### run_model
**Workflow**: Load → Preprocess → Inference → Postprocess

| Task | Priority | Type |
|------|----------|------|
| load_model | 8 | model_io |
| preprocess_input | 7 | preprocessing |
| run_inference | 9 | inference |
| postprocess_output | 6 | postprocessing |

### run_pipeline
**Workflow**: Execute FAZA 17 pipeline

| Task | Priority | Type |
|------|----------|------|
| execute_pipeline | 9 | pipeline |

## Policy Rules

### Priority Rules
- **Range**: 0 (lowest) to 10 (highest)
- **Clamping**: Priorities outside range are clamped automatically
- **Default**: 5 for most tasks
- **Critical**: 8-10 for inference and critical operations

### Heavy Task Limiting
- **Definition**: Tasks of type: `computation`, `inference`, `model_io`, `data_io`
- **Limit**: Maximum 2 parallel heavy tasks (configurable)
- **Behavior**: When limit exceeded, priority reduced by 3 for excess tasks

### Retry Policy
- **Default**: 1 retry attempt
- **Auto-Enable**: Retry enabled for high-priority tasks (priority >= 8)
- **Injection**: Automatically added to all tasks

### Metadata Enrichment
All tasks receive:
- `batch_index`: Position in batch
- `policy_version`: Policy engine version
- `is_heavy_task`: Boolean indicator

## API Reference

### ActionLayer

#### `execute_command(command: str) -> Dict`
Execute a user command through the complete pipeline.

**Returns**:
```python
{
    "status": "ok" | "error",
    "intent": "analyze_sentiment",
    "tasks_submitted": ["id1", "id2", ...],
    "count": 4,
    "parameters": {...},
    "message": "..."
}
```

**Error Types**:
- `validation_error`: Command parsing failed
- `policy_rejection`: Task rejected by policy
- `runtime_error`: Orchestrator not running
- `internal_error`: Unexpected error

#### `execute_batch(commands: List[str]) -> Dict`
Execute multiple commands in batch.

#### `validate_command(command: str) -> Dict`
Validate command without executing.

#### `get_status() -> Dict`
Get current action layer status.

### IntentParser

#### `parse(text: str) -> Dict`
Parse command into structured intent.

#### `validate(parsed_intent: Dict) -> None`
Validate intent structure (raises ValueError if invalid).

#### `get_supported_intents() -> List[str]`
Get list of supported intents.

### SemanticPlanner

#### `plan(intent: Dict) -> List[Dict]`
Plan task execution from intent.

#### `get_supported_intents() -> List[str]`
Get list of supported intents.

### PolicyEngine

#### `apply_policies(task_list: List[Dict]) -> List[Dict]`
Apply policies to task list.

#### `validate_submission(task_spec: Dict) -> None`
Validate single task (raises RejectedTaskError if rejected).

#### `get_policy_status() -> Dict`
Get current policy status.

### ActionMapper

#### `async map_and_submit(planned_tasks: List[Dict]) -> List[str]`
Map planned tasks to FAZA 25 and submit.

**Returns**: List of task IDs

## Error Handling

### Validation Errors
```python
result = await action_layer.execute_command("invalid command")
# {
#     "status": "error",
#     "error_type": "validation_error",
#     "message": "Could not determine intent from command: invalid command"
# }
```

### Policy Rejections
```python
# Task with invalid priority
result = await action_layer.execute_command("...")
# {
#     "status": "error",
#     "error_type": "policy_rejection",
#     "message": "Priority 15 outside allowed range [0, 10]"
# }
```

### Runtime Errors
```python
# Orchestrator not running
result = await action_layer.execute_command("analyze sentiment")
# {
#     "status": "error",
#     "error_type": "runtime_error",
#     "message": "FAZA 25 Orchestrator is not running. Call start() first."
# }
```

## Integration with FAZA 25

FAZA 26 seamlessly integrates with FAZA 25 Orchestration Engine:

```python
# FAZA 26 submits tasks to FAZA 25
action_layer = get_action_layer()
result = await action_layer.execute_command("analyze sentiment")

# Tasks are now in FAZA 25 orchestrator
orchestrator = get_orchestrator()
for task_id in result["tasks_submitted"]:
    status = orchestrator.get_task_status(task_id)
    print(f"Task {task_id}: {status['status']}")
```

## Integration with FAZA 17

FAZA 26 can execute FAZA 17 pipelines through FAZA 25:

```python
# Execute pipeline via FAZA 26
result = await action_layer.execute_command("run pipeline")

# This internally uses FAZA 25's pipeline integration
from senti_os.core.faza25.pipeline_integration import submit_pipeline_task
```

## Examples

### Example 1: Sentiment Analysis with Monitoring

```python
import asyncio
from senti_os.core.faza26 import get_action_layer
from senti_os.core.faza25 import get_orchestrator

async def sentiment_analysis_example():
    # Setup
    orchestrator = get_orchestrator()
    await orchestrator.start()
    action_layer = get_action_layer()

    # Execute command
    result = await action_layer.execute_command(
        "analyze sentiment count=500 dataset=reviews with plot"
    )

    if result["status"] == "ok":
        print(f"Submitted {result['count']} tasks")

        # Monitor progress
        for task_id in result["tasks_submitted"]:
            status = orchestrator.get_task_status(task_id)
            print(f"Task: {status['name']} - Status: {status['status']}")

    # Cleanup
    await orchestrator.stop()

asyncio.run(sentiment_analysis_example())
```

### Example 2: Batch Processing

```python
async def batch_processing_example():
    orchestrator = get_orchestrator()
    await orchestrator.start()
    action_layer = get_action_layer()

    # Batch commands
    commands = [
        "analyze sentiment count=100 dataset=tweets",
        "analyze sentiment count=100 dataset=reviews",
        "analyze sentiment count=100 dataset=articles with plot"
    ]

    # Execute batch
    result = await action_layer.execute_batch(commands)

    print(f"Total: {result['total_commands']}")
    print(f"Successful: {result['successful']}")
    print(f"Failed: {result['failed']}")

    # Check individual results
    for i, cmd_result in enumerate(result['results']):
        print(f"Command {i+1}: {cmd_result['status']}")

    await orchestrator.stop()

asyncio.run(batch_processing_example())
```

### Example 3: Command Validation

```python
def validation_example():
    action_layer = get_action_layer()

    # Validate before execution
    commands = [
        "analyze sentiment count=200",
        "invalid command",
        "compute statistics"
    ]

    for cmd in commands:
        validation = action_layer.validate_command(cmd)
        print(f"Command: {cmd}")
        print(f"Valid: {validation['valid']}")
        if validation['valid']:
            print(f"Will generate {validation['planned_tasks']} tasks")
        else:
            print(f"Error: {validation['message']}")
        print()

validation_example()
```

## Best Practices

### 1. Command Design
- Use clear, natural language
- Specify parameters explicitly
- Use flags for optional features
- Validate commands before execution

### 2. Error Handling
```python
result = await action_layer.execute_command(command)

if result["status"] == "error":
    error_type = result["error_type"]
    if error_type == "validation_error":
        # Handle parsing error
        print(f"Invalid command: {result['message']}")
    elif error_type == "policy_rejection":
        # Handle policy rejection
        print(f"Policy rejected: {result['message']}")
    elif error_type == "runtime_error":
        # Handle runtime error
        print(f"Runtime error: {result['message']}")
```

### 3. Batch Processing
- Use batch execution for multiple commands
- Check individual results
- Handle partial failures gracefully

### 4. Monitoring
- Check action layer status regularly
- Monitor FAZA 25 task execution
- Track policy limits and quotas

## Performance Characteristics

### Latency
- **Parsing**: ~1ms per command
- **Planning**: ~2-5ms depending on workflow
- **Policy Application**: ~1ms per task
- **Submission**: ~1ms per task to FAZA 25

### Throughput
- **Single Commands**: 100-200 commands/second
- **Batch Commands**: Higher throughput with batching
- **Concurrent Execution**: Limited by FAZA 25 workers

### Resource Usage
- **Memory**: ~50KB base + command data
- **CPU**: Minimal overhead, mostly FAZA 25
- **I/O**: Async I/O for non-blocking operations

## Testing

Run comprehensive test suite:

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 senti_os/core/faza26/test_faza26.py
```

Test coverage:
- IntentParser (9 tests)
- SemanticPlanner (7 tests)
- PolicyEngine (9 tests)
- ActionMapper (4 tests)
- ActionLayer (9 tests)

**Total: 38 comprehensive tests**

## Troubleshooting

### Command Not Recognized
```python
# Problem: "Could not determine intent from command"
# Solution: Check supported intents
intents = action_layer.parser.get_supported_intents()
print(intents)
```

### Task Rejected by Policy
```python
# Problem: "Priority outside allowed range"
# Solution: Use valid priority range (0-10)
# Or check policy status
status = action_layer.policy_engine.get_policy_status()
print(status["priority_range"])
```

### Orchestrator Not Running
```python
# Problem: "FAZA 25 Orchestrator is not running"
# Solution: Start orchestrator before executing commands
orchestrator = get_orchestrator()
await orchestrator.start()
```

### Heavy Task Quota Exceeded
```python
# Problem: "Heavy task quota exceeded"
# Solution: Check policy status and adjust
status = action_layer.policy_engine.get_policy_status()
print(f"Heavy tasks: {status['current_heavy_tasks']}/{status['max_parallel_heavy']}")
```

## Future Enhancements

Planned features for FAZA 26:

1. **LLM Integration**: GPT-4/Claude for advanced parsing
2. **Context Awareness**: Multi-turn conversation context
3. **Custom Intents**: User-defined intent registration
4. **Workflow Templates**: Pre-defined workflow patterns
5. **Natural Language**: More flexible command syntax
6. **Learning**: Adapt to user preferences
7. **Autocomplete**: Command suggestions
8. **History**: Command history and replay

## Version History

- **v1.0.0** (2024-12-04): Initial implementation
  - IntentParser with rule-based patterns
  - SemanticPlanner with 6 intent mappings
  - PolicyEngine with priority, limits, retry
  - ActionMapper with FAZA 25 integration
  - ActionLayer main interface
  - Comprehensive test suite (38 tests)

## Contributing

FAZA 26 is part of Senti OS core. For modifications:

1. Update relevant modules in `senti_os/core/faza26/`
2. Add tests to `senti_os/core/faza26/test_faza26.py`
3. Update documentation
4. Run test suite to verify

## License

Part of Senti System - Proprietary

---

**FAZA 26 - Intelligent Action Layer**
*Natural language interface for intelligent task orchestration*
