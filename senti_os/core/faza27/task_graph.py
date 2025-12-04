"""
FAZA 27 – TaskGraph Engine
Task Graph

Main graph structure with nodes, edges, and graph operations.
Provides DAG validation, topological sorting, and critical path analysis.
"""

import json
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import deque, defaultdict

from senti_os.core.faza27.task_node import TaskNode, NodeStatus
from senti_os.core.faza27.task_edge import TaskEdge, EdgeType


class TaskGraph:
    """
    Task execution graph (DAG).

    Manages task nodes and their dependencies, provides graph analysis,
    validation, and execution planning capabilities.
    """

    def __init__(self, graph_id: str = "default", metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize task graph.

        Args:
            graph_id: Unique graph identifier
            metadata: Additional graph metadata
        """
        self.graph_id = graph_id
        self.metadata = metadata or {}

        # Graph data structures
        self.nodes: Dict[str, TaskNode] = {}
        self.edges: List[TaskEdge] = []

        # Adjacency lists (updated on edge add/remove)
        self._adj_list: Dict[str, Set[str]] = defaultdict(set)  # node_id -> dependents
        self._rev_adj_list: Dict[str, Set[str]] = defaultdict(set)  # node_id -> dependencies

        # Cached analysis results
        self._topological_order: Optional[List[str]] = None
        self._critical_path: Optional[List[str]] = None
        self._is_validated: bool = False

    # ==================== Node Operations ====================

    def add_node(self, node: TaskNode) -> None:
        """
        Add node to graph.

        Args:
            node: TaskNode to add

        Raises:
            ValueError: If node with same ID already exists
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists in graph")

        self.nodes[node.node_id] = node
        self._invalidate_cache()

    def remove_node(self, node_id: str) -> None:
        """
        Remove node from graph.

        Args:
            node_id: Node identifier

        Raises:
            KeyError: If node doesn't exist
        """
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} not found in graph")

        # Remove all edges connected to this node
        self.edges = [e for e in self.edges if e.source_id != node_id and e.target_id != node_id]

        # Remove from adjacency lists (use pop to avoid KeyError)
        self._adj_list.pop(node_id, None)
        self._rev_adj_list.pop(node_id, None)

        for deps in self._adj_list.values():
            deps.discard(node_id)
        for deps in self._rev_adj_list.values():
            deps.discard(node_id)

        # Remove node
        del self.nodes[node_id]
        self._invalidate_cache()

    def get_node(self, node_id: str) -> TaskNode:
        """Get node by ID"""
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} not found")
        return self.nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        """Check if node exists"""
        return node_id in self.nodes

    def get_all_nodes(self) -> List[TaskNode]:
        """Get all nodes in graph"""
        return list(self.nodes.values())

    # ==================== Edge Operations ====================

    def add_edge(self, edge: TaskEdge) -> None:
        """
        Add edge to graph.

        Args:
            edge: TaskEdge to add

        Raises:
            ValueError: If source or target node doesn't exist
            ValueError: If edge creates cycle
        """
        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} not found")
        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} not found")

        # Check for self-loop
        if edge.source_id == edge.target_id:
            raise ValueError("Self-loops not allowed in DAG")

        # Add to edge list
        self.edges.append(edge)

        # Update adjacency lists
        self._adj_list[edge.source_id].add(edge.target_id)
        self._rev_adj_list[edge.target_id].add(edge.source_id)

        # Update node dependencies
        self.nodes[edge.source_id].dependents.add(edge.target_id)
        self.nodes[edge.target_id].dependencies.add(edge.source_id)

        # Check for cycles (strong dependencies only)
        if edge.edge_type in [EdgeType.DEPENDENCY, EdgeType.CONSTRAINT]:
            if self.has_cycle():
                # Rollback edge addition
                self.edges.pop()
                self._adj_list[edge.source_id].remove(edge.target_id)
                self._rev_adj_list[edge.target_id].remove(edge.source_id)
                self.nodes[edge.source_id].dependents.remove(edge.target_id)
                self.nodes[edge.target_id].dependencies.remove(edge.source_id)
                raise ValueError(f"Adding edge {edge.source_id} -> {edge.target_id} creates cycle")

        self._invalidate_cache()

    def remove_edge(self, source_id: str, target_id: str) -> None:
        """
        Remove edge from graph.

        Args:
            source_id: Source node ID
            target_id: Target node ID
        """
        # Remove from edge list
        self.edges = [e for e in self.edges if not (e.source_id == source_id and e.target_id == target_id)]

        # Update adjacency lists
        self._adj_list[source_id].discard(target_id)
        self._rev_adj_list[target_id].discard(source_id)

        # Update node dependencies
        if source_id in self.nodes:
            self.nodes[source_id].dependents.discard(target_id)
        if target_id in self.nodes:
            self.nodes[target_id].dependencies.discard(source_id)

        self._invalidate_cache()

    def get_edges_from(self, node_id: str) -> List[TaskEdge]:
        """Get all edges starting from node"""
        return [e for e in self.edges if e.source_id == node_id]

    def get_edges_to(self, node_id: str) -> List[TaskEdge]:
        """Get all edges ending at node"""
        return [e for e in self.edges if e.target_id == node_id]

    def has_edge(self, source_id: str, target_id: str) -> bool:
        """Check if edge exists"""
        return any(e.source_id == source_id and e.target_id == target_id for e in self.edges)

    # ==================== Graph Analysis ====================

    def has_cycle(self) -> bool:
        """
        Check if graph contains cycle using DFS.

        Returns:
            True if cycle detected, False otherwise
        """
        visited = set()
        rec_stack = set()

        def dfs_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in self._adj_list.get(node_id, []):
                if neighbor not in visited:
                    if dfs_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if dfs_cycle(node_id):
                    return True

        return False

    def is_acyclic(self) -> bool:
        """Check if graph is acyclic (DAG)"""
        return not self.has_cycle()

    def topological_sort(self) -> List[str]:
        """
        Perform topological sort using Kahn's algorithm.

        Returns:
            List of node IDs in topological order

        Raises:
            ValueError: If graph contains cycle
        """
        if self._topological_order is not None:
            return self._topological_order

        # Calculate in-degree for each node
        in_degree = {node_id: len(self._rev_adj_list.get(node_id, set())) for node_id in self.nodes}

        # Queue of nodes with in-degree 0
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            node_id = queue.popleft()
            result.append(node_id)

            # Reduce in-degree of neighbors
            for neighbor in self._adj_list.get(node_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.nodes):
            raise ValueError("Graph contains cycle, cannot perform topological sort")

        self._topological_order = result
        return result

    def get_root_nodes(self) -> List[TaskNode]:
        """Get nodes with no dependencies (entry points)"""
        return [node for node in self.nodes.values() if len(node.dependencies) == 0]

    def get_leaf_nodes(self) -> List[TaskNode]:
        """Get nodes with no dependents (exit points)"""
        return [node for node in self.nodes.values() if len(node.dependents) == 0]

    def calculate_node_levels(self) -> Dict[str, int]:
        """
        Calculate topological level for each node.

        Returns:
            Dict mapping node_id to level (0 = root level)
        """
        topo_order = self.topological_sort()
        levels = {}

        for node_id in topo_order:
            # Level is max(level of all dependencies) + 1
            deps = self._rev_adj_list.get(node_id, set())
            if not deps:
                levels[node_id] = 0
            else:
                levels[node_id] = max(levels[dep] for dep in deps) + 1

            # Update node level
            self.nodes[node_id].level = levels[node_id]

        return levels

    def calculate_critical_path(self) -> Tuple[List[str], float]:
        """
        Calculate critical path (longest path) through graph.

        Returns:
            Tuple of (node_ids in critical path, total duration)
        """
        if self._critical_path is not None:
            total_duration = sum(self.nodes[nid].cost_model.estimated_duration for nid in self._critical_path)
            return self._critical_path, total_duration

        topo_order = self.topological_sort()

        # Calculate earliest start time for each node
        earliest_start = {}
        predecessor = {}

        for node_id in topo_order:
            deps = self._rev_adj_list.get(node_id, set())
            if not deps:
                earliest_start[node_id] = 0
                predecessor[node_id] = None
            else:
                max_time = 0
                max_pred = None
                for dep in deps:
                    finish_time = earliest_start[dep] + self.nodes[dep].cost_model.estimated_duration
                    if finish_time > max_time:
                        max_time = finish_time
                        max_pred = dep
                earliest_start[node_id] = max_time
                predecessor[node_id] = max_pred

        # Find node with maximum finish time
        max_finish = 0
        end_node = None
        for node_id in self.nodes:
            finish_time = earliest_start[node_id] + self.nodes[node_id].cost_model.estimated_duration
            if finish_time > max_finish:
                max_finish = finish_time
                end_node = node_id

        # Backtrack to build critical path
        path = []
        current = end_node
        while current is not None:
            path.append(current)
            self.nodes[current].critical_path = True
            current = predecessor.get(current)

        path.reverse()
        self._critical_path = path

        return path, max_finish

    # ==================== Graph Validation ====================

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate graph consistency.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check for cycles
        if self.has_cycle():
            errors.append("Graph contains cycles")

        # Check edge consistency
        for edge in self.edges:
            if edge.source_id not in self.nodes:
                errors.append(f"Edge references non-existent source node: {edge.source_id}")
            if edge.target_id not in self.nodes:
                errors.append(f"Edge references non-existent target node: {edge.target_id}")

        # Check node dependency consistency
        for node in self.nodes.values():
            for dep_id in node.dependencies:
                if dep_id not in self.nodes:
                    errors.append(f"Node {node.node_id} references non-existent dependency: {dep_id}")

        self._is_validated = len(errors) == 0
        return self._is_validated, errors

    # ==================== Serialization ====================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize graph to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "graph_id": self.graph_id,
            "metadata": self.metadata,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges],
            "node_count": len(self.nodes),
            "edge_count": len(self.edges)
        }

    def to_json(self) -> str:
        """Serialize graph to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskGraph":
        """
        Deserialize graph from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            TaskGraph instance
        """
        graph = cls(
            graph_id=data.get("graph_id", "default"),
            metadata=data.get("metadata", {})
        )

        # Add nodes
        for node_data in data.get("nodes", {}).values():
            node = TaskNode.from_dict(node_data)
            graph.nodes[node.node_id] = node

        # Add edges
        for edge_data in data.get("edges", []):
            edge = TaskEdge.from_dict(edge_data)
            # Manually add without cycle check (already validated)
            graph.edges.append(edge)
            graph._adj_list[edge.source_id].add(edge.target_id)
            graph._rev_adj_list[edge.target_id].add(edge.source_id)

        return graph

    # ==================== Utility ====================

    def _invalidate_cache(self) -> None:
        """Invalidate cached analysis results"""
        self._topological_order = None
        self._critical_path = None
        self._is_validated = False

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            "graph_id": self.graph_id,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "root_count": len(self.get_root_nodes()),
            "leaf_count": len(self.get_leaf_nodes()),
            "is_acyclic": self.is_acyclic()
        }

    def __repr__(self) -> str:
        return f"<TaskGraph: {self.graph_id} ({len(self.nodes)} nodes, {len(self.edges)} edges)>"

    def __str__(self) -> str:
        return f"TaskGraph[{self.graph_id}]: {len(self.nodes)} nodes, {len(self.edges)} edges"
