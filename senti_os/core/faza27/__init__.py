"""
FAZA 27 – TaskGraph Engine

Advanced task execution graph with DAG structure, dependency management,
analysis, and integration with FAZA 25/26/28/28.5.

Provides:
- Task nodes with status tracking and cost models
- Task edges with dependency types and constraints
- TaskGraph with cycle detection and topological sorting
- Graph builder for FAZA 25/26 conversion
- Graph analyzer for bottleneck detection and health scoring
- Graph exporter for JSON, DOT, Markdown, YAML formats
- Graph monitor for FAZA 28/28.5 integration

Architecture:
    TaskNode        - Individual task with metadata and status
    TaskEdge        - Dependency/constraint between tasks
    TaskGraph       - Main DAG structure with validation
    GraphBuilder    - FAZA 25/26 to TaskGraph conversion
    GraphAnalyzer   - Cycle detection, influence ranking, health scoring
    GraphExporter   - Multi-format export (JSON, DOT, MD, YAML)
    GraphMonitor    - Live monitoring with FAZA 28/28.5 integration

Usage:
    from senti_os.core.faza27 import (
        TaskGraph,
        TaskNode,
        TaskEdge,
        NodeStatus,
        EdgeType,
        create_graph_builder,
        create_graph_analyzer,
        create_graph_exporter,
        create_graph_monitor
    )

    # Create graph
    graph = TaskGraph(graph_id="my_pipeline")

    # Add nodes
    node1 = TaskNode(node_id="task1", name="Fetch Data", priority=8)
    node2 = TaskNode(node_id="task2", name="Process Data", priority=7)
    graph.add_node(node1)
    graph.add_node(node2)

    # Add edge
    edge = TaskEdge(source_id="task1", target_id="task2")
    graph.add_edge(edge)

    # Analyze
    analyzer = create_graph_analyzer(graph)
    health = analyzer.calculate_graph_health()
    bottlenecks = analyzer.find_bottlenecks()

    # Export
    exporter = create_graph_exporter(graph)
    exporter.save_to_file("graph.json", format="json")
    exporter.save_to_file("graph.dot", format="dot")

Features:
- Zero external dependencies (stdlib only)
- Full type hints and docstrings
- Comprehensive error handling
- DAG validation with cycle detection
- Critical path analysis
- Parallelization analysis
- Resource cost estimation
- Multi-format export
- Real-time monitoring integration
"""

# Task Node
from senti_os.core.faza27.task_node import (
    TaskNode,
    NodeStatus,
    CostModel
)

# Task Edge
from senti_os.core.faza27.task_edge import (
    TaskEdge,
    EdgeType
)

# Task Graph
from senti_os.core.faza27.task_graph import (
    TaskGraph
)

# Graph Builder
from senti_os.core.faza27.graph_builder import (
    GraphBuilder,
    create_graph_builder
)

# Graph Analyzer
from senti_os.core.faza27.graph_analyzer import (
    GraphAnalyzer,
    create_graph_analyzer
)

# Graph Exporter
from senti_os.core.faza27.graph_exporter import (
    GraphExporter,
    create_graph_exporter
)

# Graph Monitor
from senti_os.core.faza27.graph_monitor import (
    GraphMonitor,
    create_graph_monitor
)


__all__ = [
    # Task Node
    "TaskNode",
    "NodeStatus",
    "CostModel",

    # Task Edge
    "TaskEdge",
    "EdgeType",

    # Task Graph
    "TaskGraph",

    # Graph Builder
    "GraphBuilder",
    "create_graph_builder",

    # Graph Analyzer
    "GraphAnalyzer",
    "create_graph_analyzer",

    # Graph Exporter
    "GraphExporter",
    "create_graph_exporter",

    # Graph Monitor
    "GraphMonitor",
    "create_graph_monitor",
]


__version__ = "1.0.0"
__author__ = "Senti System - FAZA 27 TaskGraph Engine"
__description__ = "Advanced task execution graph with DAG structure and comprehensive analysis"
