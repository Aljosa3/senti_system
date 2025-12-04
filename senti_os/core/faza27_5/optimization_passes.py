"""
FAZA 27.5 - Execution Optimizer Layer
Optimization Passes

Five optimization passes for task graphs:
1. DAG Reordering - Maximize parallel execution
2. Redundancy Elimination - Remove duplicate tasks
3. Task Batching - Combine similar tasks
4. Short-Circuiting - Skip unnecessary branches
5. Cost-Based Sorting - Order by execution cost
"""

import logging
from typing import Dict, List, Set
from senti_os.core.faza27_5.task_graph import TaskGraph, TaskNode, TaskType

logger = logging.getLogger(__name__)


class OptimizationPass:
    """Base class for optimization passes"""

    def __init__(self, name: str):
        self.name = name
        self.changes_made = 0

    def apply(self, graph: TaskGraph) -> TaskGraph:
        """Apply optimization pass. Must be overridden."""
        raise NotImplementedError

    def get_stats(self) -> Dict[str, any]:
        """Get statistics about changes made"""
        return {
            "pass_name": self.name,
            "changes": self.changes_made
        }


class Pass1_DAGReordering(OptimizationPass):
    """
    Pass 1: DAG Reordering

    Reorders tasks to maximize parallel execution opportunities.
    Adjusts priorities based on topological levels.
    """

    def __init__(self):
        super().__init__("DAG Reordering")

    def apply(self, graph: TaskGraph) -> TaskGraph:
        """Reorder DAG for better parallelism"""
        logger.debug(f"Applying {self.name}")

        levels = graph.get_execution_order()
        max_level = len(levels)

        for level_idx, level in enumerate(levels):
            # Higher priority for earlier levels
            base_priority = max_level - level_idx

            for node_id in level:
                node = graph.nodes[node_id]
                old_priority = node.priority

                # Adjust priority based on level and criticality
                if node_id in graph.get_critical_path():
                    node.priority = min(10, base_priority + 2)
                else:
                    node.priority = min(10, base_priority)

                if old_priority != node.priority:
                    self.changes_made += 1

        logger.info(f"{self.name}: reordered {self.changes_made} tasks across {max_level} levels")
        return graph


class Pass2_RedundancyElimination(OptimizationPass):
    """
    Pass 2: Redundancy Elimination

    Removes duplicate and redundant tasks.
    Merges tasks with identical signatures.
    """

    def __init__(self):
        super().__init__("Redundancy Elimination")

    def apply(self, graph: TaskGraph) -> TaskGraph:
        """Eliminate redundant tasks"""
        logger.debug(f"Applying {self.name}")

        seen_signatures = {}
        to_remove = set()

        for node_id, node in list(graph.nodes.items()):
            # Create signature
            sig = self._compute_signature(node)

            if sig in seen_signatures:
                # Found duplicate
                original_id = seen_signatures[sig]
                to_remove.add(node_id)

                # Redirect dependents to original
                for dep_id in node.dependents:
                    if dep_id in graph.nodes:
                        dep_node = graph.nodes[dep_id]
                        dep_node.dependencies.discard(node_id)
                        dep_node.dependencies.add(original_id)
                        if original_id in graph.nodes:
                            graph.nodes[original_id].dependents.add(dep_id)

                self.changes_made += 1
            else:
                seen_signatures[sig] = node_id

        # Remove redundant nodes
        for node_id in to_remove:
            del graph.nodes[node_id]
            graph.root_nodes.discard(node_id)
            graph.leaf_nodes.discard(node_id)

        logger.info(f"{self.name}: eliminated {self.changes_made} redundant tasks")
        return graph

    def _compute_signature(self, node: TaskNode) -> tuple:
        """Compute unique signature for a task"""
        return (
            node.name,
            node.task_type,
            tuple(sorted(node.dependencies)),
            node.cacheable,
            node.cache_key
        )


class Pass3_TaskBatching(OptimizationPass):
    """
    Pass 3: Task Batching

    Groups similar tasks that can be executed together.
    Marks batches in metadata for executor optimization.
    """

    def __init__(self):
        super().__init__("Task Batching")

    def apply(self, graph: TaskGraph) -> TaskGraph:
        """Batch similar tasks"""
        logger.debug(f"Applying {self.name}")

        levels = graph.get_execution_order()

        for level_idx, level in enumerate(levels):
            # Group by task type
            type_groups: Dict[TaskType, List[str]] = {}

            for node_id in level:
                node = graph.nodes[node_id]
                if node.task_type not in type_groups:
                    type_groups[node.task_type] = []
                type_groups[node.task_type].append(node_id)

            # Create batches for groups with 2+ tasks
            for task_type, node_ids in type_groups.items():
                if len(node_ids) >= 2:
                    batch_id = f"batch_{task_type.value}_L{level_idx}"

                    for node_id in node_ids:
                        node = graph.nodes[node_id]
                        node.metadata["batch_id"] = batch_id
                        node.metadata["batchable"] = True
                        node.metadata["batch_size"] = len(node_ids)

                    self.changes_made += len(node_ids)

        logger.info(f"{self.name}: created batches for {self.changes_made} tasks")
        return graph


