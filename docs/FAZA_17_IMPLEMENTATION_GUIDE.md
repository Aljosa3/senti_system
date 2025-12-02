# FAZA 17 Implementation Guide

**Version:** 1.0.0
**SENTI OS - Multi-Model Orchestration Layer**

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation & Setup](#installation--setup)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Best Practices](#best-practices)
6. [Examples & Recipes](#examples--recipes)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)
9. [Integration Patterns](#integration-patterns)
10. [API Reference](#api-reference)

---

## Quick Start

### Minimal Example

```python
from senti_os.core.faza17 import (
    create_orchestration_manager,
    OrchestrationRequest,
    Priority,
)

# 1. Create orchestration manager
manager = create_orchestration_manager()

# 2. Create request
request = OrchestrationRequest(
    request_id="task_001",
    task_description="Analyze customer feedback and generate insights",
    priority=Priority.HIGH,
)

# 3. Submit and process
manager.submit_task(request)
result = manager.process_next_task()

# 4. Access results
print(f"Status: {result.status.value}")
print(f"Output: {result.final_output}")
print(f"Quality: {result.quality_score:.2f}")
print(f"Cost: ${result.total_cost:.2f}")
```

### Expected Output

```
Status: completed
Output: Based on the customer feedback analysis, key insights include...
Quality: 0.85
Cost: $0.30
```

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- SENTI OS core system installed
- FAZA 16 (LLM Control Layer) installed and configured

### Installation

FAZA 17 is included with SENTI OS core. No separate installation needed.

### Verification

```bash
# Verify installation
python3 -c "from senti_os.core.faza17 import get_info; import json; print(json.dumps(get_info(), indent=2))"
```

Expected output:
```json
{
  "name": "FAZA 17 - Multi-Model Orchestration Layer",
  "version": "1.0.0",
  "author": "SENTI OS Team",
  "components": [
    "Orchestration Manager",
    "Step Planner",
    "Priority Queue",
    "Model Ensemble Engine",
    "Pipeline Manager",
    "Reliability Feedback Loop",
    "Explainability Engine"
  ]
}
```

### Environment Configuration

```bash
# Set Python path
export PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH

# Optional: Enable debug logging
export SENTI_LOG_LEVEL=DEBUG
```

---

## Basic Usage

### 1. Creating an Orchestration Manager

```python
from senti_os.core.faza17 import create_orchestration_manager
from senti_os.core.faza16 import create_llm_manager

# Option 1: Standalone (for testing)
manager = create_orchestration_manager()

# Option 2: With FAZA 16 integration (recommended)
faza16 = create_llm_manager()
manager = create_orchestration_manager(faza16_manager=faza16)
```

### 2. Creating Requests

```python
from senti_os.core.faza17 import OrchestrationRequest, Priority

# Simple request
request = OrchestrationRequest(
    request_id="task_001",
    task_description="Summarize this document",
    priority=Priority.NORMAL,
)

# Advanced request with constraints
request = OrchestrationRequest(
    request_id="task_002",
    task_description="Analyze sentiment and generate report",
    priority=Priority.HIGH,
    max_cost=5.0,              # Maximum $5 cost
    max_time=120,              # Maximum 120 seconds
    require_ensemble=True,     # Force multi-model combination
    user_consent=True,         # Allow external API calls
    context={
        "language": "en",
        "domain": "finance",
    },
)
```

### 3. Submitting Tasks

```python
# Submit single task
request_id = manager.submit_task(request)
print(f"Submitted task: {request_id}")

# Submit multiple tasks
requests = [request1, request2, request3]
for req in requests:
    manager.submit_task(req)
```

### 4. Processing Tasks

```python
# Process next task (blocking)
result = manager.process_next_task()

if result:
    print(f"Task {result.request_id} completed")
    print(f"Output: {result.final_output}")
    print(f"Quality: {result.quality_score}")
else:
    print("No tasks in queue")
```

### 5. Processing Multiple Tasks

```python
# Process all queued tasks
while True:
    result = manager.process_next_task()
    if not result:
        break  # Queue empty

    print(f"Completed: {result.request_id}")
    print(f"Status: {result.status.value}")
```

### 6. Accessing Results

```python
# Check result status
if result.status == OrchestrationStatus.COMPLETED:
    # Success
    output = result.final_output
    confidence = result.confidence_score
    quality = result.quality_score

elif result.status == OrchestrationStatus.FAILED:
    # Failed
    error_msg = result.explanation
    print(f"Task failed: {error_msg}")
```

### 7. Getting Statistics

```python
# Get comprehensive statistics
stats = manager.get_statistics()

print(f"Total orchestrations: {stats['total_orchestrations']}")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Average cost: ${stats['average_cost']:.2f}")
print(f"Average duration: {stats['average_duration']:.1f}s")
print(f"Average quality: {stats['average_quality']:.2f}")

# Queue statistics
queue_stats = stats['queue_stats']
print(f"Queue size: {queue_stats['queue_size']}")
print(f"Total completed: {queue_stats['total_completed']}")
```

---

## Advanced Features

### 1. Step Planning

Use the Step Planner directly for task decomposition:

```python
from senti_os.core.faza17 import create_planner

planner = create_planner()

# Plan a complex task
planning_result = planner.plan_task(
    task_description="Analyze data, generate insights, create report",
    context={"data_size": "large", "format": "csv"},
    max_steps=10,
)

# Inspect the plan
print(f"Execution mode: {planning_result.execution_mode.value}")
print(f"Number of steps: {len(planning_result.steps)}")
print(f"Estimated cost: ${planning_result.total_estimated_cost:.2f}")
print(f"Estimated time: {planning_result.total_estimated_time}s")
print(f"Safety checks passed: {planning_result.safety_checks_passed}")

# Examine individual steps
for step in planning_result.steps:
    print(f"  Step {step.step_id}: {step.description}")
    print(f"    Type: {step.step_type.value}")
    print(f"    Dependencies: {step.dependencies}")
    print(f"    Est. cost: ${step.estimated_cost:.2f}")
```

### 2. Priority Queue Management

Manage task priorities explicitly:

```python
from senti_os.core.faza17 import create_queue, QueuedTask, Priority
from datetime import datetime

queue = create_queue()

# Create tasks with different priorities
high_task = QueuedTask(
    task_id="urgent_001",
    priority=Priority.HIGH,
    submission_time=datetime.now(),
    estimated_duration=60,
    max_cost=10.0,
    metadata={"description": "Urgent analysis"},
)

normal_task = QueuedTask(
    task_id="regular_001",
    priority=Priority.NORMAL,
    submission_time=datetime.now(),
    estimated_duration=120,
    max_cost=5.0,
    metadata={"description": "Regular report"},
)

# Enqueue tasks
queue.enqueue(high_task)
queue.enqueue(normal_task)

# High priority tasks are processed first
next_task = queue.dequeue()
print(f"Next task: {next_task.task_id}")  # Will be "urgent_001"

# Get queue statistics
stats = queue.get_statistics()
print(f"Queue size: {stats.current_size}")
print(f"Tasks by priority: {stats.tasks_by_priority}")
print(f"Average wait time: {stats.average_wait_time:.1f}s")
```

### 3. Model Ensemble

Combine outputs from multiple models:

```python
from senti_os.core.faza17 import (
    create_ensemble_engine,
    ModelOutput,
    EnsembleStrategy,
)

engine = create_ensemble_engine()

# Collect outputs from different models
outputs = [
    ModelOutput(
        model_id="gpt-4",
        content="The sentiment is positive with confidence 95%",
        confidence=0.95,
        reliability_score=0.90,
        processing_time=2.5,
        cost=0.15,
    ),
    ModelOutput(
        model_id="claude-3",
        content="The sentiment is positive with high certainty",
        confidence=0.92,
        reliability_score=0.88,
        processing_time=2.3,
        cost=0.12,
    ),
    ModelOutput(
        model_id="local-llm",
        content="Sentiment appears positive",
        confidence=0.75,
        reliability_score=0.70,
        processing_time=0.5,
        cost=0.01,
    ),
]

# Strategy 1: Weighted Average (default)
result = engine.combine_outputs(
    outputs=outputs,
    strategy=EnsembleStrategy.WEIGHTED_AVERAGE,
)

print(f"Final output: {result.final_output}")
print(f"Confidence: {result.confidence_score:.2f}")
print(f"Quality: {result.quality_score:.2f}")
print(f"Conflicts detected: {result.conflicts_detected}")

# Strategy 2: Highest Confidence
result = engine.combine_outputs(
    outputs=outputs,
    strategy=EnsembleStrategy.HIGHEST_CONFIDENCE,
)
print(f"Selected: {result.participating_models[0]}")

# Strategy 3: Consensus (requires agreement)
result = engine.combine_outputs(
    outputs=outputs,
    strategy=EnsembleStrategy.CONSENSUS,
)
print(f"Consensus achieved: {result.quality_score > 0.8}")
```

### 4. Reliability Feedback

Track and improve model performance:

```python
from senti_os.core.faza17 import create_feedback_loop, OutcomeType

feedback = create_feedback_loop()

# Record successful outcome
feedback.record_outcome(
    model_id="gpt-4",
    task_id="task_001",
    outcome=OutcomeType.SUCCESS,
    confidence_claimed=0.95,
    actual_quality=0.92,  # Actual measured quality
    processing_time=2.5,
    cost=0.15,
)

# Record failure
feedback.record_outcome(
    model_id="local-llm",
    task_id="task_002",
    outcome=OutcomeType.FAILURE,
    confidence_claimed=0.80,
    actual_quality=0.30,
    processing_time=1.0,
    cost=0.01,
)

# Update reliability scores
updated_scores = feedback.update_reliability_scores()
print("Updated reliability scores:")
for model_id, score in updated_scores.items():
    print(f"  {model_id}: {score:.3f}")

# Get model metrics
metrics = feedback.get_model_metrics("gpt-4")
if metrics:
    print(f"Total outcomes: {metrics.total_outcomes}")
    print(f"Success rate: {metrics.success_rate:.1%}")
    print(f"Avg confidence: {metrics.average_confidence:.2f}")
    print(f"Avg actual quality: {metrics.average_actual_quality:.2f}")
    print(f"Current reliability: {metrics.current_reliability:.3f}")
```

### 5. Explainability

Access decision explanations for transparency:

```python
from senti_os.core.faza17 import create_explainability_engine, DecisionType

explainability = create_explainability_engine()

# Explain model selection
explainability.explain_model_selection(
    decision_id="decision_001",
    selected_model="gpt-4",
    candidates=["gpt-4", "claude-3", "local-llm"],
    selection_factors={
        "quality": 0.95,
        "cost": 0.60,
        "speed": 0.80,
        "reliability": 0.90,
    },
    routing_logic="Quality-first strategy with cost constraints",
)

# Explain ensemble strategy
explainability.explain_ensemble_strategy(
    decision_id="ensemble_001",
    strategy="weighted_average",
    num_models=3,
    conflicts_detected=1,
    final_confidence=0.89,
)

# Retrieve explanation
explanation = explainability.get_explanation("decision_001")
if explanation:
    print(f"Decision: {explanation.summary}")
    print(f"Confidence in decision: {explanation.confidence_in_decision:.2f}")
    print(f"Final choice: {explanation.final_choice}")

    print("Factors:")
    for factor in explanation.factors:
        print(f"  - {factor.factor_name}: {factor.factor_value:.2f} (weight: {factor.weight:.2f})")

# Get audit report
audit_report = explainability.generate_audit_report()
print(f"Total decisions: {audit_report['total_decisions']}")
print(f"Decisions by type: {audit_report['decisions_by_type']}")
print(f"Average confidence: {audit_report['average_confidence']:.2f}")
```

### 6. Pipeline Management

Control execution strategies:

```python
from senti_os.core.faza17 import create_pipeline_manager, PipelineStrategy

pipeline_mgr = create_pipeline_manager()

# Define pipeline stages
stages = [
    {"name": "Data extraction", "model_id": "local_parser"},
    {"name": "Analysis", "model_id": "gpt-4"},
    {"name": "Report generation", "model_id": "claude-3"},
]

# Strategy 1: Local → Fast → Precise
result = pipeline_mgr.execute_pipeline(
    pipeline_id="pipe_001",
    strategy=PipelineStrategy.LOCAL_FAST_PRECISE,
    stages=stages,
    max_time=300,
    max_cost=10.0,
)

print(f"Pipeline completed: {result.success}")
print(f"Total duration: {result.total_duration:.1f}s")
print(f"Total cost: ${result.total_cost:.2f}")
print(f"Quality score: {result.quality_score:.2f}")

# Examine stages
for stage in result.stages:
    print(f"  Stage: {stage.stage_name}")
    print(f"    Status: {stage.status.value}")
    print(f"    Duration: {stage.duration:.1f}s")
    print(f"    Output: {stage.output[:50]}...")

# Strategy 2: Parallel Ensemble (for quality-critical tasks)
result = pipeline_mgr.execute_pipeline(
    pipeline_id="pipe_002",
    strategy=PipelineStrategy.PARALLEL_ENSEMBLE,
    stages=stages,
    max_time=300,
    max_cost=20.0,
)
```

---

## Best Practices

### 1. Request Design

**DO:**
```python
# Clear, specific task descriptions
request = OrchestrationRequest(
    request_id="analysis_20241202_001",  # Unique, descriptive ID
    task_description="Analyze Q4 sales data and identify top 3 trends",
    priority=Priority.HIGH,
    max_cost=5.0,
    max_time=120,
    context={
        "quarter": "Q4",
        "year": 2024,
        "data_source": "sales_db",
    },
)
```

**DON'T:**
```python
# Vague, generic descriptions
request = OrchestrationRequest(
    request_id="task1",  # Not descriptive
    task_description="Do analysis",  # Too vague
)
```

### 2. Priority Assignment

**Guidelines:**
- `Priority.HIGH`: Time-sensitive, business-critical tasks
- `Priority.NORMAL`: Regular tasks, standard processing
- `Priority.LOW`: Background tasks, bulk processing

```python
# Good priority assignment
urgent_bug_fix = OrchestrationRequest(
    request_id="bug_fix_001",
    task_description="Fix critical authentication issue",
    priority=Priority.HIGH,  # Appropriate for critical bug
)

daily_report = OrchestrationRequest(
    request_id="daily_report",
    task_description="Generate daily analytics report",
    priority=Priority.NORMAL,  # Appropriate for routine task
)

data_cleanup = OrchestrationRequest(
    request_id="cleanup_001",
    task_description="Clean up old log files",
    priority=Priority.LOW,  # Appropriate for background task
)
```

### 3. Resource Limits

Set appropriate limits based on task complexity:

```python
# Simple task: Low limits
simple_request = OrchestrationRequest(
    request_id="simple_001",
    task_description="Summarize a single paragraph",
    max_cost=0.5,   # $0.50 max
    max_time=30,    # 30 seconds max
)

# Complex task: Higher limits
complex_request = OrchestrationRequest(
    request_id="complex_001",
    task_description="Analyze 1000 customer reviews, extract themes, generate comprehensive report",
    max_cost=20.0,  # $20 max
    max_time=600,   # 10 minutes max
)
```

### 4. Error Handling

Always check result status and handle errors:

```python
result = manager.process_next_task()

if result is None:
    print("No tasks to process")

elif result.status == OrchestrationStatus.COMPLETED:
    # Success path
    process_successful_result(result)

elif result.status == OrchestrationStatus.FAILED:
    # Error path
    log_error(f"Task {result.request_id} failed: {result.explanation}")

    # Optionally retry
    if should_retry(result):
        retry_request = create_retry_request(result.request_id)
        manager.submit_task(retry_request)
```

### 5. Monitoring & Logging

Regularly monitor system performance:

```python
import time

def monitor_orchestration():
    """Monitor orchestration system health."""
    while True:
        stats = manager.get_statistics()

        # Check success rate
        if stats['success_rate'] < 0.8:
            alert("Low success rate detected")

        # Check average cost
        if stats['average_cost'] > 10.0:
            alert("High average cost detected")

        # Check queue size
        queue_stats = manager.get_queue_status()
        if queue_stats['queue_size'] > 50:
            alert("Queue backlog detected")

        time.sleep(60)  # Check every minute
```

### 6. Context Usage

Provide relevant context for better results:

```python
request = OrchestrationRequest(
    request_id="sentiment_analysis_001",
    task_description="Analyze customer feedback sentiment",
    context={
        # Domain information
        "domain": "e-commerce",
        "product_category": "electronics",

        # Data characteristics
        "data_size": "large",
        "language": "en",
        "source": "customer_reviews",

        # Requirements
        "output_format": "json",
        "include_examples": True,

        # Preferences
        "model_preference": "high_quality",
        "budget_sensitivity": "low",
    },
)
```

### 7. Ensemble Usage

Use ensemble when:
- Multiple models provide different perspectives
- High confidence is required
- Conflicting outputs need resolution

```python
# When to use ensemble
high_stakes_request = OrchestrationRequest(
    request_id="legal_analysis_001",
    task_description="Analyze contract for legal risks",
    priority=Priority.HIGH,
    require_ensemble=True,  # Use multiple models for validation
    max_cost=15.0,           # Higher budget for quality
)

# When NOT to use ensemble
simple_request = OrchestrationRequest(
    request_id="greeting_001",
    task_description="Generate a friendly greeting",
    require_ensemble=False,  # Single model sufficient
    max_cost=0.1,
)
```

---

## Examples & Recipes

### Example 1: Document Analysis Pipeline

```python
from senti_os.core.faza17 import (
    create_orchestration_manager,
    OrchestrationRequest,
    Priority,
)

def analyze_document(document_path: str) -> dict:
    """Analyze a document and return insights."""

    manager = create_orchestration_manager()

    request = OrchestrationRequest(
        request_id=f"doc_analysis_{document_path}",
        task_description=f"Read document at {document_path}, extract key information, "
                        f"summarize main points, and identify action items",
        priority=Priority.NORMAL,
        max_cost=5.0,
        max_time=180,
        context={
            "document_path": document_path,
            "output_format": "structured_json",
            "sections": ["summary", "key_points", "action_items"],
        },
    )

    manager.submit_task(request)
    result = manager.process_next_task()

    if result.status == OrchestrationStatus.COMPLETED:
        return {
            "success": True,
            "summary": result.final_output,
            "confidence": result.confidence_score,
            "quality": result.quality_score,
            "cost": result.total_cost,
            "duration": result.total_duration,
        }
    else:
        return {
            "success": False,
            "error": result.explanation,
        }

# Usage
result = analyze_document("/path/to/report.pdf")
if result["success"]:
    print(f"Analysis: {result['summary']}")
    print(f"Quality: {result['quality']:.2f}")
```

### Example 2: Multi-Task Batch Processing

```python
def process_customer_feedback_batch(feedback_list: list) -> list:
    """Process multiple customer feedback items in batch."""

    manager = create_orchestration_manager()
    results = []

    # Submit all tasks
    for i, feedback in enumerate(feedback_list):
        request = OrchestrationRequest(
            request_id=f"feedback_{i}",
            task_description=f"Analyze sentiment and extract issues from: {feedback}",
            priority=Priority.NORMAL,
            max_cost=1.0,
            max_time=60,
        )
        manager.submit_task(request)

    # Process all tasks
    while True:
        result = manager.process_next_task()
        if not result:
            break

        results.append({
            "feedback_id": result.request_id,
            "analysis": result.final_output,
            "confidence": result.confidence_score,
        })

    return results

# Usage
feedback = [
    "The product is great but shipping was slow",
    "Excellent quality, will buy again!",
    "Not satisfied with customer service",
]

results = process_customer_feedback_batch(feedback)
for r in results:
    print(f"{r['feedback_id']}: {r['analysis']}")
```

### Example 3: High-Quality Ensemble Analysis

```python
def high_quality_analysis(data: str) -> dict:
    """Perform high-quality analysis using ensemble."""

    manager = create_orchestration_manager()

    request = OrchestrationRequest(
        request_id="hq_analysis_001",
        task_description=f"Perform comprehensive analysis of: {data}",
        priority=Priority.HIGH,
        require_ensemble=True,  # Force ensemble combination
        max_cost=20.0,          # Higher budget for quality
        max_time=300,
        user_consent=True,      # Allow external API calls
        context={
            "quality_level": "highest",
            "ensemble_strategy": "weighted_average",
            "min_models": 3,
        },
    )

    manager.submit_task(request)
    result = manager.process_next_task()

    # Get detailed statistics
    stats = manager.get_statistics()

    return {
        "analysis": result.final_output,
        "confidence": result.confidence_score,
        "quality": result.quality_score,
        "models_used": result.models_used,
        "cost": result.total_cost,
        "duration": result.total_duration,
        "explanation": result.explanation,
        "system_stats": stats,
    }
```

### Example 4: Cost-Optimized Processing

```python
def cost_optimized_processing(tasks: list, max_budget: float) -> list:
    """Process tasks with strict cost constraints."""

    manager = create_orchestration_manager()
    results = []
    remaining_budget = max_budget

    for task in tasks:
        if remaining_budget <= 0:
            print("Budget exhausted")
            break

        # Calculate per-task budget
        per_task_budget = remaining_budget / (len(tasks) - len(results))

        request = OrchestrationRequest(
            request_id=f"task_{len(results)}",
            task_description=task,
            priority=Priority.LOW,
            max_cost=min(per_task_budget, 1.0),  # Cap at $1 per task
            max_time=60,
            context={
                "cost_sensitivity": "high",
                "quality_threshold": "acceptable",
            },
        )

        manager.submit_task(request)
        result = manager.process_next_task()

        if result:
            results.append(result)
            remaining_budget -= result.total_cost

    return results
```

### Example 5: Real-Time Monitoring Dashboard

```python
import time
from datetime import datetime

def monitoring_dashboard():
    """Real-time orchestration monitoring."""

    manager = create_orchestration_manager()

    while True:
        # Get current statistics
        stats = manager.get_statistics()
        queue_stats = manager.get_queue_status()

        # Clear screen (Unix-like systems)
        print("\033[2J\033[H")

        # Display header
        print("=" * 60)
        print("FAZA 17 Orchestration Dashboard")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Orchestration stats
        print("\nOrchestration Statistics:")
        print(f"  Total orchestrations: {stats['total_orchestrations']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Average cost: ${stats['average_cost']:.2f}")
        print(f"  Average duration: {stats['average_duration']:.1f}s")
        print(f"  Average quality: {stats['average_quality']:.2f}")

        # Queue stats
        print("\nQueue Status:")
        print(f"  Current size: {queue_stats['queue_size']}")
        print(f"  Total completed: {queue_stats['total_completed']}")
        print(f"  Total failed: {queue_stats['total_failed']}")
        print(f"  Average wait time: {queue_stats['average_wait_time']:.1f}s")

        # Priority breakdown
        print("\nTasks by Priority:")
        for priority, count in queue_stats['tasks_by_priority'].items():
            print(f"  {priority}: {count}")

        # Alerts
        print("\nAlerts:")
        if stats['success_rate'] < 0.8:
            print("  ⚠️  Low success rate detected")
        if queue_stats['queue_size'] > 50:
            print("  ⚠️  High queue backlog")
        if stats['average_cost'] > 10.0:
            print("  ⚠️  High average cost")

        if not any([
            stats['success_rate'] < 0.8,
            queue_stats['queue_size'] > 50,
            stats['average_cost'] > 10.0
        ]):
            print("  ✓ All systems normal")

        time.sleep(5)  # Update every 5 seconds
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Queue is full" error

**Symptom:**
```python
RuntimeError: Task queue is full
```

**Cause:** Priority queue reached maximum capacity (default 100 tasks).

**Solution:**
```python
# Option 1: Process tasks to clear queue
while manager.process_next_task():
    pass

# Option 2: Increase queue size (if implementing custom queue)
from senti_os.core.faza17.priority_queue import PriorityQueue

custom_queue = PriorityQueue()
custom_queue.MAX_QUEUE_SIZE = 200  # Increase limit
```

#### Issue 2: Low quality scores

**Symptom:**
```python
result.quality_score < 0.5  # Low quality
```

**Cause:** Poor model selection or insufficient ensemble.

**Solution:**
```python
# Enable ensemble for better quality
request = OrchestrationRequest(
    request_id="task_001",
    task_description="...",
    require_ensemble=True,  # Force multi-model combination
    max_cost=10.0,          # Increase budget for quality
)
```

#### Issue 3: Tasks taking too long

**Symptom:** Tasks exceed time limits consistently.

**Cause:** Unrealistic time constraints or inefficient models.

**Solution:**
```python
# Option 1: Increase time limits
request = OrchestrationRequest(
    request_id="task_001",
    task_description="...",
    max_time=600,  # Increase from 300 to 600 seconds
)

# Option 2: Simplify task
request = OrchestrationRequest(
    request_id="task_001",
    task_description="Summarize main points only",  # More focused
    max_time=60,
)
```

#### Issue 4: High costs

**Symptom:** Average cost exceeding budget.

**Cause:** Using expensive models or unnecessary ensemble.

**Solution:**
```python
# Set strict cost limits
request = OrchestrationRequest(
    request_id="task_001",
    task_description="...",
    max_cost=1.0,           # Strict limit
    require_ensemble=False, # Disable ensemble
    context={
        "cost_sensitivity": "high",
        "model_preference": "local_first",
    },
)
```

#### Issue 5: Import errors

**Symptom:**
```python
ModuleNotFoundError: No module named 'senti_os.core.faza17'
```

**Cause:** Incorrect Python path or installation issue.

**Solution:**
```bash
# Set correct Python path
export PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH

# Verify installation
python3 -c "import senti_os.core.faza17; print('OK')"
```

### Debugging Tips

#### Enable Debug Logging

```python
import logging

# Enable debug logging for FAZA 17
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("senti_os.core.faza17")
logger.setLevel(logging.DEBUG)
```

#### Inspect Explanations

```python
# Get detailed explanation for debugging
result = manager.process_next_task()

# Access orchestration manager's explainability engine
audit_report = manager.get_audit_report()
explainability_report = audit_report['explainability_report']

print(f"Total decisions: {explainability_report['total_decisions']}")
print(f"Decisions by type: {explainability_report['decisions_by_type']}")
```

#### Check Component Health

```python
# Check individual component statistics
stats = manager.get_statistics()

# Pipeline stats
pipeline_stats = stats['pipeline_stats']
print(f"Pipeline success rate: {pipeline_stats['success_rate']:.1%}")

# Ensemble stats
ensemble_stats = stats['ensemble_stats']
print(f"Total ensembles: {ensemble_stats['total_ensembles']}")

# Feedback stats
feedback_stats = stats['feedback_stats']
print(f"Models tracked: {feedback_stats['models_tracked']}")
```

---

## Performance Optimization

### 1. Batch Processing

Process multiple similar tasks together:

```python
def batch_process(tasks: list):
    """Process tasks in batch for efficiency."""

    manager = create_orchestration_manager()

    # Submit all at once
    for task in tasks:
        manager.submit_task(task)

    # Process continuously
    results = []
    while True:
        result = manager.process_next_task()
        if not result:
            break
        results.append(result)

    return results
```

### 2. Priority Optimization

Use priorities effectively to optimize throughput:

```python
# Critical tasks: HIGH priority
critical = OrchestrationRequest(
    request_id="critical_001",
    task_description="Process urgent order",
    priority=Priority.HIGH,  # Processed first
)

# Background tasks: LOW priority
background = OrchestrationRequest(
    request_id="background_001",
    task_description="Generate analytics report",
    priority=Priority.LOW,  # Processed when idle
)
```

### 3. Cost Optimization

Minimize costs without sacrificing quality:

```python
request = OrchestrationRequest(
    request_id="cost_opt_001",
    task_description="...",
    context={
        # Prefer local models
        "model_preference": "local_first",

        # Disable unnecessary ensemble
        "ensemble_threshold": "high",

        # Use faster, cheaper models for simple steps
        "quality_threshold": "acceptable",
    },
)
```

### 4. Resource Pooling

Reuse orchestration manager instances:

```python
# Create once
manager = create_orchestration_manager()

# Reuse for multiple requests
for request in requests:
    manager.submit_task(request)

# Don't create new managers for each request
```

### 5. Async Processing

Use async patterns for non-blocking operations:

```python
import asyncio

async def async_orchestrate(request):
    """Non-blocking orchestration."""
    manager = create_orchestration_manager()
    manager.submit_task(request)

    # Simulate async processing
    await asyncio.sleep(0.1)

    return manager.process_next_task()

# Run multiple in parallel
async def main():
    tasks = [async_orchestrate(r) for r in requests]
    results = await asyncio.gather(*tasks)
    return results

# Execute
results = asyncio.run(main())
```

---

## Integration Patterns

### Pattern 1: Web API Integration

```python
from flask import Flask, request, jsonify
from senti_os.core.faza17 import create_orchestration_manager, OrchestrationRequest, Priority

app = Flask(__name__)
manager = create_orchestration_manager()

@app.route('/api/orchestrate', methods=['POST'])
def orchestrate_endpoint():
    """REST API endpoint for orchestration."""
    data = request.json

    # Create request from API payload
    orch_request = OrchestrationRequest(
        request_id=data.get('request_id'),
        task_description=data.get('task'),
        priority=Priority[data.get('priority', 'NORMAL')],
        max_cost=data.get('max_cost', 5.0),
        max_time=data.get('max_time', 300),
    )

    # Submit and process
    manager.submit_task(orch_request)
    result = manager.process_next_task()

    # Return result
    return jsonify({
        'request_id': result.request_id,
        'status': result.status.value,
        'output': result.final_output,
        'confidence': result.confidence_score,
        'quality': result.quality_score,
        'cost': result.total_cost,
        'duration': result.total_duration,
    })

@app.route('/api/stats', methods=['GET'])
def stats_endpoint():
    """Get orchestration statistics."""
    stats = manager.get_statistics()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Pattern 2: Event-Driven Integration

```python
from senti_core_module.senti_core.services.event_bus import EventBus
from senti_os.core.faza17 import create_orchestration_manager

event_bus = EventBus()
manager = create_orchestration_manager()

# Listen for orchestration requests
@event_bus.subscribe("orchestration.request")
def handle_orchestration_request(event_data):
    """Handle orchestration requests from event bus."""
    request = OrchestrationRequest(**event_data)
    manager.submit_task(request)

# Listen for processing triggers
@event_bus.subscribe("orchestration.process")
def handle_processing():
    """Process next task when triggered."""
    result = manager.process_next_task()

    if result:
        # Publish result
        event_bus.publish("orchestration.completed", {
            "request_id": result.request_id,
            "status": result.status.value,
            "quality": result.quality_score,
        })
```

### Pattern 3: Scheduled Task Integration

```python
import schedule
import time

manager = create_orchestration_manager()

def scheduled_task():
    """Task to run on schedule."""
    request = OrchestrationRequest(
        request_id=f"scheduled_{time.time()}",
        task_description="Generate daily report",
        priority=Priority.NORMAL,
    )

    manager.submit_task(request)
    result = manager.process_next_task()

    if result:
        # Save or send result
        save_result(result)

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(scheduled_task)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## API Reference

### Quick Reference

```python
# Core imports
from senti_os.core.faza17 import (
    # Manager
    OrchestrationManager,
    create_orchestration_manager,
    OrchestrationRequest,
    OrchestrationResult,
    OrchestrationStatus,

    # Planner
    StepPlanner,
    create_planner,
    Step,
    StepType,
    ExecutionMode,
    PlanningResult,

    # Queue
    PriorityQueue,
    create_queue,
    QueuedTask,
    Priority,
    QueueStatistics,

    # Ensemble
    ModelEnsembleEngine,
    create_ensemble_engine,
    ModelOutput,
    EnsembleStrategy,
    EnsembleResult,

    # Feedback
    ReliabilityFeedbackLoop,
    create_feedback_loop,
    FeedbackEntry,
    ModelMetrics,
    OutcomeType,

    # Explainability
    ExplainabilityEngine,
    create_explainability_engine,
    ExplanationEntry,
    DecisionType,
    DecisionFactor,

    # Pipeline
    PipelineManager,
    create_pipeline_manager,
    PipelineStrategy,
    PipelineStage,
    PipelineResult,
)
```

### Key Enums

```python
# Priority levels
class Priority(Enum):
    HIGH = 1
    NORMAL = 2
    LOW = 3

# Orchestration status
class OrchestrationStatus(Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    EXECUTING = "executing"
    ENSEMBLING = "ensembling"
    COMPLETED = "completed"
    FAILED = "failed"

# Step types
class StepType(Enum):
    ANALYZE = "analyze"
    GENERATE = "generate"
    VALIDATE = "validate"
    TRANSFORM = "transform"

# Ensemble strategies
class EnsembleStrategy(Enum):
    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_VOTE = "majority_vote"
    HIGHEST_CONFIDENCE = "highest_confidence"
    CONSENSUS = "consensus"
    BEST_OF_N = "best_of_n"

# Pipeline strategies
class PipelineStrategy(Enum):
    LOCAL_FAST_PRECISE = "local_fast_precise"
    PARALLEL_ENSEMBLE = "parallel_ensemble"
    SEQUENTIAL_VALIDATION = "sequential_validation"
    COST_OPTIMIZED = "cost_optimized"
    QUALITY_FIRST = "quality_first"

# Outcome types
class OutcomeType(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
```

---

## Additional Resources

### Documentation
- **FAZA_17_SPEC.md**: Technical specification
- **FAZA_16_SPEC.md**: LLM Control Layer specification
- **SENTI OS Architecture**: System-wide architecture

### Testing
```bash
# Run all FAZA 17 tests
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH \
python3 -m unittest senti_os/tests/faza17/test_faza17_comprehensive.py -v
```

### Support
- Check logs: `/var/log/senti_os/faza17.log`
- Enable debug mode: `export SENTI_LOG_LEVEL=DEBUG`
- Review audit reports: `manager.get_audit_report()`

---

**Version:** 1.0.0
**Last Updated:** 2025-12-02
**SENTI OS Team**
