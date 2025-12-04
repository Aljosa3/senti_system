"""
FAZA 27 – TaskGraph Engine
Graph Monitor

Integrates with FAZA 28 (Agent Execution Loop) and FAZA 28.5 (Meta-Layer)
for live graph monitoring and status tracking.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from senti_os.core.faza27.task_graph import TaskGraph
from senti_os.core.faza27.task_node import TaskNode, NodeStatus
from senti_os.core.faza27.graph_analyzer import GraphAnalyzer

logger = logging.getLogger(__name__)


class GraphMonitor:
    """
    Live TaskGraph monitor with FAZA 28/28.5 integration.

    Tracks graph execution, syncs with agent states, and provides
    real-time metrics and health monitoring.
    """

    def __init__(self, graph: TaskGraph):
        """
        Initialize graph monitor.

        Args:
            graph: TaskGraph to monitor
        """
        self.graph = graph
        self.analyzer = GraphAnalyzer(graph)

        # FAZA 28 integration
        self.event_bus: Optional[Any] = None
        self.agent_callbacks: Dict[str, Callable] = {}

        # Execution tracking
        self.execution_start_time: Optional[datetime] = None
        self.execution_end_time: Optional[datetime] = None
        self.node_events: list[Dict[str, Any]] = []

        # Statistics
        self.stats = {
            "nodes_completed": 0,
            "nodes_failed": 0,
            "nodes_running": 0,
            "total_duration": 0.0
        }

    # ==================== FAZA 28 Integration ====================

    def attach_to_event_bus(self, event_bus: Any) -> None:
        """
        Attach monitor to FAZA 28 EventBus.

        Args:
            event_bus: FAZA 28 EventBus instance
        """
        self.event_bus = event_bus

        # Subscribe to relevant events
        self.event_bus.subscribe("agent.started", "graph_monitor", self._on_agent_started)
        self.event_bus.subscribe("agent.completed", "graph_monitor", self._on_agent_completed)
        self.event_bus.subscribe("agent.failed", "graph_monitor", self._on_agent_failed)

        logger.info("GraphMonitor attached to FAZA 28 EventBus")

    def detach_from_event_bus(self) -> None:
        """Detach monitor from EventBus"""
        if self.event_bus:
            self.event_bus.unsubscribe("agent.started", "graph_monitor")
            self.event_bus.unsubscribe("agent.completed", "graph_monitor")
            self.event_bus.unsubscribe("agent.failed", "graph_monitor")
            self.event_bus = None
            logger.info("GraphMonitor detached from EventBus")

    def _on_agent_started(self, event: Any) -> None:
        """Handle agent started event"""
        agent_name = event.data.get("agent_name")
        if agent_name and self.graph.has_node(agent_name):
            self.on_node_start(agent_name)

    def _on_agent_completed(self, event: Any) -> None:
        """Handle agent completed event"""
        agent_name = event.data.get("agent_name")
        duration = event.data.get("duration", 0.0)
        if agent_name and self.graph.has_node(agent_name):
            self.on_node_complete(agent_name, duration)

    def _on_agent_failed(self, event: Any) -> None:
        """Handle agent failed event"""
        agent_name = event.data.get("agent_name")
        error = event.data.get("error", "Unknown error")
        if agent_name and self.graph.has_node(agent_name):
            self.on_node_fail(agent_name, error)

    # ==================== Node Status Updates ====================

    def on_node_start(self, node_id: str) -> None:
        """
        Handle node execution start.

        Args:
            node_id: Node identifier
        """
        if not self.graph.has_node(node_id):
            logger.warning(f"Node {node_id} not found in graph")
            return

        node = self.graph.get_node(node_id)
        node.mark_running()

        self.stats["nodes_running"] += 1

        self.node_events.append({
            "node_id": node_id,
            "event": "started",
            "timestamp": datetime.now().isoformat()
        })

        # Publish event
        if self.event_bus:
            self.event_bus.publish({
                "type": "graph.node.started",
                "source": "graph_monitor",
                "data": {
                    "graph_id": self.graph.graph_id,
                    "node_id": node_id,
                    "node_name": node.name
                }
            })

        logger.info(f"Node {node_id} started")

    def on_node_complete(self, node_id: str, duration: Optional[float] = None) -> None:
        """
        Handle node execution completion.

        Args:
            node_id: Node identifier
            duration: Actual execution duration
        """
        if not self.graph.has_node(node_id):
            logger.warning(f"Node {node_id} not found in graph")
            return

        node = self.graph.get_node(node_id)
        node.mark_completed(duration)

        self.stats["nodes_completed"] += 1
        self.stats["nodes_running"] -= 1
        if duration:
            self.stats["total_duration"] += duration

        self.node_events.append({
            "node_id": node_id,
            "event": "completed",
            "timestamp": datetime.now().isoformat(),
            "duration": duration
        })

        # Publish event
        if self.event_bus:
            self.event_bus.publish({
                "type": "graph.node.completed",
                "source": "graph_monitor",
                "data": {
                    "graph_id": self.graph.graph_id,
                    "node_id": node_id,
                    "node_name": node.name,
                    "duration": duration
                }
            })

        logger.info(f"Node {node_id} completed in {duration}s")

    def on_node_fail(self, node_id: str, error_message: str) -> None:
        """
        Handle node execution failure.

        Args:
            node_id: Node identifier
            error_message: Error description
        """
        if not self.graph.has_node(node_id):
            logger.warning(f"Node {node_id} not found in graph")
            return

        node = self.graph.get_node(node_id)
        node.mark_failed(error_message)

        self.stats["nodes_failed"] += 1
        self.stats["nodes_running"] -= 1

        self.node_events.append({
            "node_id": node_id,
            "event": "failed",
            "timestamp": datetime.now().isoformat(),
            "error": error_message
        })

        # Publish event
        if self.event_bus:
            self.event_bus.publish({
                "type": "graph.node.failed",
                "source": "graph_monitor",
                "data": {
                    "graph_id": self.graph.graph_id,
                    "node_id": node_id,
                    "node_name": node.name,
                    "error": error_message
                }
            })

        logger.error(f"Node {node_id} failed: {error_message}")

    def update_node_status(self, node_id: str, status: NodeStatus) -> None:
        """
        Update node status manually.

        Args:
            node_id: Node identifier
            status: New status
        """
        if not self.graph.has_node(node_id):
            logger.warning(f"Node {node_id} not found in graph")
            return

        node = self.graph.get_node(node_id)
        old_status = node.status
        node.status = status

        logger.info(f"Node {node_id} status: {old_status.value} -> {status.value}")

    # ==================== Live Metrics ====================

    def get_live_stats(self) -> Dict[str, Any]:
        """
        Get live execution statistics.

        Returns:
            Statistics dictionary
        """
        total_nodes = len(self.graph.nodes)
        completed = self.stats["nodes_completed"]
        failed = self.stats["nodes_failed"]
        running = self.stats["nodes_running"]
        pending = total_nodes - completed - failed - running

        return {
            "graph_id": self.graph.graph_id,
            "total_nodes": total_nodes,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
            "total_duration": self.stats["total_duration"],
            "progress_percent": (completed / total_nodes * 100) if total_nodes > 0 else 0.0
        }

    def get_progress(self) -> float:
        """
        Get execution progress percentage.

        Returns:
            Progress (0.0-100.0)
        """
        total = len(self.graph.nodes)
        if total == 0:
            return 0.0

        completed = self.stats["nodes_completed"]
        return (completed / total) * 100.0

    def get_execution_time(self) -> Optional[float]:
        """
        Get total execution time.

        Returns:
            Execution time in seconds, or None if not started/completed
        """
        if not self.execution_start_time:
            return None

        end = self.execution_end_time or datetime.now()
        return (end - self.execution_start_time).total_seconds()

    # ==================== FAZA 28.5 Integration ====================

    def get_health_report(self) -> Dict[str, Any]:
        """
        Get graph health report for FAZA 28.5 meta-layer.

        Returns:
            Health report
        """
        health = self.analyzer.calculate_graph_health()
        live_stats = self.get_live_stats()

        return {
            "graph_id": self.graph.graph_id,
            "health_score": health["health_score"],
            "status": health["status"],
            "issues": health["issues"],
            "execution_progress": live_stats["progress_percent"],
            "nodes_failed": live_stats["failed"],
            "timestamp": datetime.now().isoformat()
        }

    def get_meta_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for FAZA 28.5 oversight agent.

        Returns:
            Meta-layer metrics
        """
        costs = self.analyzer.calculate_total_cost()
        quality = self.analyzer.check_graph_quality()

        return {
            "graph_id": self.graph.graph_id,
            "quality": quality,
            "costs": costs,
            "live_stats": self.get_live_stats(),
            "health": self.get_health_report(),
            "parallelization_index": self.analyzer.calculate_parallelization_index()
        }

    # ==================== Execution Control ====================

    def start_monitoring(self) -> None:
        """Start execution monitoring"""
        self.execution_start_time = datetime.now()
        self.stats = {
            "nodes_completed": 0,
            "nodes_failed": 0,
            "nodes_running": 0,
            "total_duration": 0.0
        }
        self.node_events.clear()
        logger.info(f"Started monitoring graph {self.graph.graph_id}")

    def stop_monitoring(self) -> None:
        """Stop execution monitoring"""
        self.execution_end_time = datetime.now()
        logger.info(f"Stopped monitoring graph {self.graph.graph_id}")

    def reset(self) -> None:
        """Reset monitoring state"""
        self.execution_start_time = None
        self.execution_end_time = None
        self.node_events.clear()
        self.stats = {
            "nodes_completed": 0,
            "nodes_failed": 0,
            "nodes_running": 0,
            "total_duration": 0.0
        }
        logger.info("Monitor state reset")


def create_graph_monitor(graph: TaskGraph) -> GraphMonitor:
    """
    Factory function to create GraphMonitor instance.

    Args:
        graph: TaskGraph to monitor

    Returns:
        GraphMonitor instance
    """
    return GraphMonitor(graph)
