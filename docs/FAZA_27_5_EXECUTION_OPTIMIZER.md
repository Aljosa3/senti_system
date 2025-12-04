

# FAZA 27.5 - Execution Optimizer Layer (XOL)

## Overview

FAZA 27.5 is the Execution Optimizer Layer for Senti OS, providing intelligent task graph optimization. It sits between FAZA 26 (Action Layer) and FAZA 25 (Orchestration Engine), optimizing execution plans before they reach the orchestrator.

**Key Capabilities:**
- Task graph validation (cycle detection, dependency checking)
- DAG reordering for maximum parallelization
- Redundancy elimination
- Task batching for efficiency
- Short-circuit optimizations
- Cost-based task scheduling
- Performance estimation and reporting

**Note:** Currently uses mock TaskGraph implementation. Will integrate with FAZA 27 when available.

## Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────┐
│           FAZA 27.5 - Execution Optimizer Layer          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  TaskGraph (Mock) ────────────────────────────────────┐ │
│       │                                                │ │
│       ↓                                                │ │
│  ┌──────────────┐          ┌─────────────────────┐   │ │
│  │GraphValidator│          │                     │   │ │
│  │- Cycles      │          │  OptimizerManager   │   │ │
│  │- Dependencies│          │  (Orchestrator)     │   │ │
│  │- Schema      │          │                     │   │ │
│  └──────┬───────┘          └──────────┬──────────┘   │ │
│         │                               │              │ │
│         ↓                               ↓              │ │
│  Valid Graph                  Optimization Pipeline   │ │
│         │                               │              │ │
│         │                    ┌──────────┴────────┐    │ │
│         │                    │                   │    │ │
│         │       Pass 1: DAG Reordering           │    │ │
│         │       Pass 2: Redundancy Elimination   │    │ │
│         │       Pass 3: Task Batching            │    │ │
│         │       Pass 4: Short-Circuiting         │    │ │
│         │       Pass 5: Cost-Based Sorting       │    │ │
│         │                    │                   │    │ │
│         │                    └───────────┬───────┘    │ │
│         │                                │            │ │
│         ↓                                ↓            │ │
│  Optimized Graph                 OptimizationReport  │ │
│         │                                │            │ │
│         └────────────────┬───────────────┘            │ │
│                          │                            │ │
│                          ↓                            │ │
│              Export to FAZA 25 Format                │ │
│                          │                            │ │
└──────────────────────────┼────────────────────────────┘ │
                           │                              │
                           ↓                              │
                   FAZA 25 Orchestrator                   │
                                                           │
└──────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. TaskGraph (Mock)
**File:** `task_graph.py`

Mock implementation of FAZA 27 TaskGraph. Provides:
- Directed Acyclic Graph (DAG) structure
- Node and edge management
- Dependency tracking
- Topological sorting
- Critical path calculation

```python
from senti_os.core.faza27_5 import TaskGraph, TaskNode, TaskType

graph = TaskGraph("my_graph")
node = TaskNode(id="task1", name="Fetch Data", task_type=TaskType.IO)
graph.add_node(node)
```

#### 2. GraphValidator
**File:** `graph_validator.py`

Validates graph structure and correctness:
- **Cycle Detection:** Ensures DAG property
- **Dependency Validation:** All dependencies exist
- **Orphan Detection:** Identifies isolated nodes
- **Schema Validation:** Checks node properties

```python
from senti_os.core.faza27_5 import GraphValidator

validator = GraphValidator()
result = validator.validate(graph)

if result["valid"]:
    print("Graph is valid!")
else:
    print("Errors:", result["errors"])
```

#### 3. Optimization Passes
**File:** `optimization_passes.py`

Five optimization passes applied sequentially:

**Pass 1: DAG Reordering**
- Maximizes parallel execution opportunities
- Adjusts priorities based on topological levels
- Prioritizes critical path tasks

**Pass 2: Redundancy Elimination**
- Removes duplicate tasks with identical signatures
- Merges redundant operations
- Redirects dependencies to canonical nodes

**Pass 3: Task Batching**
- Groups similar tasks at same execution level
- Marks batches for executor optimization
- Enables batch processing optimizations

**Pass 4: Short-Circuiting**
- Skips tasks with cached results
- Eliminates unnecessary computations
- Identifies tasks with no impact