class Pass4_ShortCircuiting(OptimizationPass):
    """
    Pass 4: Short-Circuiting

    Identifies tasks that can be skipped:
    - Cached results available
    - No side effects
    - Deterministic outcomes
    """

    def __init__(self):
        super().__init__("Short-Circuiting")

    def apply(self, graph: TaskGraph) -> TaskGraph:
        """Apply short-circuit optimizations"""
        logger.debug(f"Applying {self.name}")

        for node_id, node in graph.nodes.items():
            can_skip = False

            # Skip if cacheable with valid cache key
            if node.cacheable and node.cache_key:
                can_skip = True
                node.metadata["skip_reason"] = "cache_available"

            # Skip if no dependents and no side effects
            if not node.dependents and not node.metadata.get("side_effects"):
                if node.task_type == TaskType.GENERIC:
                    can_skip = True
                    node.metadata["skip_reason"] = "no_impact"

            # Skip if already executed (idempotent)
            if node.executed and node.result is not None:
                can_skip = True
                node.metadata["skip_reason"] = "already_executed"

            if can_skip:
                node.metadata["can_skip"] = True
                self.changes_made += 1

        logger.info(f"{self.name}: marked {self.changes_made} tasks for skipping")
        return graph


class Pass5_CostBasedSorting(OptimizationPass):
    """
    Pass 5: Cost-Based Sorting

    Reorders tasks within levels based on execution cost.
    Prioritizes cheaper tasks to unblock dependents faster.
    """

    def __init__(self):
        super().__init__("Cost-Based Sorting")

    def apply(self, graph: TaskGraph) -> TaskGraph:
        """Sort tasks by cost"""
        logger.debug(f"Applying {self.name}")

        levels = graph.get_execution_order()

        for level in levels:
            if len(level) <= 1:
                continue

            # Sort nodes by total cost (time + monetary + resource)
            level_nodes = [(node_id, graph.nodes[node_id]) for node_id in level]
            level_nodes.sort(key=lambda x: self._compute_cost(x[1]))

            # Adjust priorities within level
            for priority_offset, (node_id, node) in enumerate(level_nodes):
                old_priority = node.priority
                # Cheaper tasks get slightly higher priority
                node.priority = min(10, node.priority + (len(level_nodes) - priority_offset) // 10)

                if old_priority != node.priority:
                    self.changes_made += 1

        logger.info(f"{self.name}: re-sorted {self.changes_made} tasks by cost")
        return graph

    def _compute_cost(self, node: TaskNode) -> float:
        """Compute total cost metric for a task"""
        # Weighted cost: duration + monetary + resource pressure
        time_cost = node.estimated_duration
        monetary_cost = node.estimated_cost * 10  # Scale up
        resource_cost = node.cpu_load * 5 + node.memory_mb / 1000

        return time_cost + monetary_cost + resource_cost


class OptimizationPipeline:
    """
    Manages the complete optimization pipeline.
    Applies all passes in sequence.
    """

    def __init__(self):
        """Initialize pipeline with all passes"""
        self.passes = [
            Pass1_DAGReordering(),
            Pass2_RedundancyElimination(),
            Pass3_TaskBatching(),
            Pass4_ShortCircuiting(),
            Pass5_CostBasedSorting()
        ]
        logger.info(f"OptimizationPipeline initialized with {len(self.passes)} passes")

    def apply_all(self, graph: TaskGraph) -> TaskGraph:
        """
        Apply all optimization passes in sequence.

        Args:
            graph: Input task graph

        Returns:
            Optimized task graph
        """
        optimized = graph.clone()

        for pass_obj in self.passes:
            optimized = pass_obj.apply(optimized)

        total_changes = sum(p.changes_made for p in self.passes)
        logger.info(f"Optimization pipeline complete: {total_changes} total changes")

        return optimized

    def get_stats(self) -> List[Dict[str, any]]:
        """Get statistics from all passes"""
        return [p.get_stats() for p in self.passes]


def create_optimization_pipeline() -> OptimizationPipeline:
    """Factory function for OptimizationPipeline"""
    return OptimizationPipeline()
