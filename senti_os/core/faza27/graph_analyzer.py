"""
FAZA 27 – TaskGraph Engine
Graph Analyzer

Advanced graph analysis including cycle detection, bottleneck identification,
influence ranking, parallelization analysis, and health scoring.
"""

import logging
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict, deque

from senti_os.core.faza27.task_graph import TaskGraph
from senti_os.core.faza27.task_node import TaskNode, NodeStatus
from senti_os.core.faza27.task_edge import TaskEdge, EdgeType

logger = logging.getLogger(__name__)


class GraphAnalyzer:
    """
    Advanced graph analysis engine.

    Provides cycle detection, bottleneck identification, influence ranking,
    parallelization analysis, and comprehensive health scoring.
    """

    def __init__(self, graph: TaskGraph):
        """
        Initialize analyzer with graph.

        Args:
            graph: TaskGraph to analyze
        """
        self.graph = graph
        self._analysis_cache: Dict[str, Any] = {}

    # ==================== Cycle Analysis ====================

    def find_all_cycles(self) -> List[List[str]]:
        """
        Find all cycles in graph using DFS.

        Returns:
            List of cycles, each cycle is list of node IDs
        """
        if "cycles" in self._analysis_cache:
            return self._analysis_cache["cycles"]

        cycles = []
        visited = set()
        rec_stack = []
        rec_stack_set = set()

        def dfs(node_id: str) -> None:
            visited.add(node_id)
            rec_stack.append(node_id)
            rec_stack_set.add(node_id)

            for neighbor in self.graph._adj_list.get(node_id, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack_set:
                    # Found cycle - extract it from rec_stack
                    cycle_start_idx = rec_stack.index(neighbor)
                    cycle = rec_stack[cycle_start_idx:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.pop()
            rec_stack_set.remove(node_id)

        for node_id in self.graph.nodes:
            if node_id not in visited:
                dfs(node_id)

        self._analysis_cache["cycles"] = cycles
        logger.info(f"Found {len(cycles)} cycles in graph")
        return cycles

    def find_cycle_nodes(self) -> Set[str]:
        """
        Find all nodes involved in any cycle.

        Returns:
            Set of node IDs that participate in cycles
        """
        cycles = self.find_all_cycles()
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)
        return cycle_nodes

    # ==================== Bottleneck Detection ====================

    def find_bottlenecks(self, threshold: int = 3) -> List[Dict[str, Any]]:
        """
        Find bottleneck nodes (high fan-in or fan-out).

        Args:
            threshold: Minimum connections to be considered bottleneck

        Returns:
            List of bottleneck info dicts
        """
        bottlenecks = []

        for node in self.graph.get_all_nodes():
            fan_in = len(node.dependencies)
            fan_out = len(node.dependents)

            if fan_in >= threshold or fan_out >= threshold:
                bottlenecks.append({
                    "node_id": node.node_id,
                    "node_name": node.name,
                    "fan_in": fan_in,
                    "fan_out": fan_out,
                    "bottleneck_score": fan_in + fan_out,
                    "type": "convergence" if fan_in >= threshold else "divergence"
                })

        bottlenecks.sort(key=lambda x: x["bottleneck_score"], reverse=True)
        logger.info(f"Found {len(bottlenecks)} bottlenecks")
        return bottlenecks

    def find_critical_nodes(self) -> List[str]:
        """
        Find nodes on critical path.

        Returns:
            List of node IDs on critical path
        """
        critical_path, _ = self.graph.calculate_critical_path()
        return critical_path

    def calculate_node_criticality(self) -> Dict[str, float]:
        """
        Calculate criticality score for each node (0.0-1.0).

        Criticality is based on:
        - Position on critical path
        - Number of dependent nodes
        - Cost model weight

        Returns:
            Dict mapping node_id to criticality score
        """
        criticality = {}
        critical_nodes = set(self.find_critical_nodes())
        max_dependents = max(len(n.dependents) for n in self.graph.get_all_nodes()) or 1
        max_cost = max(n.cost_model.total_cost() for n in self.graph.get_all_nodes()) or 1.0

        for node in self.graph.get_all_nodes():
            score = 0.0

            # Critical path bonus (40%)
            if node.node_id in critical_nodes:
                score += 0.4

            # Dependent count factor (30%)
            score += 0.3 * (len(node.dependents) / max_dependents)

            # Cost factor (30%)
            score += 0.3 * (node.cost_model.total_cost() / max_cost)

            criticality[node.node_id] = min(score, 1.0)

        return criticality

    # ==================== Influence Ranking ====================

    def calculate_influence_scores(self, iterations: int = 20, damping: float = 0.85) -> Dict[str, float]:
        """
        Calculate influence scores using PageRank algorithm.

        Args:
            iterations: Number of PageRank iterations
            damping: Damping factor (0.0-1.0)

        Returns:
            Dict mapping node_id to influence score
        """
        if "influence" in self._analysis_cache:
            return self._analysis_cache["influence"]

        nodes = list(self.graph.nodes.keys())
        n = len(nodes)
        if n == 0:
            return {}

        # Initialize scores
        scores = {node_id: 1.0 / n for node_id in nodes}

        # Build reverse adjacency (who points to me)
        incoming: Dict[str, Set[str]] = defaultdict(set)
        outgoing_count: Dict[str, int] = defaultdict(int)

        for edge in self.graph.edges:
            incoming[edge.target_id].add(edge.source_id)
            outgoing_count[edge.source_id] += 1

        # PageRank iterations
        for _ in range(iterations):
            new_scores = {}
            for node_id in nodes:
                rank_sum = 0.0
                for source in incoming[node_id]:
                    if outgoing_count[source] > 0:
                        rank_sum += scores[source] / outgoing_count[source]

                new_scores[node_id] = (1 - damping) / n + damping * rank_sum

            scores = new_scores

        # Normalize to 0-1 range
        max_score = max(scores.values()) if scores else 1.0
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}

        # Update node objects
        for node_id, score in scores.items():
            self.graph.nodes[node_id].influence_score = score

        self._analysis_cache["influence"] = scores
        logger.info("Calculated influence scores for all nodes")
        return scores

    def find_most_influential_nodes(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Find most influential nodes.

        Args:
            top_n: Number of top nodes to return

        Returns:
            List of (node_id, influence_score) tuples
        """
        scores = self.calculate_influence_scores()
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_n]

    # ==================== Parallelization Analysis ====================

    def calculate_parallelization_index(self) -> float:
        """
        Calculate graph parallelization potential (0.0-1.0).

        Higher score means more parallel execution possible.

        Returns:
            Parallelization index
        """
        if len(self.graph.nodes) == 0:
            return 0.0

        levels = self.graph.calculate_node_levels()
        max_level = max(levels.values()) + 1 if levels else 1

        # Count nodes per level
        level_counts = defaultdict(int)
        for level in levels.values():
            level_counts[level] += 1

        # Calculate average parallelism per level
        avg_parallel = sum(level_counts.values()) / max_level if max_level > 0 else 0
        max_parallel = max(level_counts.values()) if level_counts else 1

        # Parallelization index
        index = avg_parallel / len(self.graph.nodes)

        return min(index, 1.0)

    def find_parallel_stages(self) -> Dict[int, List[str]]:
        """
        Find nodes that can execute in parallel (grouped by level).

        Returns:
            Dict mapping level to list of node IDs
        """
        levels = self.graph.calculate_node_levels()
        stages: Dict[int, List[str]] = defaultdict(list)

        for node_id, level in levels.items():
            stages[level].append(node_id)

        logger.info(f"Found {len(stages)} parallel stages")
        return dict(stages)

    def calculate_parallelization_factor(self) -> Dict[str, float]:
        """
        Calculate parallelization factor for each node.

        Factor indicates how many other nodes can run in parallel with this one.

        Returns:
            Dict mapping node_id to parallelization factor
        """
        stages = self.find_parallel_stages()
        factors = {}

        for level, node_ids in stages.items():
            # Factor is normalized by total nodes in this level
            factor = (len(node_ids) - 1) / len(self.graph.nodes) if len(self.graph.nodes) > 1 else 0.0
            for node_id in node_ids:
                factors[node_id] = factor
                self.graph.nodes[node_id].parallelization_factor = factor

        return factors

    # ==================== Health & Quality Analysis ====================

    def calculate_graph_health(self) -> Dict[str, Any]:
        """
        Calculate overall graph health score.

        Considers:
        - Cycle presence (bad)
        - Bottlenecks (moderate issue)
        - Parallelization (good)
        - Balance (good)

        Returns:
            Health report with score (0-100) and details
        """
        health_score = 100.0
        issues = []

        # Check for cycles (-50 points)
        cycles = self.find_all_cycles()
        if cycles:
            health_score -= 50.0
            issues.append(f"Contains {len(cycles)} cycles")

        # Check for bottlenecks (-10 points per bottleneck, max -30)
        bottlenecks = self.find_bottlenecks(threshold=5)
        if bottlenecks:
            penalty = min(len(bottlenecks) * 10, 30)
            health_score -= penalty
            issues.append(f"Contains {len(bottlenecks)} bottlenecks")

        # Check parallelization (bonus +0 to +20)
        parallel_index = self.calculate_parallelization_index()
        if parallel_index < 0.3:
            health_score -= 10.0
            issues.append("Low parallelization potential")

        # Check for isolated nodes (-5 points per isolated)
        isolated = [n for n in self.graph.get_all_nodes()
                   if len(n.dependencies) == 0 and len(n.dependents) == 0]
        if len(isolated) > 1:
            health_score -= min(len(isolated) * 5, 20)
            issues.append(f"Contains {len(isolated)} isolated nodes")

        health_score = max(health_score, 0.0)

        return {
            "health_score": health_score,
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy",
            "issues": issues,
            "parallelization_index": parallel_index,
            "cycle_count": len(cycles),
            "bottleneck_count": len(bottlenecks),
            "isolated_count": len(isolated)
        }

    def check_graph_quality(self) -> Dict[str, Any]:
        """
        Check graph quality metrics.

        Returns:
            Quality report with various metrics
        """
        nodes = self.graph.get_all_nodes()
        edges = self.graph.edges

        if not nodes:
            return {"error": "Empty graph"}

        # Calculate metrics
        avg_fan_in = sum(len(n.dependencies) for n in nodes) / len(nodes)
        avg_fan_out = sum(len(n.dependents) for n in nodes) / len(nodes)
        max_fan_in = max(len(n.dependencies) for n in nodes)
        max_fan_out = max(len(n.dependents) for n in nodes)

        # Check balance
        root_count = len(self.graph.get_root_nodes())
        leaf_count = len(self.graph.get_leaf_nodes())

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "avg_fan_in": round(avg_fan_in, 2),
            "avg_fan_out": round(avg_fan_out, 2),
            "max_fan_in": max_fan_in,
            "max_fan_out": max_fan_out,
            "root_count": root_count,
            "leaf_count": leaf_count,
            "is_balanced": abs(root_count - leaf_count) <= 2,
            "density": round(len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0, 3)
        }

    # ==================== Resource Analysis ====================

    def calculate_total_cost(self) -> Dict[str, float]:
        """
        Calculate total estimated resource costs.

        Returns:
            Dict with cost breakdown
        """
        total_duration = 0.0
        total_cost = 0.0
        total_cpu = 0.0
        total_memory = 0.0
        total_io = 0

        for node in self.graph.get_all_nodes():
            cm = node.cost_model
            total_duration += cm.estimated_duration
            total_cost += cm.estimated_cost
            total_cpu += cm.cpu_units
            total_memory += cm.memory_mb
            total_io += cm.io_operations

        # Calculate critical path duration
        _, critical_duration = self.graph.calculate_critical_path()

        return {
            "total_duration_sequential": round(total_duration, 2),
            "critical_path_duration": round(critical_duration, 2),
            "total_cost": round(total_cost, 2),
            "total_cpu_units": round(total_cpu, 2),
            "total_memory_mb": round(total_memory, 2),
            "total_io_operations": total_io,
            "efficiency_ratio": round(critical_duration / total_duration if total_duration > 0 else 0, 2)
        }

    def find_resource_hotspots(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Find nodes with highest resource usage.

        Args:
            top_n: Number of top nodes to return

        Returns:
            List of hotspot info dicts
        """
        hotspots = []

        for node in self.graph.get_all_nodes():
            cm = node.cost_model
            hotspots.append({
                "node_id": node.node_id,
                "node_name": node.name,
                "duration": cm.estimated_duration,
                "cost": cm.estimated_cost,
                "cpu_units": cm.cpu_units,
                "memory_mb": cm.memory_mb,
                "total_cost": cm.total_cost()
            })

        hotspots.sort(key=lambda x: x["total_cost"], reverse=True)
        return hotspots[:top_n]

    # ==================== Redundancy Analysis ====================

    def calculate_redundancy_score(self) -> float:
        """
        Calculate graph redundancy score (0.0-1.0).

        Higher score means more redundant paths (better fault tolerance).

        Returns:
            Redundancy score
        """
        if len(self.graph.nodes) < 2:
            return 0.0

        # Count alternative paths between root and leaf nodes
        roots = self.graph.get_root_nodes()
        leaves = self.graph.get_leaf_nodes()

        if not roots or not leaves:
            return 0.0

        total_paths = 0
        total_possible = len(roots) * len(leaves)

        for root in roots:
            for leaf in leaves:
                paths = self._count_paths(root.node_id, leaf.node_id)
                total_paths += paths

        # Redundancy is ratio of actual paths to possible paths
        redundancy = min(total_paths / (total_possible * 2), 1.0) if total_possible > 0 else 0.0

        return redundancy

    def _count_paths(self, start: str, end: str, visited: Optional[Set[str]] = None) -> int:
        """
        Count paths between two nodes using DFS.

        Args:
            start: Start node ID
            end: End node ID
            visited: Set of visited nodes

        Returns:
            Number of paths
        """
        if visited is None:
            visited = set()

        if start == end:
            return 1

        if start in visited:
            return 0

        visited.add(start)
        path_count = 0

        for neighbor in self.graph._adj_list.get(start, []):
            path_count += self._count_paths(neighbor, end, visited.copy())

        return path_count

    # ==================== Comprehensive Analysis ====================

    def get_analysis_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report.

        Returns:
            Complete analysis report
        """
        logger.info("Generating comprehensive analysis report")

        report = {
            "graph_id": self.graph.graph_id,
            "stats": self.graph.get_stats(),
            "health": self.calculate_graph_health(),
            "quality": self.check_graph_quality(),
            "costs": self.calculate_total_cost(),
            "bottlenecks": self.find_bottlenecks(),
            "critical_nodes": self.find_critical_nodes(),
            "influential_nodes": self.find_most_influential_nodes(),
            "resource_hotspots": self.find_resource_hotspots(),
            "parallel_stages": self.find_parallel_stages(),
            "parallelization_index": self.calculate_parallelization_index(),
            "redundancy_score": self.calculate_redundancy_score(),
            "cycles": self.find_all_cycles()
        }

        return report

    def clear_cache(self) -> None:
        """Clear analysis cache"""
        self._analysis_cache.clear()


def create_graph_analyzer(graph: TaskGraph) -> GraphAnalyzer:
    """
    Factory function to create GraphAnalyzer instance.

    Args:
        graph: TaskGraph to analyze

    Returns:
        GraphAnalyzer instance
    """
    return GraphAnalyzer(graph)
