"""
FAZA 26 - Intelligent Action Layer
Policy Engine

Enforces policies on task execution including priority rules,
resource limits, retry policies, and validation.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class RejectedTaskError(Exception):
    """Exception raised when a task is rejected by policy."""
    pass


class PolicyEngine:
    """
    Enforces execution policies on tasks.

    Policies include:
    - Priority enforcement and adjustment
    - Resource limit enforcement (max parallel heavy tasks)
    - Retry policy configuration
    - Task validation
    """

    # Policy configuration
    MAX_PARALLEL_HEAVY_TASKS = 2
    DEFAULT_RETRY_COUNT = 1
    MAX_PRIORITY = 10
    MIN_PRIORITY = 0

    # Heavy task types (resource-intensive operations)
    HEAVY_TASK_TYPES = [
        'computation',
        'inference',
        'model_io',
        'data_io'
    ]

    def __init__(self, max_parallel_heavy: int = MAX_PARALLEL_HEAVY_TASKS):
        """
        Initialize policy engine.

        Args:
            max_parallel_heavy: Maximum number of parallel heavy tasks (default: 2)
        """
        self.max_parallel_heavy = max_parallel_heavy
        self.current_heavy_tasks = 0
        logger.info(f"PolicyEngine initialized (max_parallel_heavy={max_parallel_heavy})")

    def apply_policies(self, task_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply policies to a list of tasks.

        Modifies tasks in place and returns the updated list.

        Policies applied:
        - Priority validation and normalization
        - Retry policy injection
        - Heavy task limiting
        - Metadata enrichment

        Args:
            task_list: List of task specifications

        Returns:
            Modified task list with policies applied

        Raises:
            RejectedTaskError: If tasks violate policies
        """
        if not task_list:
            return []

        modified_tasks = []
        heavy_task_count = 0

        for i, task in enumerate(task_list):
            # Validate task structure
            self._validate_task_structure(task)

            # Apply priority policy
            task = self._apply_priority_policy(task)

            # Check heavy task limit
            task_type = task.get("metadata", {}).get("task_type", "generic")
            is_heavy = task_type in self.HEAVY_TASK_TYPES

            if is_heavy:
                heavy_task_count += 1
                if heavy_task_count > self.max_parallel_heavy:
                    # Reduce priority for excess heavy tasks
                    original_priority = task["priority"]
                    task["priority"] = max(self.MIN_PRIORITY, original_priority - 3)
                    logger.warning(
                        f"Heavy task limit exceeded ({heavy_task_count}/{self.max_parallel_heavy}), "
                        f"reducing priority: {original_priority} -> {task['priority']}"
                    )

            # Apply retry policy
            task = self._apply_retry_policy(task)

            # Enrich metadata
            task = self._enrich_metadata(task, i)

            modified_tasks.append(task)

        logger.info(
            f"Applied policies to {len(modified_tasks)} tasks "
            f"({heavy_task_count} heavy tasks)"
        )

        return modified_tasks

    def validate_submission(self, task_spec: Dict[str, Any]) -> None:
        """
        Validate a single task before submission.

        Args:
            task_spec: Task specification

        Raises:
            RejectedTaskError: If task is rejected by policy
            ValueError: If task structure is invalid
        """
        # Validate structure
        self._validate_task_structure(task_spec)

        # Check priority bounds
        priority = task_spec.get("priority", 5)
        if priority < self.MIN_PRIORITY or priority > self.MAX_PRIORITY:
            raise RejectedTaskError(
                f"Priority {priority} outside allowed range "
                f"[{self.MIN_PRIORITY}, {self.MAX_PRIORITY}]"
            )

        # Check for required metadata
        metadata = task_spec.get("metadata", {})
        if not metadata:
            raise RejectedTaskError("Task must contain metadata")

        # Check heavy task quota
        task_type = metadata.get("task_type", "generic")
        if task_type in self.HEAVY_TASK_TYPES:
            if self.current_heavy_tasks >= self.max_parallel_heavy:
                raise RejectedTaskError(
                    f"Heavy task quota exceeded "
                    f"({self.current_heavy_tasks}/{self.max_parallel_heavy})"
                )

        logger.debug(f"Task validated: {task_spec.get('task', 'unknown')}")

    def _validate_task_structure(self, task: Dict[str, Any]) -> None:
        """
        Validate task structure.

        Args:
            task: Task specification

        Raises:
            ValueError: If structure is invalid
        """
        if not isinstance(task, dict):
            raise ValueError("Task must be a dictionary")

        if "task" not in task:
            raise ValueError("Task must contain 'task' field")

        if "priority" not in task:
            raise ValueError("Task must contain 'priority' field")

        if "metadata" not in task:
            raise ValueError("Task must contain 'metadata' field")

        if not isinstance(task["metadata"], dict):
            raise ValueError("Task metadata must be a dictionary")

    def _apply_priority_policy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply priority validation and normalization.

        Args:
            task: Task specification

        Returns:
            Task with normalized priority
        """
        priority = task.get("priority", 5)

        # Clamp priority to valid range
        if priority < self.MIN_PRIORITY:
            logger.warning(f"Priority {priority} too low, setting to {self.MIN_PRIORITY}")
            priority = self.MIN_PRIORITY
        elif priority > self.MAX_PRIORITY:
            logger.warning(f"Priority {priority} too high, setting to {self.MAX_PRIORITY}")
            priority = self.MAX_PRIORITY

        task["priority"] = priority
        return task

    def _apply_retry_policy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply retry policy to task.

        Args:
            task: Task specification

        Returns:
            Task with retry configuration
        """
        if "retry_count" not in task:
            task["retry_count"] = self.DEFAULT_RETRY_COUNT

        if "retry_on_error" not in task:
            # Enable retry for critical tasks (priority >= 8)
            task["retry_on_error"] = task["priority"] >= 8

        return task

    def _enrich_metadata(self, task: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Enrich task metadata with additional information.

        Args:
            task: Task specification
            index: Task index in the batch

        Returns:
            Task with enriched metadata
        """
        metadata = task.get("metadata", {})

        # Add batch index
        metadata["batch_index"] = index

        # Add policy version
        metadata["policy_version"] = "1.0"

        # Add heavy task indicator
        task_type = metadata.get("task_type", "generic")
        metadata["is_heavy_task"] = task_type in self.HEAVY_TASK_TYPES

        task["metadata"] = metadata
        return task

    def increment_heavy_task_count(self) -> None:
        """Increment the current heavy task counter."""
        self.current_heavy_tasks += 1
        logger.debug(f"Heavy task count: {self.current_heavy_tasks}/{self.max_parallel_heavy}")

    def decrement_heavy_task_count(self) -> None:
        """Decrement the current heavy task counter."""
        if self.current_heavy_tasks > 0:
            self.current_heavy_tasks -= 1
        logger.debug(f"Heavy task count: {self.current_heavy_tasks}/{self.max_parallel_heavy}")

    def get_policy_status(self) -> Dict[str, Any]:
        """
        Get current policy engine status.

        Returns:
            Dictionary with policy status information
        """
        return {
            "max_parallel_heavy": self.max_parallel_heavy,
            "current_heavy_tasks": self.current_heavy_tasks,
            "heavy_quota_available": self.max_parallel_heavy - self.current_heavy_tasks,
            "default_retry_count": self.DEFAULT_RETRY_COUNT,
            "priority_range": [self.MIN_PRIORITY, self.MAX_PRIORITY]
        }


def create_policy_engine(max_parallel_heavy: int = 2) -> PolicyEngine:
    """
    Factory function to create a PolicyEngine instance.

    Args:
        max_parallel_heavy: Maximum parallel heavy tasks (default: 2)

    Returns:
        PolicyEngine instance
    """
    return PolicyEngine(max_parallel_heavy=max_parallel_heavy)
