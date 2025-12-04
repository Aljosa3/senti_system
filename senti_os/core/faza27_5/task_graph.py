"""
FAZA 27.5 - Execution Optimizer Layer
Mock TaskGraph Interface (Placeholder for FAZA 27)

This module provides a lightweight TaskGraph implementation
that will be replaced by FAZA 27 when it's implemented.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
from enum import Enum
import uuid


class TaskType(Enum):
    """Types of tasks in the graph"""
    COMPUTE = "compute"
    IO = "io"
    NETWORK = "network"
    MODEL = "model"
    DATA = "data"
    GENERIC = "generic"


@dataclass
class TaskNode:
    """
    Represents a single task node in the execution graph.

    This is a mock implementation that will be replaced by FAZA 27.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    task_type: TaskType = TaskType.GENERIC

    # Dependencies
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)

    # Execution metadata
    priority: int = 5
    estimated_duration: float = 1.0  # seconds
    estimated_cost: float = 0.0  # dollars

    # Resource requirements
    cpu_load: float = 0.5  # 0.0 to 1.0
    memory_mb: int = 100
    io_heavy: bool = False

    # Execution state
    executed: bool = False
    result: Any = None
    error: Optional[str] = None

    # Caching
    cacheable: bool = False
    cache_key: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)

    def can_execute(self, completed_nodes: Set[str]) -> bool:
        """Check if all dependencies are completed"""
        return self.dependencies.issubset(completed_nodes)


class TaskGraph:
    """
    Directed Acyclic Graph (DAG) of tasks.

    Mock implementation for FAZA 27 compatibility.
    Will be replaced by actual FAZA 27 TaskGraph.
    """

    def __init__(self, name: str = "TaskGraph"):
        """Initialize task graph"""
        self.name = name
        self.nodes: Dict[str, TaskNode] = {}
        self.root_nodes: Set[str] = set()
        self.leaf_nodes: Set[str] = set()

    def add_node(self, node: TaskNode) -> None:
        """Add a task node to the graph"""
        self.nodes[node.id] = node

        # Update root/leaf tracking
        if not node.dependencies:
            self.root_nodes.add(node.id)
        if not node.dependents:
            self.leaf_nodes.add(node.id)

    def add_edge(self, from_node_id: str, to_node_id: str) -> None:
        """Add a dependency edge from one node to another"""
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            raise ValueError("Both nodes must exist in graph")

        from_node = self.nodes[from_node_id]
        to_node = self.nodes[to_node_id]

        # Add dependency
        to_node.dependencies.add(from_node_id)
        from_node.dependents.add(to_node_id)

        # Update root/leaf tracking
        if to_node_id in self.root_nodes:
            self.root_nodes.remove(to_node_id)
        if from_node_id in self.leaf_nodes:
            self.leaf_nodes.remove(from_node_id)

    def get_node(self, node_id: str) -> Optional[TaskNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def get_ready_nodes(self, completed_nodes: Set[str]) -> List[TaskNode]:
        """Get nodes that are ready to execute"""
        ready = []
        for node in self.nodes.values():
            if not node.executed and node.can_execute(completed_nodes):
                ready.append(node)
        return ready

    def get_execution_order(self) -> List[List[str]]:
        """
        Get topological sort of nodes grouped by level.
        Returns list of lists where each sublist can be executed in parallel.
        """
        completed = set()
        levels = []

        while len(completed) < len(self.nodes):
            ready = [
                node.id for node in self.get_ready_nodes(completed)
            ]

            if not ready:
                # Check for cycles
                if len(completed) < len(self.nodes):
                    raise ValueError("Cycle detected in task graph")
                break

            levels.append(ready)
            completed.update(ready)

        return levels

    def get_critical_path(self) -> List[str]:
        """
        Get critical path (longest path by duration).
        Simple implementation for mock.
        """
        # Build levels
        levels = self.get_execution_order()

        # Find longest path (simplified)
        critical_path = []
        for level in levels:
            if level:
                # Pick node with longest duration in each level
                longest = max(
                    level,
                    key=lambda nid: self.nodes[nid].estimated_duration
                )
                critical_path.append(longest)

        return critical_path

    def clone(self) -> 'TaskGraph':
        """Create a deep copy of the graph"""
        import copy
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary"""
        return {
            "name": self.name,
            "nodes": {
                nid: {
                    "id": node.id,
                    "name": node.name,
                    "task_type": node.task_type.value,
                    "dependencies": list(node.dependencies),
                    "priority": node.priority,
                    "estimated_duration": node.estimated_duration,
                    "estimated_cost": node.estimated_cost,
                }
                for nid, node in self.nodes.items()
            }
        }

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return f"TaskGraph(name='{self.name}', nodes={len(self.nodes)})"


def create_sample_graph() -> TaskGraph:
    """Create a sample task graph for testing"""
    graph = TaskGraph("sample_graph")

    # Create nodes
    n1 = TaskNode(id="task1", name="Fetch Data", task_type=TaskType.IO, estimated_duration=2.0)
    n2 = TaskNode(id="task2", name="Process Data", task_type=TaskType.COMPUTE, estimated_duration=3.0)
    n3 = TaskNode(id="task3", name="Train Model", task_type=TaskType.MODEL, estimated_duration=10.0)
    n4 = TaskNode(id="task4", name="Evaluate", task_type=TaskType.COMPUTE, estimated_duration=1.0)

    # Add nodes
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)
    graph.add_node(n4)

    # Add dependencies: task1 -> task2 -> task3 -> task4
    graph.add_edge("task1", "task2")
    graph.add_edge("task2", "task3")
    graph.add_edge("task3", "task4")

    return graph
