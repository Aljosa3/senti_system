"""
FAZA 27.5 - Execution Optimizer Layer
Graph Validator

Validates task graph consistency:
- Detects cycles (DAG requirement)
- Validates dependencies exist
- Checks for orphan nodes
- Ensures minimal schema compliance
"""

import logging
from typing import Set, List, Dict, Optional
from senti_os.core.faza27_5.task_graph import TaskGraph, TaskNode

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when graph validation fails"""
    pass


class GraphValidator:
    """
    Validates task graphs for consistency and correctness.

    Checks:
    - Graph is acyclic (DAG property)
    - All dependencies exist
    - No orphan nodes (unless intended)
    - Task schema compliance
    """

    def __init__(self):
        """Initialize validator"""
        logger.info("GraphValidator initialized")

    def validate(self, graph: TaskGraph) -> Dict[str, any]:
        """
        Validate entire graph.

        Args:
            graph: Task graph to validate

        Returns:
            Validation result dictionary:
            {
                "valid": bool,
                "errors": list,
                "warnings": list,
                "stats": dict
            }

        Raises:
            ValidationError: If critical validation fails
        """
        errors = []
        warnings = []

        # Check if graph is empty
        if len(graph) == 0:
            warnings.append("Graph is empty")
            return {
                "valid": True,
                "errors": errors,
                "warnings": warnings,
                "stats": {"nodes": 0, "edges": 0}
            }

        # Run validation checks
        try:
            self._validate_dependencies(graph, errors)
            self._detect_cycles(graph, errors)
            self._check_orphans(graph, warnings)
            self._validate_schema(graph, errors, warnings)
        except ValidationError as e:
            errors.append(str(e))

        # Compute stats
        stats = self._compute_stats(graph)

        valid = len(errors) == 0

        if valid:
            logger.info(f"Graph validation passed: {stats['nodes']} nodes, {stats['edges']} edges")
        else:
            logger.error(f"Graph validation failed with {len(errors)} errors")

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "stats": stats
        }

    def _validate_dependencies(self, graph: TaskGraph, errors: List[str]) -> None:
        """Check that all dependencies exist in graph"""
        for node_id, node in graph.nodes.items():
            for dep_id in node.dependencies:
                if dep_id not in graph.nodes:
                    errors.append(
                        f"Node '{node_id}' has missing dependency: '{dep_id}'"
                    )

            for dep_id in node.dependents:
                if dep_id not in graph.nodes:
                    errors.append(
                        f"Node '{node_id}' has missing dependent: '{dep_id}'"
                    )

    def _detect_cycles(self, graph: TaskGraph, errors: List[str]) -> None:
        """
        Detect cycles in graph using DFS.
        Graph must be a DAG (directed acyclic graph).
        """
        WHITE = 0  # Not visited
        GRAY = 1   # Currently visiting
        BLACK = 2  # Finished visiting

        colors = {node_id: WHITE for node_id in graph.nodes}
        cycle_path = []

        def dfs(node_id: str, path: List[str]) -> bool:
            """DFS with cycle detection"""
            if colors[node_id] == GRAY:
                # Found cycle
                cycle_start = path.index(node_id)
                cycle_path.extend(path[cycle_start:] + [node_id])
                return True

            if colors[node_id] == BLACK:
                return False

            colors[node_id] = GRAY
            path.append(node_id)

            node = graph.nodes[node_id]
            for dep_id in node.dependents:
                if dep_id in graph.nodes:
                    if dfs(dep_id, path):
                        return True

            path.pop()
            colors[node_id] = BLACK
            return False

        # Check each node
        for node_id in graph.nodes:
            if colors[node_id] == WHITE:
                if dfs(node_id, []):
                    cycle_str = " -> ".join(cycle_path)
                    errors.append(f"Cycle detected: {cycle_str}")
                    return  # Stop after first cycle

    def _check_orphans(self, graph: TaskGraph, warnings: List[str]) -> None:
        """Check for orphan nodes (no dependencies and no dependents)"""
        for node_id, node in graph.nodes.items():
            if not node.dependencies and not node.dependents:
                warnings.append(
                    f"Orphan node detected: '{node_id}' has no dependencies or dependents"
                )

    def _validate_schema(
        self,
        graph: TaskGraph,
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """Validate that each node meets minimal schema requirements"""
        for node_id, node in graph.nodes.items():
            # Check required fields
            if not node.name:
                warnings.append(f"Node '{node_id}' has empty name")

            if not node.task_type:
                errors.append(f"Node '{node_id}' has no task_type")

            # Check priority range
            if node.priority < 0 or node.priority > 10:
                warnings.append(
                    f"Node '{node_id}' has priority {node.priority} outside range [0, 10]"
                )

            # Check estimated duration
            if node.estimated_duration < 0:
                warnings.append(
                    f"Node '{node_id}' has negative estimated_duration"
                )

            # Check resource values
            if node.cpu_load < 0 or node.cpu_load > 1:
                warnings.append(
                    f"Node '{node_id}' has cpu_load {node.cpu_load} outside range [0, 1]"
                )

            if node.memory_mb < 0:
                warnings.append(
                    f"Node '{node_id}' has negative memory_mb"
                )

    def _compute_stats(self, graph: TaskGraph) -> Dict[str, any]:
        """Compute graph statistics"""
        total_edges = sum(len(node.dependencies) for node in graph.nodes.values())

        return {
            "nodes": len(graph),
            "edges": total_edges,
            "root_nodes": len(graph.root_nodes),
            "leaf_nodes": len(graph.leaf_nodes),
            "avg_dependencies": total_edges / len(graph) if len(graph) > 0 else 0
        }

    def quick_check(self, graph: TaskGraph) -> bool:
        """
        Quick validation check (returns True/False only).

        Args:
            graph: Task graph to check

        Returns:
            True if valid, False otherwise
        """
        result = self.validate(graph)
        return result["valid"]


def create_graph_validator() -> GraphValidator:
    """Factory function for GraphValidator"""
    return GraphValidator()