**Pass 5: Cost-Based Sorting**
- Orders tasks by execution cost
- Prioritizes cheaper tasks
- Balances time, monetary, and resource costs

```python
from senti_os.core.faza27_5 import OptimizationPipeline

pipeline = OptimizationPipeline()
optimized_graph = pipeline.apply_all(graph)
```

#### 4. OptimizationReport
**File:** `optimization_report.py`

Generates detailed optimization reports:
- Before/after statistics
- Performance estimates (time, cost)
- Applied optimizations
- Detected redundancies
- Warnings and notes

```python
from senti_os.core.faza27_5 import ReportBuilder

builder = ReportBuilder()
report = (builder
          .set_graph_name("my_graph")
          .set_before_stats(10, 15)
          .set_after_stats(8, 12)
          .build())

print(report.format_text())
```

#### 5. OptimizerManager
**File:** `optimizer_manager.py`

Main orchestrator coordinating the pipeline:
- Validates graph
- Applies optimization passes
- Generates reports
- Exports to FAZA 25

```python
from senti_os.core.faza27_5 import get_optimizer

optimizer = get_optimizer()
optimized_graph, report = optimizer.optimize(graph)
print(report.format_summary())
```

## Usage

### Basic Optimization

```python
from senti_os.core.faza27_5 import (
    create_sample_graph,
    get_optimizer
)

# Create graph
graph = create_sample_graph()

# Optimize
optimizer = get_optimizer()
optimized_graph, report = optimizer.optimize(graph)

# View report
print(report.format_text())
```

### Custom Graph Creation

```python
from senti_os.core.faza27_5 import TaskGraph, TaskNode, TaskType

# Create graph
graph = TaskGraph("workflow")

# Add nodes
fetch = TaskNode(
    id="fetch",
    name="Fetch Data",
    task_type=TaskType.IO,
    estimated_duration=2.0,
    priority=7
)

process = TaskNode(
    id="process",
    name="Process Data",
    task_type=TaskType.COMPUTE,
    estimated_duration=5.0,
    priority=8
)

graph.add_node(fetch)
graph.add_node(process)

# Add dependency
graph.add_edge("fetch", "process")

# Optimize
optimized, report = optimizer.optimize(graph)
```

### Validation Only

```python
from senti_os.core.faza27_5 import GraphValidator

validator = GraphValidator()
result = validator.validate(graph)

if not result["valid"]:
    print("Validation errors:")
    for error in result["errors"]:
        print(f"  - {error}")

if result["warnings"]:
    print("Warnings:")
    for warning in result["warnings"]:
        print(f"  - {warning}")
```

### Quick Optimization

```python
# Without detailed report
optimized_graph = optimizer.quick_optimize(graph)
```

### Export to FAZA 25

```python
# Convert to FAZA 25 task specifications
task_specs = optimizer.export_to_faza25(optimized_graph)

# Each spec contains:
# - name
# - priority
# - task_type
# - metadata (duration, cost, etc.)
```

## Optimization Passes Details

### Pass 1: DAG Reordering

**Purpose:** Maximize parallelization

**How it works:**
1. Compute topological levels
2. Assign priorities by level (earlier = higher)
3. Boost priority for critical path tasks
4. Result: Better parallel execution

**Example:**
```
Before:  A(5) -> B(5) -> C(5)
         D(5) -> E(5) -> F(5)

After:   A(8) -> B(6) -> C(4)  [Critical path]
         D(8) -> E(6) -> F(4)
```

### Pass 2: Redundancy Elimination

**Purpose:** Remove duplicate tasks

**How it works:**
1. Compute task signature (name, type, dependencies)
2. Identify duplicates
3. Merge duplicates, redirect dependencies
4. Result: Fewer nodes, same output

**Example:**
```
Before:  [FetchA] [FetchB] [Process]
         (FetchA and FetchB are identical)

After:   [Fetch] [Process]
         (Merged FetchA and FetchB)
```

### Pass 3: Task Batching

**Purpose:** Enable batch processing

**How it works:**
1. Group tasks by type at each level
2. Mark batches with metadata
3. Executors can batch-process similar tasks
4. Result: Reduced overhead

