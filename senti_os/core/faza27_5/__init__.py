"""
FAZA 27.5 - Execution Optimizer Layer (XOL)

Intelligent task graph optimization for Senti OS.

Provides:
- Task graph validation
- DAG optimization (reordering, batching, redundancy elimination)
- Cost-based task scheduling
- Short-circuit optimizations
- Performance estimation
- Integration with FAZA 25 & 26

Note: Currently uses mock TaskGraph implementation.
Will integrate with FAZA 27 when available.

Usage:
    from senti_os.core.faza27_5 import get_optimizer, create_sample_graph

    # Create sample graph
    graph = create_sample_graph()

    # Get optimizer
    optimizer = get_optimizer()

    # Optimize graph
    optimized_graph, report = optimizer.optimize(graph)

    # Print report
    print(report.format_text())

    # Export to FAZA 25
    task_specs = optimizer.export_to_faza25(optimized_graph)
"""

# Task Graph (Mock for FAZA 27)
from senti_os.core.faza27_5.task_graph import (
    TaskGraph,
    TaskNode,
    TaskType,
    create_sample_graph
)

# Validation
from senti_os.core.faza27_5.graph_validator import (
    GraphValidator,
    ValidationError,
    create_graph_validator
)

# Optimization
from senti_os.core.faza27_5.graph_optimizer import (
    GraphOptimizer,
    create_graph_optimizer
)

from senti_os.core.faza27_5.optimization_passes import (
    OptimizationPass,
    Pass1_DAGReordering,
    Pass2_RedundancyElimination,
    Pass3_TaskBatching,
    Pass4_ShortCircuiting,
    Pass5_CostBasedSorting,
    OptimizationPipeline,
    create_optimization_pipeline
)

# Reporting
from senti_os.core.faza27_5.optimization_report import (
    OptimizationReport,
    ReportBuilder,
    create_report_builder
)

# Main Manager
from senti_os.core.faza27_5.optimizer_manager import (
    OptimizerManager,
    create_optimizer_manager,
    get_optimizer
)


__all__ = [
    # Task Graph (Mock)
    "TaskGraph",
    "TaskNode",
    "TaskType",
    "create_sample_graph",

    # Validation
    "GraphValidator",
    "ValidationError",
    "create_graph_validator",

    # Optimization
    "GraphOptimizer",
    "create_graph_optimizer",

    # Optimization Passes
    "OptimizationPass",
    "Pass1_DAGReordering",
    "Pass2_RedundancyElimination",
    "Pass3_TaskBatching",
    "Pass4_ShortCircuiting",
    "Pass5_CostBasedSorting",
    "OptimizationPipeline",
    "create_optimization_pipeline",

    # Reporting
    "OptimizationReport",
    "ReportBuilder",
    "create_report_builder",

    # Main Manager (primary API)
    "OptimizerManager",
    "create_optimizer_manager",
    "get_optimizer",
]


__version__ = "1.0.0"
__author__ = "Senti System"
__description__ = "FAZA 27.5 - Execution Optimizer Layer"
