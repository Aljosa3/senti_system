"""
FAZA 27.5 - Execution Optimizer Layer
Optimizer Manager

Main orchestrator for the complete optimization pipeline:
1. Validate graph
2. Apply optimization passes
3. Generate report
4. Export to FAZA 25

Provides clean API for FAZA 26 and FAZA 28 integration.
"""

import logging
from typing import Dict, Any, Optional

from senti_os.core.faza27_5.task_graph import TaskGraph
from senti_os.core.faza27_5.graph_validator import GraphValidator, ValidationError
from senti_os.core.faza27_5.optimization_passes import OptimizationPipeline
from senti_os.core.faza27_5.optimization_report import OptimizationReport, ReportBuilder

logger = logging.getLogger(__name__)


class OptimizerManager:
    """
    Main manager for task graph optimization.

    Orchestrates the complete optimization pipeline:
    - Graph validation
    - Optimization pass application
    - Report generation
    - FAZA 25 export preparation
    """

    def __init__(self, skip_validation: bool = False):
        """
        Initialize optimizer manager.

        Args:
            skip_validation: Skip validation step (use with caution)
        """
        self.validator = GraphValidator()
        self.pipeline = OptimizationPipeline()
        self.skip_validation = skip_validation

        self._warn_mock_mode()

        logger.info("OptimizerManager initialized")

    def optimize(self, graph: TaskGraph) -> tuple[TaskGraph, OptimizationReport]:
        """
        Optimize a task graph.

        Complete pipeline:
        1. Validate graph structure
        2. Apply optimization passes
        3. Generate optimization report
        4. Return optimized graph + report

        Args:
            graph: Input task graph

        Returns:
            Tuple of (optimized_graph, report)

        Raises:
            ValidationError: If graph validation fails
        """
        logger.info(f"Starting optimization for graph: {graph.name}")

        # Step 1: Validation
        if not self.skip_validation:
            validation_result = self.validator.validate(graph)
            if not validation_result["valid"]:
                errors = validation_result["errors"]
                raise ValidationError(f"Graph validation failed: {errors}")

            if validation_result["warnings"]:
                logger.warning(f"Graph validation warnings: {validation_result['warnings']}")
        else:
            logger.warning("Skipping validation (not recommended)")

        # Step 2: Collect before statistics
        before_stats = self._collect_stats(graph)

        # Step 3: Apply optimization passes
        optimized_graph = self.pipeline.apply_all(graph)

        # Step 4: Collect after statistics
        after_stats = self._collect_stats(optimized_graph)

        # Step 5: Generate report
        report = self._generate_report(
            graph_name=graph.name,
            before_stats=before_stats,
            after_stats=after_stats,
            pass_stats=self.pipeline.get_stats()
        )

        logger.info(f"Optimization complete: {report.format_summary()}")

        return optimized_graph, report

    def validate_only(self, graph: TaskGraph) -> Dict[str, Any]:
        """
        Only validate graph without optimization.

        Args:
            graph: Task graph to validate

        Returns:
            Validation result dictionary
        """
        return self.validator.validate(graph)

    def quick_optimize(self, graph: TaskGraph) -> TaskGraph:
        """
        Quick optimization without detailed report.

        Args:
            graph: Input task graph

        Returns:
            Optimized task graph
        """
        optimized, _ = self.optimize(graph)
        return optimized

    def export_to_faza25(
        self,
        graph: TaskGraph,
        orchestrator=None
    ) -> list:
        """
        Export optimized graph to FAZA 25 orchestrator.

        Converts TaskGraph nodes to FAZA 25 task submissions.
        Note: This is a mock implementation until FAZA 27 provides
        proper TaskGraph-to-FAZA25 conversion.

        Args:
            graph: Optimized task graph
            orchestrator: FAZA 25 orchestrator instance (optional)

        Returns:
            List of task IDs (if orchestrator provided) or task specs
        """
        logger.info(f"Exporting {len(graph)} nodes to FAZA 25 format")

        task_specs = []
        execution_order = graph.get_execution_order()

        # Convert to FAZA 25 compatible format
        for level in execution_order:
            for node_id in level:
                node = graph.nodes[node_id]

                spec = {
                    "name": node.name,
                    "priority": node.priority,
                    "task_type": node.task_type.value,
                    "metadata": {
                        **node.metadata,
                        "graph_node_id": node_id,
                        "estimated_duration": node.estimated_duration,
                        "estimated_cost": node.estimated_cost,
                    }
                }

                task_specs.append(spec)

        if orchestrator:
            # If orchestrator provided, submit tasks
            logger.warning("Direct FAZA 25 submission requires custom executor mapping")
            # This would need proper integration with FAZA 25
            return []

        return task_specs

    def _collect_stats(self, graph: TaskGraph) -> Dict[str, Any]:
        """Collect graph statistics"""
        total_time = sum(node.estimated_duration for node in graph.nodes.values())
        total_cost = sum(node.estimated_cost for node in graph.nodes.values())
        total_edges = sum(len(node.dependencies) for node in graph.nodes.values())

        # Count special node types
        redundant_count = sum(
            1 for node in graph.nodes.values()
            if node.metadata.get("redundant", False)
        )

        batched_count = sum(
            1 for node in graph.nodes.values()
            if node.metadata.get("batchable", False)
        )

        skippable_count = sum(
            1 for node in graph.nodes.values()
            if node.metadata.get("can_skip", False)
        )

        # Parallelization score (simplified)
        levels = graph.get_execution_order()
        if levels:
            avg_parallel = sum(len(level) for level in levels) / len(levels)
            parallel_score = avg_parallel / len(graph) if len(graph) > 0 else 0.0
        else:
            parallel_score = 0.0

        return {
            "nodes": len(graph),
            "edges": total_edges,
            "estimated_time": total_time,
            "estimated_cost": total_cost,
            "redundant_count": redundant_count,
            "batched_count": batched_count,
            "skippable_count": skippable_count,
            "parallelization_score": parallel_score
        }

    def _generate_report(
        self,
        graph_name: str,
        before_stats: Dict[str, Any],
        after_stats: Dict[str, Any],
        pass_stats: list
    ) -> OptimizationReport:
        """Generate optimization report"""
        builder = ReportBuilder()

        builder.set_graph_name(graph_name)
        builder.set_before_stats(before_stats["nodes"], before_stats["edges"])
        builder.set_after_stats(after_stats["nodes"], after_stats["edges"])

        # Add optimization names
        for stat in pass_stats:
            if stat["changes"] > 0:
                builder.add_optimization(stat["pass_name"])

        # Set counts
        builder.set_redundancies(before_stats["nodes"] - after_stats["nodes"])
        builder.set_batched(after_stats["batched_count"])
        builder.set_skippable(after_stats["skippable_count"])

        # Set performance estimates
        builder.set_time_estimates(
            before_stats["estimated_time"],
            after_stats["estimated_time"]
        )
        builder.set_cost_estimates(
            before_stats["estimated_cost"],
            after_stats["estimated_cost"]
        )
        builder.set_parallelization_scores(
            before_stats["parallelization_score"],
            after_stats["parallelization_score"]
        )

        # Add pass statistics
        builder.set_pass_stats(pass_stats)

        # Add mock mode warning
        builder.add_note(
            "Using mock TaskGraph (FAZA 27 not yet implemented). "
            "Real performance gains will vary."
        )

        return builder.build()

    def _warn_mock_mode(self):
        """Warn about mock TaskGraph mode"""
        logger.warning(
            "FAZA 27.5 is running in MOCK mode. "
            "Using placeholder TaskGraph until FAZA 27 is implemented. "
            "Optimization results are simulated."
        )


def create_optimizer_manager(skip_validation: bool = False) -> OptimizerManager:
    """
    Factory function for OptimizerManager.

    Args:
        skip_validation: Skip validation step (not recommended)

    Returns:
        OptimizerManager instance
    """
    return OptimizerManager(skip_validation=skip_validation)


# Global instance (singleton)
_optimizer_instance: Optional[OptimizerManager] = None


def get_optimizer() -> OptimizerManager:
    """
    Get global optimizer instance (singleton).

    Returns:
        OptimizerManager instance
    """
    global _optimizer_instance

    if _optimizer_instance is None:
        _optimizer_instance = OptimizerManager()

    return _optimizer_instance
