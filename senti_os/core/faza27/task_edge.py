"""
FAZA 27 – TaskGraph Engine
Task Edge

Represents edges (dependencies/constraints) between task nodes in the graph.
"""

import json
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class EdgeType(Enum):
    """Edge type enumeration"""
    DEPENDENCY = "dependency"        # Standard dependency (A must complete before B)
    CONSTRAINT = "constraint"        # Timing or resource constraint
    DATA_FLOW = "data_flow"         # Data flows from A to B
    CONDITIONAL = "conditional"      # Conditional dependency
    WEAK = "weak"                   # Weak dependency (preferred but not required)


class TaskEdge:
    """
    Edge in task graph representing dependency or constraint between nodes.

    Represents relationships between task nodes including dependencies,
    data flow, constraints, and conditional relationships.
    """

    def __init__(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType = EdgeType.DEPENDENCY,
        weight: float = 1.0,
        constraints: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize task edge.

        Args:
            source_id: Source node identifier
            target_id: Target node identifier
            edge_type: Type of edge relationship
            weight: Edge weight (for weighted algorithms)
            constraints: Constraint specifications
            metadata: Additional edge metadata
        """
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.weight = weight
        self.constraints = constraints or {}
        self.metadata = metadata or {}

    def is_dependency(self) -> bool:
        """Check if edge is a standard dependency"""
        return self.edge_type == EdgeType.DEPENDENCY

    def is_conditional(self) -> bool:
        """Check if edge is conditional"""
        return self.edge_type == EdgeType.CONDITIONAL

    def is_weak(self) -> bool:
        """Check if edge is weak dependency"""
        return self.edge_type == EdgeType.WEAK

    def get_constraint(self, key: str, default: Any = None) -> Any:
        """Get constraint value"""
        return self.constraints.get(key, default)

    def set_constraint(self, key: str, value: Any) -> None:
        """Set constraint value"""
        self.constraints[key] = value

    def has_timing_constraint(self) -> bool:
        """Check if edge has timing constraints"""
        return "max_delay" in self.constraints or "min_delay" in self.constraints

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize edge to dictionary.

        Returns:
            Dictionary representation of edge
        """
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
            "constraints": self.constraints,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Serialize edge to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskEdge":
        """
        Deserialize edge from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            TaskEdge instance
        """
        edge = cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=EdgeType(data.get("edge_type", "dependency")),
            weight=data.get("weight", 1.0),
            constraints=data.get("constraints", {}),
            metadata=data.get("metadata", {})
        )
        return edge

    def __repr__(self) -> str:
        return f"<TaskEdge: {self.source_id} -> {self.target_id} ({self.edge_type.value})>"

    def __str__(self) -> str:
        return f"{self.source_id} -> {self.target_id}"
