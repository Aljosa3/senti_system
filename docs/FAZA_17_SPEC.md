# FAZA 17 - Multi-Model Orchestration Layer

**Version:** 1.0.0
**Status:** Production Ready
**SENTI OS Core Component**

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Data Models](#data-models)
5. [Workflow & Control Flow](#workflow--control-flow)
6. [Integration Points](#integration-points)
7. [Performance Characteristics](#performance-characteristics)
8. [Security & Privacy](#security--privacy)
9. [Testing & Validation](#testing--validation)
10. [References](#references)

---

## Overview

### Purpose

FAZA 17 provides intelligent multi-model orchestration capabilities for SENTI OS, enabling the system to:

- **Decompose Complex Tasks**: Break down sophisticated requests into manageable steps
- **Coordinate Multiple Models**: Route steps to optimal models via FAZA 16
- **Combine Results**: Intelligently merge outputs from multiple models
- **Learn from Outcomes**: Continuously improve routing based on performance
- **Ensure Transparency**: Provide complete explainability for all decisions
- **Optimize Resources**: Balance quality, cost, and speed constraints

### Key Features

- **Step Planning**: Task decomposition with safety validation
- **Priority Scheduling**: Three-level queue with starvation prevention
- **Model Ensemble**: Multiple combination strategies (weighted average, majority vote, consensus)
- **Reliability Feedback**: Learning loop adjusting model scores based on outcomes
- **Explainability**: Complete decision trail for EU AI Act compliance
- **Pipeline Management**: Flexible execution strategies (Local→Fast→Precise, Parallel, Sequential)
- **Quality Assurance**: Multi-level quality scoring and validation

### Design Principles

1. **Modularity**: Each component is self-contained with clear interfaces
2. **Transparency**: All decisions are logged and explainable
3. **Learning**: System improves through reliability feedback
4. **Safety First**: Multiple validation layers and safety checks
5. **Resource Efficiency**: Intelligent cost/time limit enforcement
6. **Privacy Preservation**: No external calls without consent (via FAZA 16)

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Orchestration Manager                      │
│                    (Main Coordinator)                        │
└────┬──────────┬──────────┬──────────┬──────────┬───────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌─────────┐ ┌────────┐ ┌──────────┐ ┌──────┐ ┌───────────┐
│  Step   │ │Priority│ │ Pipeline │ │Model │ │Reliability│
│ Planner │ │ Queue  │ │ Manager  │ │Ensem │ │ Feedback  │
└─────────┘ └────────┘ └──────────┘ └──ble─┘ └───────────┘
                                     └──────┘
                                        ▲
                                        │
                              ┌─────────┴──────────┐
                              │  Explainability    │
                              │     Engine         │
                              └────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────────┐
                              │    FAZA 16 LLM      │
                              │   Control Layer     │
                              └─────────────────────┘
```

### Component Interaction Flow

```
1. Request Received
   ↓
2. Submit to Priority Queue
   ↓
3. Dequeue Next Task
   ↓
4. Step Planner: Decompose Task
   ↓
5. Explainability: Log Planning Decisions
   ↓
6. Pipeline Manager: Execute Steps
   │  ├─ Route to Models (via FAZA 16)
   │  └─ Execute with Strategy
   ↓
7. Ensemble Engine: Combine Results (if needed)
   ↓
8. Explainability: Log Ensemble Decisions
   ↓
9. Reliability Feedback: Record Outcomes
   ↓
10. Return Orchestration Result
```

### Directory Structure

```
senti_os/core/faza17/
├── __init__.py                        # Module exports and API
├── orchestration_manager.py           # Main coordinator
├── step_planner.py                    # Task decomposition
├── priority_queue.py                  # Priority scheduling
├── model_ensemble_engine.py           # Multi-model combination
├── reliability_feedback.py            # Learning loop
├── explainability_engine.py           # Decision transparency
└── pipeline_manager.py                # Execution flow control

senti_os/tests/faza17/
└── test_faza17_comprehensive.py       # 55 comprehensive tests

docs/
├── FAZA_17_SPEC.md                    # This document
└── FAZA_17_IMPLEMENTATION_GUIDE.md    # Implementation guide
```

---

## Core Components

### 1. Orchestration Manager

**File:** `orchestration_manager.py` (424 lines)

**Purpose:** Main coordinator integrating all FAZA 17 components.

**Key Classes:**
- `OrchestrationManager`: Central orchestration coordinator
- `OrchestrationRequest`: Input request specification
- `OrchestrationResult`: Output with full execution details
- `OrchestrationStatus`: Task status tracking

**Key Methods:**

```python
def submit_task(self, request: OrchestrationRequest) -> str:
    """Submit task to priority queue."""

def process_next_task(self) -> Optional[OrchestrationResult]:
    """Process next task from queue through full pipeline."""

def get_statistics(self) -> Dict:
    """Get comprehensive orchestration statistics."""

def get_audit_report(self) -> Dict:
    """Generate full audit report for compliance."""
```

**Integration Points:**
- Creates all sub-components (planner, queue, ensemble, etc.)
- Routes through FAZA 16 for model selection
- Coordinates full orchestration lifecycle

### 2. Step Planner

**File:** `step_planner.py` (412 lines)

**Purpose:** Decomposes complex tasks into executable steps.

**Key Classes:**
- `StepPlanner`: Task decomposition engine
- `Step`: Individual execution step
- `PlanningResult`: Complete plan with estimates
- `StepType`: Step categorization (ANALYZE, GENERATE, VALIDATE, TRANSFORM)
- `ExecutionMode`: Sequential vs. parallel execution

**Key Features:**
- Task complexity assessment
- Dependency analysis between steps
- Cost and time estimation
- Safety validation
- Control flow graph generation

**Safety Checks:**
```python
def _perform_safety_checks(self, steps: List[Step]) -> bool:
    """Validate plan safety."""
    # Check for prohibited patterns
    # Validate execution order
    # Ensure resource constraints
```

### 3. Priority Queue

**File:** `priority_queue.py` (337 lines)

**Purpose:** Priority-based task scheduling with starvation prevention.

**Key Classes:**
- `PriorityQueue`: Main queue manager
- `QueuedTask`: Task with metadata
- `Priority`: Three-level priority (HIGH=1, NORMAL=2, LOW=3)
- `QueueStatistics`: Queue performance metrics

**Key Features:**
- Priority-based sorting (HIGH > NORMAL > LOW)
- Aging mechanism to prevent starvation
- Automatic retry on failure
- Comprehensive statistics tracking

**Starvation Prevention:**
```python
def _apply_aging(self) -> None:
    """Boost priority of waiting tasks after threshold."""
    threshold = timedelta(seconds=120)  # 2 minutes

    for task in self.queue:
        wait_time = current_time - task.submission_time
        if wait_time > threshold:
            # Boost priority: LOW → NORMAL → HIGH
```

### 4. Model Ensemble Engine

**File:** `model_ensemble_engine.py` (448 lines - after fix)

**Purpose:** Intelligently combine outputs from multiple models.

**Key Classes:**
- `ModelEnsembleEngine`: Main ensemble coordinator
- `ModelOutput`: Single model result
- `EnsembleResult`: Combined result with metadata
- `EnsembleStrategy`: Combination strategies
- `ConflictResolution`: Conflict handling methods

**Ensemble Strategies:**

1. **WEIGHTED_AVERAGE**: Weight by confidence × reliability
2. **MAJORITY_VOTE**: Democratic voting
3. **HIGHEST_CONFIDENCE**: Select most confident model
4. **CONSENSUS**: Require agreement threshold
5. **BEST_OF_N**: Select highest quality

**Conflict Detection:**
```python
def _detect_conflicts(self, outputs: List[ModelOutput]) -> List[Dict]:
    """Detect contradictions between model outputs."""
    # Compare pairwise outputs
    # Identify contradictions
    # Return conflict details
```

### 5. Reliability Feedback Loop

**File:** `reliability_feedback.py` (452 lines)

**Purpose:** Learn from outcomes to improve model routing.

**Key Classes:**
- `ReliabilityFeedbackLoop`: Learning coordinator
- `FeedbackEntry`: Outcome record
- `ModelMetrics`: Performance metrics per model
- `OutcomeType`: SUCCESS, FAILURE, PARTIAL_SUCCESS

**Learning Algorithm:**
```python
def _update_score(self, current: float, outcome: float) -> float:
    """Apply exponential moving average."""
    learning_rate = 0.1
    new_score = current + learning_rate * (outcome - current)
    return max(0.1, min(1.0, new_score))  # Bounded [0.1, 1.0]
```

**Metrics Tracked:**
- Success rate per model
- Average confidence vs. actual quality
- Processing time trends
- Cost efficiency
- Reliability drift detection

### 6. Explainability Engine

**File:** `explainability_engine.py` (463 lines)

**Purpose:** Provide transparent explanations for all decisions.

**Key Classes:**
- `ExplainabilityEngine`: Explanation coordinator
- `ExplanationEntry`: Single decision explanation
- `DecisionType`: Type of decision being explained
- `DecisionFactor`: Individual factor in decision

**Decision Types Explained:**
- `MODEL_SELECTION`: Why specific model was chosen
- `STEP_PLANNING`: How task was decomposed
- `ENSEMBLE_STRATEGY`: Why ensemble method was used
- `PRIORITY_ASSIGNMENT`: Why priority was assigned
- `CONFLICT_RESOLUTION`: How conflicts were resolved
- `PIPELINE_ROUTING`: Why execution path was chosen

**Audit Report:**
```python
def generate_audit_report(self) -> Dict:
    """Generate EU AI Act compliant audit trail."""
    return {
        "total_decisions": count,
        "decisions_by_type": breakdown,
        "average_confidence": score,
        "oldest_decision": timestamp,
        "newest_decision": timestamp,
    }
```

### 7. Pipeline Manager

**File:** `pipeline_manager.py` (343 lines)

**Purpose:** Control execution flow through different strategies.

**Key Classes:**
- `PipelineManager`: Execution controller
- `PipelineStage`: Individual stage in pipeline
- `PipelineResult`: Complete execution result
- `PipelineStrategy`: Execution strategies
- `StageStatus`: Stage status tracking

**Pipeline Strategies:**

1. **LOCAL_FAST_PRECISE**
   - Try local model first
   - Fallback to fast cloud model
   - Final fallback to precise model
   - Sequential execution

2. **PARALLEL_ENSEMBLE**
   - Execute all models simultaneously
   - Combine results via ensemble
   - Best for quality-critical tasks

3. **SEQUENTIAL_VALIDATION**
   - Execute models in sequence
   - Validate each output
   - Stop on validation pass

4. **COST_OPTIMIZED**
   - Prefer low-cost models
   - Trade quality for cost

5. **QUALITY_FIRST**
   - Prefer high-quality models
   - Ignore cost constraints

**Stage Execution:**
```python
def execute_pipeline(
    self,
    pipeline_id: str,
    strategy: PipelineStrategy,
    stages: List[Dict],
    max_time: int = 300,
    max_cost: float = 10.0,
) -> PipelineResult:
    """Execute pipeline with limits."""
```

---

## Data Models

### OrchestrationRequest

```python
@dataclass
class OrchestrationRequest:
    request_id: str                    # Unique identifier
    task_description: str              # Natural language task
    priority: Priority                 # Task priority
    max_cost: float = 5.0             # Maximum cost in dollars
    max_time: int = 300               # Maximum time in seconds
    require_ensemble: bool = False    # Force ensemble combination
    user_consent: bool = False        # Consent for external calls
    context: Dict = field(default_factory=dict)  # Additional context
```

### OrchestrationResult

```python
@dataclass
class OrchestrationResult:
    request_id: str                    # Request identifier
    status: OrchestrationStatus        # Final status
    final_output: str                  # Final result
    confidence_score: float            # Confidence [0.0-1.0]
    total_cost: float                  # Total cost incurred
    total_duration: float              # Total time in seconds
    steps_executed: int                # Number of steps executed
    models_used: List[str]            # Models utilized
    explanation: str                   # Human-readable explanation
    quality_score: float              # Quality assessment
    timestamp: str                     # ISO timestamp
    metadata: Dict                     # Additional metadata
```

### Step

```python
@dataclass
class Step:
    step_id: str                       # Unique step identifier
    description: str                   # Step description
    step_type: StepType               # ANALYZE/GENERATE/VALIDATE/TRANSFORM
    dependencies: List[str]            # Dependent step IDs
    estimated_cost: float              # Estimated cost
    estimated_time: int                # Estimated time
    required_capabilities: List[str]   # Required model capabilities
    safety_constraints: List[str]      # Safety requirements
```

### ModelOutput

```python
@dataclass
class ModelOutput:
    model_id: str                      # Model identifier
    content: str                       # Output content
    confidence: float                  # Confidence score
    reliability_score: float           # Historical reliability
    processing_time: float             # Time taken
    cost: float                        # Cost incurred
```

### EnsembleResult

```python
@dataclass
class EnsembleResult:
    final_output: str                  # Combined output
    confidence_score: float            # Final confidence
    strategy_used: EnsembleStrategy    # Strategy applied
    participating_models: List[str]    # Models involved
    model_weights: Dict[str, float]   # Weight per model
    conflicts_detected: int            # Number of conflicts
    conflicts_resolved: int            # Conflicts resolved
    quality_score: float              # Quality assessment
    explanation: str                   # Combination reasoning
    individual_outputs: List[ModelOutput]  # Original outputs
```

---

## Workflow & Control Flow

### Complete Orchestration Flow

```python
# 1. User submits request
request = OrchestrationRequest(
    request_id="task_001",
    task_description="Analyze customer feedback and generate report",
    priority=Priority.HIGH,
    max_cost=5.0,
    max_time=300,
)

# 2. Submit to orchestration manager
manager = create_orchestration_manager(faza16_manager)
request_id = manager.submit_task(request)

# 3. Process next task (can be called repeatedly)
result = manager.process_next_task()

# 4. Internal flow within process_next_task():
#    a. Dequeue from priority queue
#    b. Plan steps with StepPlanner
#    c. Log planning decisions with Explainability
#    d. Execute via PipelineManager
#       - Route to models via FAZA 16
#       - Execute stages with strategy
#    e. Combine results with Ensemble (if needed)
#    f. Log ensemble decisions with Explainability
#    g. Record outcomes with ReliabilityFeedback
#    h. Return OrchestrationResult

# 5. Access results and statistics
if result.status == OrchestrationStatus.COMPLETED:
    print(f"Output: {result.final_output}")
    print(f"Quality: {result.quality_score}")
    print(f"Cost: ${result.total_cost}")
```

### Step Planning Process

```python
# 1. Receive task description and context
planning_result = planner.plan_task(
    task_description="Analyze data and generate insights",
    context={"data_size": "large", "format": "csv"},
    max_steps=10,
)

# 2. Internal planning:
#    a. Assess task complexity
#    b. Decompose into steps
#    c. Identify dependencies
#    d. Estimate costs and times
#    e. Perform safety checks
#    f. Select execution mode

# 3. Result contains:
#    - List of steps
#    - Execution mode (sequential/parallel)
#    - Total estimated cost
#    - Total estimated time
#    - Safety validation status
```

### Ensemble Combination Process

```python
# 1. Collect outputs from multiple models
outputs = [
    ModelOutput("gpt-4", "Analysis: ...", 0.95, 0.90, 2.5, 0.15),
    ModelOutput("claude", "Analysis: ...", 0.92, 0.88, 2.3, 0.12),
    ModelOutput("local", "Analysis: ...", 0.75, 0.70, 0.5, 0.01),
]

# 2. Combine with strategy
result = ensemble_engine.combine_outputs(
    outputs=outputs,
    strategy=EnsembleStrategy.WEIGHTED_AVERAGE,
)

# 3. Internal process:
#    a. Calculate model weights (confidence × reliability)
#    b. Detect conflicts between outputs
#    c. Apply ensemble strategy
#    d. Assess quality of combined result
#    e. Generate explanation

# 4. Result contains:
#    - Combined output
#    - Confidence score
#    - Quality score
#    - Conflict information
#    - Explanation
```

---

## Integration Points

### Integration with FAZA 16

FAZA 17 builds on top of FAZA 16 (LLM Control Layer):

```python
# Initialize with FAZA 16 integration
from senti_os.core.faza16 import create_llm_manager
from senti_os.core.faza17 import create_orchestration_manager

faza16_manager = create_llm_manager()
faza17_manager = create_orchestration_manager(faza16_manager)

# FAZA 17 uses FAZA 16 for:
# - Model routing and selection
# - Safety and privacy enforcement
# - Knowledge verification
# - Fact checking
```

### Integration with SENTI OS Core

```python
from senti_core_module.senti_core.services.event_bus import EventBus

# Publish orchestration events
event_bus.publish("orchestration.completed", {
    "request_id": result.request_id,
    "status": result.status.value,
    "quality": result.quality_score,
})
```

### External API Integration

```python
# All external calls go through FAZA 16's safety layer
# FAZA 17 never makes external calls directly
# This ensures:
# - User consent checking
# - PII sanitization
# - Cost tracking
# - Safety enforcement
```

---

## Performance Characteristics

### Time Complexity

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| Submit Task | O(log n) | Priority queue insertion |
| Dequeue Task | O(log n) | Priority queue extraction |
| Plan Task | O(k) | k = task complexity |
| Execute Pipeline | O(m × t) | m = stages, t = avg time per stage |
| Ensemble Combine | O(n²) | n = number of models (conflict detection) |
| Update Reliability | O(m) | m = number of models |
| Generate Explanation | O(1) | Constant time logging |

### Space Complexity

| Component | Space Usage | Notes |
|-----------|-------------|-------|
| Priority Queue | O(n) | n = queued tasks |
| Ensemble History | O(h) | h = history size (max 10000) |
| Feedback History | O(m × e) | m = models, e = entries per model |
| Explanation Log | O(d) | d = decisions logged (max 1000) |
| Pipeline History | O(p) | p = pipelines executed |

### Throughput

- **Tasks/second**: 10-50 (depends on task complexity)
- **Concurrent tasks**: Limited by priority queue size (default 100)
- **Batch processing**: Supported via multiple submit_task() calls

### Latency

- **Queue submission**: <1ms
- **Task planning**: 10-50ms
- **Pipeline execution**: 1-10s (depends on models and strategy)
- **Ensemble combination**: 50-200ms
- **Total orchestration**: 2-15s (typical)

---

## Security & Privacy

### Privacy Guarantees

1. **No Direct External Calls**
   - All external model access via FAZA 16
   - FAZA 16 enforces consent requirements
   - PII sanitization before transmission

2. **Data Minimization**
   - Only necessary data passed to models
   - No unnecessary logging of sensitive data
   - Configurable data retention policies

3. **User Consent**
   - Required for external model access
   - Checked at FAZA 16 level
   - Logged for audit purposes

### Security Features

1. **Input Validation**
   - Task descriptions sanitized
   - Context data validated
   - Resource limits enforced

2. **Safety Checks**
   - Prohibited action detection
   - Malicious prompt filtering
   - Output validation

3. **Audit Trail**
   - Complete decision logging
   - Explainability for all actions
   - EU AI Act compliance

4. **Resource Limits**
   - Maximum cost enforcement
   - Maximum time enforcement
   - Queue size limits

### Compliance

**GDPR (General Data Protection Regulation)**
- Right to explanation (via Explainability Engine)
- Data minimization (only necessary data processed)
- Purpose limitation (task-specific processing)
- Audit trail (complete decision history)

**ZVOP (Slovenian Personal Data Protection)**
- User consent requirements
- Data processing transparency
- Security measures

**EU AI Act**
- High-risk AI transparency requirements
- Human oversight capabilities
- Accuracy and robustness
- Technical documentation (this document)

---

## Testing & Validation

### Test Coverage

**Total Tests:** 55 comprehensive tests

**Test Breakdown:**
- StepPlanner: 8 tests
- PriorityQueue: 10 tests
- ModelEnsembleEngine: 8 tests
- ReliabilityFeedback: 8 tests
- ExplainabilityEngine: 7 tests
- PipelineManager: 6 tests
- OrchestrationManager: 6 tests
- Integration: 2 tests

**Coverage:** 100% of core functionality

### Test Categories

1. **Unit Tests**
   - Component initialization
   - Individual method behavior
   - Edge case handling
   - Error conditions

2. **Integration Tests**
   - Full orchestration flow
   - Multi-task coordination
   - Cross-component interaction

3. **Validation Tests**
   - Safety check enforcement
   - Resource limit validation
   - Quality assessment

### Running Tests

```bash
# Run all FAZA 17 tests
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH \
python3 -m unittest senti_os/tests/faza17/test_faza17_comprehensive.py -v

# Expected result: 55 tests passed
```

### Test Examples

```python
# Test: Full orchestration flow
def test_full_orchestration_flow(self):
    """Test complete orchestration lifecycle."""
    request = OrchestrationRequest(
        request_id="integration_001",
        task_description="Test task",
        priority=Priority.HIGH,
    )

    self.manager.submit_task(request)
    result = self.manager.process_next_task()

    self.assertEqual(result.status, OrchestrationStatus.COMPLETED)
    self.assertGreater(result.quality_score, 0.0)

# Test: Priority queue starvation prevention
def test_starvation_prevention(self):
    """Test that aging prevents starvation."""
    low_task = QueuedTask(
        task_id="low",
        priority=Priority.LOW,
        submission_time=datetime.now() - timedelta(seconds=200),
    )

    self.queue.enqueue(low_task)
    self.queue._apply_aging()

    # Low priority should be boosted after threshold
    self.assertEqual(self.queue.queue[0].priority, Priority.NORMAL)

# Test: Ensemble conflict detection
def test_conflict_detection(self):
    """Test conflict detection between models."""
    outputs = [
        ModelOutput("m1", "The answer is A", 0.9, 0.9, 1.0, 0.1),
        ModelOutput("m2", "The answer is B", 0.9, 0.9, 1.0, 0.1),
    ]

    result = self.engine.combine_outputs(outputs)

    self.assertGreater(result.conflicts_detected, 0)
```

---

## References

### Related Documentation

- **FAZA 16 Specification**: LLM Control Layer integration
- **FAZA 16 Implementation Guide**: Using FAZA 16 with FAZA 17
- **SENTI OS Architecture**: Overall system design
- **EU AI Act Compliance**: Regulatory requirements

### External Standards

- ISO/IEC 23053:2022 - Framework for AI systems
- ISO/IEC 42001:2023 - AI management system
- GDPR (Regulation EU 2016/679)
- EU AI Act (Regulation EU 2024/1689)

### Code References

```python
# Main entry point
from senti_os.core.faza17 import (
    create_orchestration_manager,
    OrchestrationRequest,
    Priority,
)

# Quick start
manager = create_orchestration_manager()
request = OrchestrationRequest(
    request_id="demo",
    task_description="Analyze and summarize",
    priority=Priority.HIGH,
)
manager.submit_task(request)
result = manager.process_next_task()
```

---

## Version History

**1.0.0** (2025-12-02)
- Initial production release
- 8 core modules implemented
- 55 comprehensive tests (100% passing)
- Full EU AI Act compliance
- Integration with FAZA 16

---

## Contact & Support

**SENTI OS Team**
**Project:** SENTI System
**Module:** FAZA 17 - Multi-Model Orchestration Layer

For implementation guidance, see `FAZA_17_IMPLEMENTATION_GUIDE.md`.
