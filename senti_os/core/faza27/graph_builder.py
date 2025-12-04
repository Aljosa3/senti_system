"""
FAZA 27 – TaskGraph Engine
Graph Builder

Converts FAZA 25 tasks and FAZA 26 workflows into TaskGraph format.
Provides dependency detection and cost estimation.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

from senti_os.core.faza27.task_graph import TaskGraph
from senti_os.core.faza27.task_node import TaskNode, NodeStatus, CostModel
from senti_os.core.faza27.task_edge import TaskEdge, EdgeType

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Builds TaskGraphs from FAZA 25/26 structures.

    Converts pipeline tasks and command workflows into execution graphs
    with automatic dependency detection and cost estimation.
    """

    def __init__(self):
        """Initialize graph builder"""
        # Task type to cost model mapping
        self.cost_models: Dict[str, CostModel] = {
            "data_fetch": CostModel(estimated_duration=2.0, cpu_units=1.0, memory_mb=256, io_operations=100),
            "computation": CostModel(estimated_duration=5.0, cpu_units=4.0, memory_mb=512, io_operations=10),
            "aggregation": CostModel(estimated_duration=1.0, cpu_units=1.0, memory_mb=128, io_operations=20),
            "visualization": CostModel(estimated_duration=3.0, cpu_units=2.0, memory_mb=256, io_operations=50),
            "data_io": CostModel(estimated_duration=2.5, cpu_units=1.0, memory_mb=256, io_operations=200),
            "transformation": CostModel(estimated_duration=4.0, cpu_units=2.0, memory_mb=512, io_operations=50),
            "validation": CostModel(estimated_duration=2.0, cpu_units=1.0, memory_mb=128, io_operations=30),
            "model_io": CostModel(estimated_duration=10.0, cpu_units=2.0, memory_mb=1024, io_operations=500),
            "preprocessing": CostModel(estimated_duration=3.0, cpu_units=2.0, memory_mb=512, io_operations=20),
            "inference": CostModel(estimated_duration=15.0, cpu_units=8.0, memory_mb=2048, io_operations=10),
            "postprocessing": CostModel(estimated_duration=2.0, cpu_units=1.0, memory_mb=256, io_operations=20),
            "pipeline": CostModel(estimated_duration=20.0, cpu_units=4.0, memory_mb=1024, io_operations=100),
            "generic": CostModel(estimated_duration=1.0, cpu_units=1.0, memory_mb=128, io_operations=10),
        }

        # Dependency patterns for automatic edge detection
        self.dependency_patterns: Dict[str, List[str]] = {
            "compute_sentiment": ["fetch_data"],
            "aggregate_results": ["compute_sentiment"],
            "generate_plot": ["aggregate_results"],
            "transform_data": ["load_data"],
            "validate_data": ["transform_data"],
            "save_data": ["validate_data"],
            "preprocess_input": ["load_model"],
            "run_inference": ["preprocess_input", "load_model"],
            "postprocess_output": ["run_inference"],
        }

    def from_faza25_task(
        self,
        task: Any,
        graph_id: str = "faza25_graph"
    ) -> TaskGraph:
        """
        Convert FAZA 25 Task to TaskGraph.

        Args:
            task: FAZA 25 Task object
            graph_id: Graph identifier

        Returns:
            TaskGraph with single node
        """
        graph = TaskGraph(graph_id=graph_id, metadata={"source": "faza25", "original_task_id": task.id})

        # Convert status
        status_map = {
            "queued": NodeStatus.PENDING,
            "running": NodeStatus.RUNNING,
            "done": NodeStatus.COMPLETED,
            "error": NodeStatus.FAILED,
            "cancelled": NodeStatus.CANCELLED,
        }
        status = status_map.get(task.status.value, NodeStatus.PENDING)

        # Estimate cost model from task_type
        cost_model = self.cost_models.get(task.task_type, self.cost_models["generic"])

        # Create node
        node = TaskNode(
            node_id=task.id,
            name=task.name,
            node_type=task.task_type,
            priority=task.priority,
            cost_model=cost_model,
            metadata={
                "context": task.context,
                "created_at": task.created_at.isoformat() if hasattr(task, 'created_at') else None,
            }
        )
        node.status = status

        # Set timing if available
        if hasattr(task, 'started_at') and task.started_at:
            node.start_time = task.started_at
        if hasattr(task, 'completed_at') and task.completed_at:
            node.end_time = task.completed_at

        graph.add_node(node)

        logger.info(f"Converted FAZA 25 task {task.id} to TaskGraph")
        return graph

    def from_faza25_tasks(
        self,
        tasks: List[Any],
        graph_id: str = "faza25_pipeline",
        detect_dependencies: bool = True
    ) -> TaskGraph:
        """
        Convert list of FAZA 25 Tasks to TaskGraph.

        Args:
            tasks: List of FAZA 25 Task objects
            graph_id: Graph identifier
            detect_dependencies: Auto-detect dependencies based on task order

        Returns:
            TaskGraph with multiple nodes
        """
        graph = TaskGraph(graph_id=graph_id, metadata={"source": "faza25", "task_count": len(tasks)})

        # Add all nodes
        for task in tasks:
            status_map = {
                "queued": NodeStatus.PENDING,
                "running": NodeStatus.RUNNING,
                "done": NodeStatus.COMPLETED,
                "error": NodeStatus.FAILED,
                "cancelled": NodeStatus.CANCELLED,
            }
            status = status_map.get(task.status.value, NodeStatus.PENDING)

            cost_model = self.cost_models.get(task.task_type, self.cost_models["generic"])

            node = TaskNode(
                node_id=task.id,
                name=task.name,
                node_type=task.task_type,
                priority=task.priority,
                cost_model=cost_model,
                metadata={"context": task.context}
            )
            node.status = status
            graph.add_node(node)

        # Add dependencies based on order (sequential pipeline)
        if detect_dependencies and len(tasks) > 1:
            for i in range(len(tasks) - 1):
                edge = TaskEdge(
                    source_id=tasks[i].id,
                    target_id=tasks[i + 1].id,
                    edge_type=EdgeType.DEPENDENCY
                )
                graph.add_edge(edge)

        logger.info(f"Converted {len(tasks)} FAZA 25 tasks to TaskGraph with {len(graph.edges)} edges")
        return graph

    def from_faza26_workflow(
        self,
        task_specs: List[Dict[str, Any]],
        graph_id: str = "faza26_workflow"
    ) -> TaskGraph:
        """
        Convert FAZA 26 workflow (semantic planner output) to TaskGraph.

        Args:
            task_specs: List of task specifications from SemanticPlanner.plan()
                Format: [{"task": "name", "priority": 5, "metadata": {...}}, ...]
            graph_id: Graph identifier

        Returns:
            TaskGraph with dependency edges
        """
        graph = TaskGraph(graph_id=graph_id, metadata={"source": "faza26", "task_count": len(task_specs)})

        # Create nodes
        node_map: Dict[str, str] = {}  # task_name -> node_id
        for idx, spec in enumerate(task_specs):
            task_name = spec.get("task", f"task_{idx}")
            priority = spec.get("priority", 5)
            metadata = spec.get("metadata", {})
            task_type = metadata.get("task_type", "generic")

            # Generate node ID
            node_id = f"{task_name}_{idx}"
            node_map[task_name] = node_id

            # Get cost model
            cost_model = self.cost_models.get(task_type, self.cost_models["generic"])

            # Create node
            node = TaskNode(
                node_id=node_id,
                name=task_name,
                node_type=task_type,
                priority=priority,
                cost_model=cost_model,
                metadata=metadata
            )
            graph.add_node(node)

        # Auto-detect dependencies using pattern matching
        for idx, spec in enumerate(task_specs):
            task_name = spec.get("task", f"task_{idx}")
            node_id = node_map[task_name]

            # Check dependency patterns
            if task_name in self.dependency_patterns:
                for dep_name in self.dependency_patterns[task_name]:
                    # Find matching dependency node
                    for prev_idx in range(idx):
                        prev_spec = task_specs[prev_idx]
                        prev_name = prev_spec.get("task", f"task_{prev_idx}")
                        if prev_name == dep_name:
                            prev_node_id = node_map[prev_name]
                            edge = TaskEdge(
                                source_id=prev_node_id,
                                target_id=node_id,
                                edge_type=EdgeType.DEPENDENCY
                            )
                            try:
                                graph.add_edge(edge)
                            except ValueError:
                                # Skip if edge creates cycle
                                logger.warning(f"Skipping edge {prev_node_id} -> {node_id} (cycle detected)")

        logger.info(f"Converted FAZA 26 workflow with {len(task_specs)} tasks to TaskGraph")
        return graph

    def from_faza26_sequential(
        self,
        task_specs: List[Dict[str, Any]],
        graph_id: str = "faza26_sequential"
    ) -> TaskGraph:
        """
        Convert FAZA 26 workflow to TaskGraph with sequential dependencies.

        Creates a linear chain where each task depends on the previous one.

        Args:
            task_specs: List of task specifications
            graph_id: Graph identifier

        Returns:
            TaskGraph with sequential edges
        """
        graph = TaskGraph(graph_id=graph_id, metadata={"source": "faza26", "mode": "sequential"})

        node_ids: List[str] = []

        # Create nodes
        for idx, spec in enumerate(task_specs):
            task_name = spec.get("task", f"task_{idx}")
            priority = spec.get("priority", 5)
            metadata = spec.get("metadata", {})
            task_type = metadata.get("task_type", "generic")

            node_id = f"{task_name}_{idx}"
            node_ids.append(node_id)

            cost_model = self.cost_models.get(task_type, self.cost_models["generic"])

            node = TaskNode(
                node_id=node_id,
                name=task_name,
                node_type=task_type,
                priority=priority,
                cost_model=cost_model,
                metadata=metadata
            )
            graph.add_node(node)

        # Create sequential edges
        for i in range(len(node_ids) - 1):
            edge = TaskEdge(
                source_id=node_ids[i],
                target_id=node_ids[i + 1],
                edge_type=EdgeType.DEPENDENCY
            )
            graph.add_edge(edge)

        logger.info(f"Created sequential TaskGraph with {len(node_ids)} nodes")
        return graph

    def merge_graphs(
        self,
        graphs: List[TaskGraph],
        merged_graph_id: str = "merged_graph"
    ) -> TaskGraph:
        """
        Merge multiple TaskGraphs into one.

        Args:
            graphs: List of TaskGraph objects to merge
            merged_graph_id: ID for merged graph

        Returns:
            Merged TaskGraph
        """
        merged = TaskGraph(
            graph_id=merged_graph_id,
            metadata={"source": "merged", "source_graphs": [g.graph_id for g in graphs]}
        )

        # Track node ID conflicts
        node_id_map: Dict[str, str] = {}

        # Add all nodes
        for graph in graphs:
            for node in graph.get_all_nodes():
                new_node_id = f"{graph.graph_id}_{node.node_id}"
                node_id_map[node.node_id] = new_node_id

                new_node = TaskNode(
                    node_id=new_node_id,
                    name=node.name,
                    node_type=node.node_type,
                    priority=node.priority,
                    cost_model=node.cost_model,
                    metadata={**node.metadata, "source_graph": graph.graph_id}
                )
                new_node.status = node.status
                merged.add_node(new_node)

        # Add all edges
        for graph in graphs:
            for edge in graph.edges:
                source_id = f"{graph.graph_id}_{edge.source_id}"
                target_id = f"{graph.graph_id}_{edge.target_id}"

                new_edge = TaskEdge(
                    source_id=source_id,
                    target_id=target_id,
                    edge_type=edge.edge_type,
                    weight=edge.weight,
                    constraints=edge.constraints.copy(),
                    metadata=edge.metadata.copy()
                )
                merged.add_edge(new_edge)

        logger.info(f"Merged {len(graphs)} graphs into {merged_graph_id}")
        return merged

    def add_cost_model(self, task_type: str, cost_model: CostModel) -> None:
        """
        Register custom cost model for task type.

        Args:
            task_type: Task type identifier
            cost_model: CostModel to associate with task type
        """
        self.cost_models[task_type] = cost_model
        logger.info(f"Registered cost model for task type: {task_type}")

    def add_dependency_pattern(self, task_name: str, dependencies: List[str]) -> None:
        """
        Register dependency pattern for task.

        Args:
            task_name: Task name
            dependencies: List of task names this task depends on
        """
        self.dependency_patterns[task_name] = dependencies
        logger.info(f"Registered dependency pattern for {task_name}: {dependencies}")


def create_graph_builder() -> GraphBuilder:
    """
    Factory function to create GraphBuilder instance.

    Returns:
        GraphBuilder instance
    """
    return GraphBuilder()
