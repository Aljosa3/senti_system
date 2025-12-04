"""
FAZA 27 – TaskGraph Engine
Task Node

Represents a single task node in the execution graph.
Contains metadata, cost models, status tracking, and serialization.
"""

import json
from enum import Enum
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


class NodeStatus(Enum):
    """Task node execution status"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


@dataclass
class CostModel:
    """
    Cost model for task execution.

    Attributes:
        estimated_duration: Estimated execution time (seconds)
        estimated_cost: Estimated monetary cost
        cpu_units: CPU resource units required
        memory_mb: Memory required (MB)
        io_operations: Estimated I/O operations
        network_bandwidth: Network bandwidth required (Mbps)
    """
    estimated_duration: float = 1.0
    estimated_cost: float = 0.0
    cpu_units: float = 1.0
    memory_mb: float = 128.0
    io_operations: int = 0
    network_bandwidth: float = 0.0

    def total_cost(self) -> float:
        """Calculate total cost considering all factors"""
        return self.estimated_cost + (self.estimated_duration * 0.01)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "estimated_duration": self.estimated_duration,
            "estimated_cost": self.estimated_cost,
            "cpu_units": self.cpu_units,
            "memory_mb": self.memory_mb,
            "io_operations": self.io_operations,
            "network_bandwidth": self.network_bandwidth
        }


class TaskNode:
    """
    Task node in execution graph.

    Represents a single executable task with metadata, dependencies,
    cost estimation, and execution tracking.
    """

    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: str = "generic",
        priority: int = 5,
        cost_model: Optional[CostModel] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize task node.

        Args:
            node_id: Unique node identifier
            name: Human-readable task name
            node_type: Type of task (generic, compute, io, network, etc.)
            priority: Execution priority (0-10, higher = more important)
            cost_model: Cost estimation model
            metadata: Additional task metadata
        """
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.priority = priority
        self.status = NodeStatus.PENDING

        self.cost_model = cost_model or CostModel()
        self.metadata = metadata or {}

        # Dependencies (filled by TaskGraph)
        self.dependencies: Set[str] = set()  # Incoming edges (predecessors)
        self.dependents: Set[str] = set()    # Outgoing edges (successors)

        # Execution tracking
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.actual_duration: Optional[float] = None
        self.error_message: Optional[str] = None

        # Graph analysis results (computed by analyzer)
        self.level: Optional[int] = None              # Topological level
        self.critical_path: bool = False              # On critical path
        self.influence_score: float = 0.0             # PageRank-like score
        self.parallelization_factor: float = 1.0      # Parallel execution potential

    def mark_ready(self) -> None:
        """Mark node as ready for execution"""
        self.status = NodeStatus.READY

    def mark_running(self) -> None:
        """Mark node as currently executing"""
        self.status = NodeStatus.RUNNING
        self.start_time = datetime.now()

    def mark_completed(self, actual_duration: Optional[float] = None) -> None:
        """Mark node as successfully completed"""
        self.status = NodeStatus.COMPLETED
        self.end_time = datetime.now()
        if actual_duration is not None:
            self.actual_duration = actual_duration
        elif self.start_time:
            self.actual_duration = (self.end_time - self.start_time).total_seconds()

    def mark_failed(self, error_message: str) -> None:
        """Mark node as failed"""
        self.status = NodeStatus.FAILED
        self.end_time = datetime.now()
        self.error_message = error_message
        if self.start_time:
            self.actual_duration = (self.end_time - self.start_time).total_seconds()

    def mark_cancelled(self) -> None:
        """Mark node as cancelled"""
        self.status = NodeStatus.CANCELLED

    def mark_blocked(self) -> None:
        """Mark node as blocked (dependencies not met)"""
        self.status = NodeStatus.BLOCKED

    def is_terminal(self) -> bool:
        """Check if node is in terminal state"""
        return self.status in [NodeStatus.COMPLETED, NodeStatus.FAILED, NodeStatus.CANCELLED]

    def can_execute(self) -> bool:
        """Check if node can be executed (all dependencies met)"""
        return self.status == NodeStatus.READY

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value"""
        self.metadata[key] = value

    def update_metadata(self, updates: Dict[str, Any]) -> None:
        """Update multiple metadata values"""
        self.metadata.update(updates)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize node to dictionary.

        Returns:
            Dictionary representation of node
        """
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type,
            "priority": self.priority,
            "status": self.status.value,
            "cost_model": self.cost_model.to_dict(),
            "metadata": self.metadata,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "level": self.level,
            "critical_path": self.critical_path,
            "influence_score": self.influence_score,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "actual_duration": self.actual_duration,
            "error_message": self.error_message
        }

    def to_json(self) -> str:
        """Serialize node to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskNode":
        """
        Deserialize node from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            TaskNode instance
        """
        cost_data = data.get("cost_model", {})
        cost_model = CostModel(
            estimated_duration=cost_data.get("estimated_duration", 1.0),
            estimated_cost=cost_data.get("estimated_cost", 0.0),
            cpu_units=cost_data.get("cpu_units", 1.0),
            memory_mb=cost_data.get("memory_mb", 128.0),
            io_operations=cost_data.get("io_operations", 0),
            network_bandwidth=cost_data.get("network_bandwidth", 0.0)
        )

        node = cls(
            node_id=data["node_id"],
            name=data["name"],
            node_type=data.get("node_type", "generic"),
            priority=data.get("priority", 5),
            cost_model=cost_model,
            metadata=data.get("metadata", {})
        )

        node.status = NodeStatus(data.get("status", "pending"))
        node.dependencies = set(data.get("dependencies", []))
        node.dependents = set(data.get("dependents", []))
        node.level = data.get("level")
        node.critical_path = data.get("critical_path", False)
        node.influence_score = data.get("influence_score", 0.0)

        return node

    def __repr__(self) -> str:
        return f"<TaskNode: {self.node_id} ({self.status.value})>"

    def __str__(self) -> str:
        return f"{self.name} [{self.node_id}]"