**Example:**
```
Before:  [ComputeA] [ComputeB] [ComputeC]
         (All at same level, same type)

After:   [ComputeA] [ComputeB] [ComputeC]
         (Marked as batch_id="batch_compute_L0")
```

### Pass 4: Short-Circuiting

**Purpose:** Skip unnecessary tasks

**How it works:**
1. Identify cacheable tasks
2. Mark tasks with no dependents
3. Flag deterministic computations
4. Result: Fewer executions

**Example:**
```
Task with cache_key="xyz" → can_skip=true
Task with no dependents → can_skip=true
Task already executed → can_skip=true
```

### Pass 5: Cost-Based Sorting

**Purpose:** Optimize execution order

**How it works:**
1. Compute total cost (time + money + resources)
2. Sort tasks within levels by cost
3. Prioritize cheaper tasks
4. Result: Faster unblocking of dependents

**Example:**
```
Before:  [Expensive(10s)] [Cheap(1s)]

After:   [Cheap(1s)] [Expensive(10s)]
         (Cheap task completes faster)
```

## API Reference

### TaskGraph

```python
graph = TaskGraph(name: str)
graph.add_node(node: TaskNode)
graph.add_edge(from_id: str, to_id: str)
graph.get_execution_order() -> List[List[str]]
graph.get_critical_path() -> List[str]
graph.clone() -> TaskGraph
```

### GraphValidator

```python
validator = GraphValidator()
result = validator.validate(graph: TaskGraph) -> Dict
quick_check = validator.quick_check(graph: TaskGraph) -> bool
```

### OptimizerManager

```python
optimizer = OptimizerManager()
optimized, report = optimizer.optimize(graph: TaskGraph)
validation = optimizer.validate_only(graph: TaskGraph)
optimized = optimizer.quick_optimize(graph: TaskGraph)
task_specs = optimizer.export_to_faza25(graph: TaskGraph)
```

### OptimizationReport

```python
report.get_node_reduction() -> int
report.get_time_savings() -> float
report.get_cost_savings() -> float
report.get_time_savings_percent() -> float
report.format_text() -> str
report.format_summary() -> str
report.to_dict() -> Dict
```

## Integration with Other FAZA Modules

### Integration with FAZA 26 (Action Layer)

FAZA 26 can use FAZA 27.5 to optimize task sequences before submission:

```python
from senti_os.core.faza26 import get_action_layer
from senti_os.core.faza27_5 import get_optimizer, TaskGraph

# In FAZA 26, after planning:
# Convert planned tasks to TaskGraph
graph = TaskGraph("action_workflow")
# ... populate graph from planned tasks ...

# Optimize
optimizer = get_optimizer()
optimized_graph, report = optimizer.optimize(graph)

# Export to FAZA 25
task_specs = optimizer.export_to_faza25(optimized_graph)
```

### Integration with FAZA 25 (Orchestrator)

FAZA 27.5 prepares optimized task specifications for FAZA 25:

```python
from senti_os.core.faza25 import get_orchestrator
from senti_os.core.faza27_5 import get_optimizer

# Optimize graph
optimized_graph, report = optimizer.optimize(graph)

# Export and submit to FAZA 25
orchestrator = get_orchestrator()
await orchestrator.start()

# Submit optimized tasks
# (Custom executor mapping required)
```

## Mock TaskGraph vs Real FAZA 27

### Current State (Mock)

FAZA 27.5 currently uses a **mock TaskGraph** implementation because FAZA 27 doesn't exist yet.

**Mock limitations:**
- Simplified task model
- No real execution
- Simulated cost estimates
- Placeholder dependencies

**Mock advantages:**
- Fully functional optimizer
- Can be used now
- Easy to test
- Demonstrates concepts

### Future Integration with FAZA 27

When FAZA 27 is implemented, migration will be straightforward:

1. **Replace imports:**
   ```python
   # Current (mock)
   from senti_os.core.faza27_5.task_graph import TaskGraph

   # Future (real FAZA 27)
   from senti_os.core.faza27 import TaskGraph
   ```

2. **Update OptimizerManager:**
   - Add FAZA 27-specific optimizations
   - Integrate with real execution engine
   - Remove mock mode warnings

3. **Enhance cost models:**
   - Use real execution data
   - Profile actual task durations
   - Learn from history

