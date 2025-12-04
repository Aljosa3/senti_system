"""
FAZA 27.5 - Execution Optimizer Layer
Graph Optimizer

Optimizes task graphs through:
- DAG reordering for better parallelization
- Task batching for efficiency
- Redundancy elimination
- Short-circuit optimizations
"""

import logging
from typing import List, Set, Dict
from senti_os.core.faza27_5.task_graph import TaskGraph, TaskNode, TaskType

logger = logging.getLogger(__name__)


class GraphOptimizer:
    """
    Optimizes task execution graphs for performance.

    Strategies:
    - Reorder tasks to maximize parallelism
    - Batch similar tasks together
    - Eliminate redundant operations
    - Apply short-circuit logic
    """

    def __init__(self):
        """Initialize optimizer"""
        logger.info("GraphOptimizer initialized")

    def optimize(self, graph: TaskGraph) -> TaskGraph:
        """
        Apply all optimizations to the graph.

        Args:
            graph: Input task graph

        Returns:
            Optimized task graph
        """
        optimized = graph.clone()

        # Apply optimizations in sequence
        optimized = self._eliminate_redundant_tasks(optimized)
        optimized = self._reorder_for_parallelism(optimized)
        optimized = self._batch_similar_tasks(optimized)
        optimized = self._apply_short_circuits(optimized)

        logger.info(f"Optimized graph: {len(graph)} -> {len(optimized)} nodes")
        return optimized

    def _eliminate_redundant_tasks(self, graph: TaskGraph) -> TaskGraph:
        """Remove duplicate/redundant tasks"""
        seen_signatures = {}
        to_remove = set()

        for node_id, node in graph.nodes.items():
            # Create signature based on task properties
            sig = (node.name, node.task_type, tuple(sorted(node.dependencies)))

            if sig in seen_signatures:
                # Found duplicate - mark for removal
                original_id = seen_signatures[sig]
                to_remove.add(node_id)

                # Redirect dependents to original
                for dep_id in node.dependents:
                    dep_node = graph.nodes[dep_id]
                    dep_node.dependencies.discard(node_id)
                    dep_node.dependencies.add(original_id)
                    graph.nodes[original_id].dependents.add(dep_id)
            else:
                seen_signatures[sig] = node_id

        # Remove redundant nodes
        for node_id in to_remove:
            del graph.nodes[node_id]
            graph.root_nodes.discard(node_id)
            graph.leaf_nodes.discard(node_id)

        if to_remove:
            logger.info(f"Eliminated {len(to_remove)} redundant tasks")

        return graph

    def _reorder_for_parallelism(self, graph: TaskGraph) -> TaskGraph:
        """
        Reorder tasks to maximize parallel execution opportunities.
        Priority adjustments to group parallelizable tasks.
        """
        levels = graph.get_execution_order()

        # Adjust priorities by level (earlier levels get higher priority)
        max_level = len(levels)
        for level_idx, level in enumerate(levels):
            base_priority = max_level - level_idx
            for node_id in level:
                node = graph.nodes[node_id]
                node.priority = base_priority

        logger.debug(f"Reordered {len(graph)} nodes across {len(levels)} levels")
        return graph

    def _batch_similar_tasks(self, graph: TaskGraph) -> TaskGraph:
        """
        Identify and batch similar tasks that can be executed together.
        Groups tasks of same type at same level.
        """
        levels = graph.get_execution_order()

        for level in levels:
            # Group by task type
            type_groups: Dict[TaskType, List[str]] = {}
            for node_id in level:
                node = graph.nodes[node_id]
                if node.task_type not in type_groups:
                    type_groups[node.task_type] = []
                type_groups[node.task_type].append(node_id)

            # Mark batches in metadata
            for task_type, node_ids in type_groups.items():
                if len(node_ids) > 1:
                    batch_id = f"batch_{task_type.value}_{id(node_ids)}"
                    for node_id in node_ids:
                        graph.nodes[node_id].metadata["batch_id"] = batch_id
                        graph.nodes[node_id].metadata["batchable"] = True

        return graph

    def _apply_short_circuits(self, graph: TaskGraph) -> TaskGraph:
        """
        Apply short-circuit optimizations.
        Skip tasks whose results can be predetermined.
        """
        for node_id, node in list(graph.nodes.items()):
            # Skip if result is cacheable and likely cached
            if node.cacheable and node.cache_key:
                node.metadata["can_skip"] = True

            # Skip pure computation tasks with no side effects
            if node.task_type == TaskType.GENERIC and not node.dependents:
                if "side_effects" not in node.metadata:
                    node.metadata["can_skip"] = True

        return graph

    def get_parallelization_score(self, graph: TaskGraph) -> float:
        """
        Calculate parallelization score (0.0 to 1.0).
        Higher = more parallelism possible.
        """
        levels = graph.get_execution_order()
        if not levels:
            return 0.0

        total_nodes = len(graph)
        max_parallel = max(len(level) for level in levels)

        # Score based on average parallelism
        avg_parallel = sum(len(level) for level in levels) / len(levels)
        score = avg_parallel / total_nodes if total_nodes > 0 else 0.0

        return min(score, 1.0)


def create_graph_optimizer() -> GraphOptimizer:
    """Factory function for GraphOptimizer"""
    return GraphOptimizer()