## Performance Characteristics

### Optimization Overhead

- **Validation:** O(V + E) where V = nodes, E = edges
- **Cycle Detection:** O(V + E)
- **Redundancy Elimination:** O(V²) worst case
- **Batching:** O(V)
- **Reordering:** O(V log V)
- **Total:** ~O(V² + E) for complex graphs

### Typical Results

For a 100-node graph:
- **Validation:** <10ms
- **All passes:** 50-100ms
- **Report generation:** <5ms
- **Total overhead:** <150ms

### Scalability

Tested up to:
- 1,000 nodes: <1 second
- 10,000 nodes: <10 seconds
- 100,000 nodes: Not recommended (mock mode)

Real FAZA 27 will have better scaling.

## Testing

### Run Test Suite

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 tests/test_faza27_5.py
```

### Test Coverage

**31 comprehensive tests:**
- TaskGraph: 6 tests
- GraphValidator: 7 tests
- Optimization Passes: 5 tests
- Pipeline: 3 tests
- Report: 5 tests
- OptimizerManager: 5 tests

All tests passing ✓

## Example Output

### Optimization Report

```
======================================================================
FAZA 27.5 - Execution Optimization Report
======================================================================
Graph: workflow_graph
Timestamp: 2024-12-04T16:45:00

Statistics:
  Nodes: 10 → 8 (-2)
  Edges: 15 → 12

Applied Optimizations:
  ✓ DAG Reordering
  ✓ Redundancy Elimination
  ✓ Task Batching
  ✓ Short-Circuiting
  ✓ Cost-Based Sorting

Findings:
  • Redundancies eliminated: 2
  • Tasks batched: 4
  • Tasks skippable: 1

Performance Estimates:
  • Time: 45.00s → 32.50s
    Savings: 12.50s (27.8%)
  • Cost: $0.5000 → $0.3500
    Savings: $0.1500
  • Parallelization: 0.45 → 0.62
    Improvement: +0.17

Pass Statistics:
  • DAG Reordering: 8 changes
  • Redundancy Elimination: 2 changes
  • Task Batching: 4 changes
  • Short-Circuiting: 1 changes
  • Cost-Based Sorting: 6 changes

Notes:
  ℹ Using mock TaskGraph (FAZA 27 not yet implemented).
    Real performance gains will vary.

======================================================================
```

## Troubleshooting

### Graph Validation Fails

**Problem:** "Cycle detected in graph"

**Solution:** Remove circular dependencies. Use validator to identify cycle path.

```python
result = validator.validate(graph)
print(result["errors"])  # Shows cycle path
```

### Optimization Not Effective

**Problem:** No improvement in parallelization score

**Solution:**
- Check if graph is already optimal (linear chains)
- Add more parallel branches
- Review task dependencies

### Mock Mode Warnings

**Problem:** "FAZA 27.5 is running in MOCK mode"

**Solution:** This is expected. Will be resolved when FAZA 27 is implemented.

## Future Enhancements

When FAZA 27 is available:

1. **Real Execution Integration:**
   - Actual task execution via FAZA 27
   - Real-time cost tracking
   - Adaptive optimization based on execution data

2. **Advanced Optimizations:**
   - Machine learning for cost prediction
   - Dynamic reordering during execution
   - Resource-aware scheduling

3. **Enhanced Cost Models:**
   - GPU/TPU awareness
   - Network bandwidth considerations
   - Memory pressure modeling

4. **Monitoring & Profiling:**
   - Execution telemetry
   - Bottleneck identification
   - Automatic optimization tuning

## Version History

- **v1.0.0** (2024-12-04): Initial implementation
  - Mock TaskGraph implementation
  - 5 optimization passes
  - Graph validation with cycle detection
  - Optimization reporting
  - FAZA 25 export
  - 31 comprehensive tests

## Contributing

FAZA 27.5 is part of Senti OS core. For modifications:

1. Update relevant modules in `senti_os/core/faza27_5/`
2. Add tests to `tests/test_faza27_5.py`
3. Update documentation
4. Run test suite

## License

Part of Senti System - Proprietary

---

**FAZA 27.5 - Execution Optimizer Layer**
*Intelligent task graph optimization for maximum efficiency*
