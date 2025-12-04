"""
FAZA 27 – TaskGraph Engine
Comprehensive Test Suite

Tests all FAZA 27 modules: task_node, task_edge, task_graph,
graph_builder, graph_analyzer, graph_exporter, graph_monitor
"""

import unittest
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from senti_os.core.faza27 import (
    TaskNode,
    TaskEdge,
    TaskGraph,
    NodeStatus,
    EdgeType,
    CostModel,
    GraphBuilder,
    GraphAnalyzer,
    GraphExporter,
    GraphMonitor,
    create_graph_builder,
    create_graph_analyzer,
    create_graph_exporter,
    create_graph_monitor
)


# ==================== Mock FAZA 25/26 Structures ====================

@dataclass
class MockTask:
    """Mock FAZA 25 Task"""
    id: str
    name: str
    status: Any
    priority: int
    task_type: str
    context: dict
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class MockTaskStatus:
    """Mock FAZA 25 TaskStatus"""
    class Status:
        def __init__(self, value):
            self.value = value

    QUEUED = Status("queued")
    RUNNING = Status("running")
    DONE = Status("done")
    ERROR = Status("error")


# ==================== TaskNode Tests ====================

class TestTaskNode(unittest.TestCase):
    """Test TaskNode functionality"""

    def test_node_creation(self):
        """Test basic node creation"""
        node = TaskNode(node_id="task1", name="Test Task", priority=8)
        self.assertEqual(node.node_id, "task1")
        self.assertEqual(node.name, "Test Task")
        self.assertEqual(node.priority, 8)
        self.assertEqual(node.status, NodeStatus.PENDING)

    def test_node_status_transitions(self):
        """Test node status transitions"""
        node = TaskNode(node_id="task1", name="Test")

        node.mark_ready()
        self.assertEqual(node.status, NodeStatus.READY)

        node.mark_running()
        self.assertEqual(node.status, NodeStatus.RUNNING)
        self.assertIsNotNone(node.start_time)

        node.mark_completed(5.0)
        self.assertEqual(node.status, NodeStatus.COMPLETED)
        self.assertEqual(node.actual_duration, 5.0)
        self.assertIsNotNone(node.end_time)

    def test_node_serialization(self):
        """Test node to_dict"""
        node = TaskNode(node_id="task1", name="Test", priority=7)
        data = node.to_dict()

        self.assertEqual(data["node_id"], "task1")
        self.assertEqual(data["name"], "Test")
        self.assertEqual(data["priority"], 7)
        self.assertEqual(data["status"], "pending")

    def test_node_deserialization(self):
        """Test node from_dict"""
        data = {
            "node_id": "task1",
            "name": "Test",
            "node_type": "compute",
            "priority": 8,
            "status": "running",
            "cost_model": {
                "estimated_duration": 5.0,
                "estimated_cost": 1.0
            },
            "metadata": {"key": "value"}
        }

        node = TaskNode.from_dict(data)
        self.assertEqual(node.node_id, "task1")
        self.assertEqual(node.name, "Test")
        self.assertEqual(node.status, NodeStatus.RUNNING)

    def test_node_metadata(self):
        """Test node metadata operations"""
        node = TaskNode(node_id="task1", name="Test")

        node.set_metadata("key1", "value1")
        self.assertEqual(node.get_metadata("key1"), "value1")

        node.update_metadata({"key2": "value2", "key3": "value3"})
        self.assertEqual(node.get_metadata("key2"), "value2")
        self.assertEqual(node.get_metadata("key3"), "value3")

    def test_cost_model(self):
        """Test cost model"""
        cm = CostModel(estimated_duration=10.0, estimated_cost=5.0)
        self.assertEqual(cm.estimated_duration, 10.0)
        self.assertEqual(cm.estimated_cost, 5.0)
        self.assertGreater(cm.total_cost(), 5.0)

    def test_node_terminal_states(self):
        """Test terminal state detection"""
        node = TaskNode(node_id="task1", name="Test")
        self.assertFalse(node.is_terminal())

        node.mark_completed()
        self.assertTrue(node.is_terminal())

        node2 = TaskNode(node_id="task2", name="Test2")
        node2.mark_failed("error")
        self.assertTrue(node2.is_terminal())


# ==================== TaskEdge Tests ====================

class TestTaskEdge(unittest.TestCase):
    """Test TaskEdge functionality"""

    def test_edge_creation(self):
        """Test basic edge creation"""
        edge = TaskEdge(source_id="task1", target_id="task2")
        self.assertEqual(edge.source_id, "task1")
        self.assertEqual(edge.target_id, "task2")
        self.assertEqual(edge.edge_type, EdgeType.DEPENDENCY)

    def test_edge_types(self):
        """Test different edge types"""
        edge = TaskEdge("task1", "task2", EdgeType.DATA_FLOW)
        self.assertEqual(edge.edge_type, EdgeType.DATA_FLOW)
        self.assertFalse(edge.is_dependency())

        edge2 = TaskEdge("task1", "task2", EdgeType.WEAK)
        self.assertTrue(edge2.is_weak())

    def test_edge_constraints(self):
        """Test edge constraints"""
        edge = TaskEdge("task1", "task2")
        edge.set_constraint("max_delay", 10.0)
        self.assertEqual(edge.get_constraint("max_delay"), 10.0)
        self.assertTrue(edge.has_timing_constraint())

    def test_edge_serialization(self):
        """Test edge to_dict"""
        edge = TaskEdge("task1", "task2", EdgeType.CONSTRAINT, weight=2.0)
        data = edge.to_dict()

        self.assertEqual(data["source_id"], "task1")
        self.assertEqual(data["target_id"], "task2")
        self.assertEqual(data["edge_type"], "constraint")
        self.assertEqual(data["weight"], 2.0)

    def test_edge_deserialization(self):
        """Test edge from_dict"""
        data = {
            "source_id": "task1",
            "target_id": "task2",
            "edge_type": "data_flow",
            "weight": 1.5
        }

        edge = TaskEdge.from_dict(data)
        self.assertEqual(edge.source_id, "task1")
        self.assertEqual(edge.edge_type, EdgeType.DATA_FLOW)


# ==================== TaskGraph Tests ====================

class TestTaskGraph(unittest.TestCase):
    """Test TaskGraph functionality"""

    def test_graph_creation(self):
        """Test basic graph creation"""
        graph = TaskGraph(graph_id="test_graph")
        self.assertEqual(graph.graph_id, "test_graph")
        self.assertEqual(len(graph.nodes), 0)
        self.assertEqual(len(graph.edges), 0)

    def test_add_remove_nodes(self):
        """Test adding and removing nodes"""
        graph = TaskGraph()
        node1 = TaskNode("task1", "Task 1")
        node2 = TaskNode("task2", "Task 2")

        graph.add_node(node1)
        graph.add_node(node2)
        self.assertEqual(len(graph.nodes), 2)
        self.assertTrue(graph.has_node("task1"))

        graph.remove_node("task1")
        self.assertEqual(len(graph.nodes), 1)
        self.assertFalse(graph.has_node("task1"))

    def test_add_remove_edges(self):
        """Test adding and removing edges"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))

        edge = TaskEdge("task1", "task2")
        graph.add_edge(edge)
        self.assertEqual(len(graph.edges), 1)
        self.assertTrue(graph.has_edge("task1", "task2"))

        graph.remove_edge("task1", "task2")
        self.assertEqual(len(graph.edges), 0)

    def test_cycle_detection(self):
        """Test cycle detection"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_node(TaskNode("task3", "Task 3"))

        graph.add_edge(TaskEdge("task1", "task2"))
        graph.add_edge(TaskEdge("task2", "task3"))

        # Should reject edge that creates cycle
        with self.assertRaises(ValueError):
            graph.add_edge(TaskEdge("task3", "task1"))

        self.assertTrue(graph.is_acyclic())

    def test_self_loop_prevention(self):
        """Test self-loop prevention"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))

        with self.assertRaises(ValueError):
            graph.add_edge(TaskEdge("task1", "task1"))

    def test_topological_sort(self):
        """Test topological sorting"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_node(TaskNode("task3", "Task 3"))

        graph.add_edge(TaskEdge("task1", "task2"))
        graph.add_edge(TaskEdge("task2", "task3"))

        topo_order = graph.topological_sort()
        self.assertEqual(len(topo_order), 3)
        self.assertTrue(topo_order.index("task1") < topo_order.index("task2"))
        self.assertTrue(topo_order.index("task2") < topo_order.index("task3"))

    def test_root_leaf_nodes(self):
        """Test root and leaf node detection"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_node(TaskNode("task3", "Task 3"))

        graph.add_edge(TaskEdge("task1", "task2"))
        graph.add_edge(TaskEdge("task2", "task3"))

        roots = graph.get_root_nodes()
        leaves = graph.get_leaf_nodes()

        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].node_id, "task1")
        self.assertEqual(len(leaves), 1)
        self.assertEqual(leaves[0].node_id, "task3")

    def test_node_levels(self):
        """Test node level calculation"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_node(TaskNode("task3", "Task 3"))

        graph.add_edge(TaskEdge("task1", "task2"))
        graph.add_edge(TaskEdge("task2", "task3"))

        levels = graph.calculate_node_levels()
        self.assertEqual(levels["task1"], 0)
        self.assertEqual(levels["task2"], 1)
        self.assertEqual(levels["task3"], 2)

    def test_critical_path(self):
        """Test critical path calculation"""
        graph = TaskGraph()
        n1 = TaskNode("task1", "Task 1", cost_model=CostModel(estimated_duration=5.0))
        n2 = TaskNode("task2", "Task 2", cost_model=CostModel(estimated_duration=10.0))
        n3 = TaskNode("task3", "Task 3", cost_model=CostModel(estimated_duration=3.0))

        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_node(n3)

        graph.add_edge(TaskEdge("task1", "task2"))
        graph.add_edge(TaskEdge("task2", "task3"))

        path, duration = graph.calculate_critical_path()
        self.assertEqual(len(path), 3)
        self.assertEqual(duration, 18.0)  # 5 + 10 + 3

    def test_graph_validation(self):
        """Test graph validation"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_edge(TaskEdge("task1", "task2"))

        is_valid, errors = graph.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_graph_serialization(self):
        """Test graph serialization"""
        graph = TaskGraph(graph_id="test")
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_edge(TaskEdge("task1", "task2"))

        data = graph.to_dict()
        self.assertEqual(data["graph_id"], "test")
        self.assertEqual(data["node_count"], 2)
        self.assertEqual(data["edge_count"], 1)

    def test_graph_deserialization(self):
        """Test graph deserialization"""
        graph = TaskGraph(graph_id="test")
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_edge(TaskEdge("task1", "task2"))

        data = graph.to_dict()
        graph2 = TaskGraph.from_dict(data)

        self.assertEqual(graph2.graph_id, "test")
        self.assertEqual(len(graph2.nodes), 2)
        self.assertEqual(len(graph2.edges), 1)

    def test_graph_stats(self):
        """Test graph statistics"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_edge(TaskEdge("task1", "task2"))

        stats = graph.get_stats()
        self.assertEqual(stats["node_count"], 2)
        self.assertEqual(stats["edge_count"], 1)
        self.assertTrue(stats["is_acyclic"])

    def test_has_node_edge(self):
        """Test has_node and has_edge"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_edge(TaskEdge("task1", "task2"))

        self.assertTrue(graph.has_node("task1"))
        self.assertFalse(graph.has_node("task3"))
        self.assertTrue(graph.has_edge("task1", "task2"))
        self.assertFalse(graph.has_edge("task2", "task1"))

    def test_get_edges_from_to(self):
        """Test get_edges_from and get_edges_to"""
        graph = TaskGraph()
        graph.add_node(TaskNode("task1", "Task 1"))
        graph.add_node(TaskNode("task2", "Task 2"))
        graph.add_node(TaskNode("task3", "Task 3"))

        graph.add_edge(TaskEdge("task1", "task2"))
        graph.add_edge(TaskEdge("task1", "task3"))

        edges_from = graph.get_edges_from("task1")
        self.assertEqual(len(edges_from), 2)

        edges_to = graph.get_edges_to("task2")
        self.assertEqual(len(edges_to), 1)


# ==================== GraphBuilder Tests ====================

class TestGraphBuilder(unittest.TestCase):
    """Test GraphBuilder functionality"""

    def test_builder_creation(self):
        """Test builder creation"""
        builder = create_graph_builder()
        self.assertIsInstance(builder, GraphBuilder)

    def test_faza25_single_task(self):
        """Test FAZA 25 single task conversion"""
        builder = GraphBuilder()
        task = MockTask(
            id="task1",
            name="Test Task",
            status=MockTaskStatus.QUEUED,
            priority=8,
            task_type="computation",
            context={"key": "value"}
        )

        graph = builder.from_faza25_task(task)
        self.assertEqual(len(graph.nodes), 1)
        self.assertTrue(graph.has_node("task1"))

    def test_faza25_multiple_tasks(self):
        """Test FAZA 25 multiple tasks conversion"""
        builder = GraphBuilder()
        tasks = [
            MockTask("task1", "Task 1", MockTaskStatus.QUEUED, 8, "data_fetch", {}),
            MockTask("task2", "Task 2", MockTaskStatus.QUEUED, 7, "computation", {}),
            MockTask("task3", "Task 3", MockTaskStatus.QUEUED, 6, "aggregation", {})
        ]

        graph = builder.from_faza25_tasks(tasks)
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)  # Sequential dependencies

    def test_faza26_workflow(self):
        """Test FAZA 26 workflow conversion"""
        builder = GraphBuilder()
        workflow = [
            {"task": "fetch_data", "priority": 7, "metadata": {"task_type": "data_fetch"}},
            {"task": "compute_sentiment", "priority": 8, "metadata": {"task_type": "computation"}},
            {"task": "aggregate_results", "priority": 6, "metadata": {"task_type": "aggregation"}}
        ]

        graph = builder.from_faza26_workflow(workflow)
        self.assertEqual(len(graph.nodes), 3)
        # Should have dependency edges based on patterns
        self.assertGreater(len(graph.edges), 0)

    def test_faza26_sequential(self):
        """Test FAZA 26 sequential conversion"""
        builder = GraphBuilder()
        workflow = [
            {"task": "task1", "priority": 7, "metadata": {"task_type": "generic"}},
            {"task": "task2", "priority": 8, "metadata": {"task_type": "generic"}}
        ]

        graph = builder.from_faza26_sequential(workflow)
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)

    def test_merge_graphs(self):
        """Test graph merging"""
        builder = GraphBuilder()

        graph1 = TaskGraph(graph_id="graph1")
        graph1.add_node(TaskNode("task1", "Task 1"))

        graph2 = TaskGraph(graph_id="graph2")
        graph2.add_node(TaskNode("task2", "Task 2"))

        merged = builder.merge_graphs([graph1, graph2])
        self.assertEqual(len(merged.nodes), 2)

    def test_custom_cost_model(self):
        """Test custom cost model registration"""
        builder = GraphBuilder()
        custom_cost = CostModel(estimated_duration=20.0, cpu_units=8.0)
        builder.add_cost_model("custom_type", custom_cost)

        self.assertIn("custom_type", builder.cost_models)

    def test_custom_dependency_pattern(self):
        """Test custom dependency pattern"""
        builder = GraphBuilder()
        builder.add_dependency_pattern("custom_task", ["dep1", "dep2"])

        self.assertIn("custom_task", builder.dependency_patterns)


# ==================== GraphAnalyzer Tests ====================

class TestGraphAnalyzer(unittest.TestCase):
    """Test GraphAnalyzer functionality"""

    def setUp(self):
        """Set up test graph"""
        self.graph = TaskGraph()
        self.graph.add_node(TaskNode("task1", "Task 1"))
        self.graph.add_node(TaskNode("task2", "Task 2"))
        self.graph.add_node(TaskNode("task3", "Task 3"))
        self.graph.add_edge(TaskEdge("task1", "task2"))
        self.graph.add_edge(TaskEdge("task2", "task3"))

    def test_analyzer_creation(self):
        """Test analyzer creation"""
        analyzer = create_graph_analyzer(self.graph)
        self.assertIsInstance(analyzer, GraphAnalyzer)

    def test_find_cycles(self):
        """Test cycle detection"""
        analyzer = GraphAnalyzer(self.graph)
        cycles = analyzer.find_all_cycles()
        self.assertEqual(len(cycles), 0)

    def test_find_bottlenecks(self):
        """Test bottleneck detection"""
        # Create graph with bottleneck
        graph = TaskGraph()
        for i in range(6):
            graph.add_node(TaskNode(f"task{i}", f"Task {i}"))

        # Create convergence bottleneck at task3
        graph.add_edge(TaskEdge("task0", "task3"))
        graph.add_edge(TaskEdge("task1", "task3"))
        graph.add_edge(TaskEdge("task2", "task3"))

        analyzer = GraphAnalyzer(graph)
        bottlenecks = analyzer.find_bottlenecks(threshold=3)
        self.assertGreater(len(bottlenecks), 0)

    def test_find_critical_nodes(self):
        """Test critical node detection"""
        analyzer = GraphAnalyzer(self.graph)
        critical = analyzer.find_critical_nodes()
        self.assertEqual(len(critical), 3)

    def test_calculate_criticality(self):
        """Test criticality calculation"""
        analyzer = GraphAnalyzer(self.graph)
        criticality = analyzer.calculate_node_criticality()
        self.assertEqual(len(criticality), 3)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in criticality.values()))

    def test_influence_scores(self):
        """Test influence score calculation"""
        analyzer = GraphAnalyzer(self.graph)
        scores = analyzer.calculate_influence_scores()
        self.assertEqual(len(scores), 3)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in scores.values()))

    def test_parallelization_index(self):
        """Test parallelization index"""
        analyzer = GraphAnalyzer(self.graph)
        index = analyzer.calculate_parallelization_index()
        self.assertGreaterEqual(index, 0.0)
        self.assertLessEqual(index, 1.0)

    def test_parallel_stages(self):
        """Test parallel stage detection"""
        analyzer = GraphAnalyzer(self.graph)
        stages = analyzer.find_parallel_stages()
        self.assertGreater(len(stages), 0)

    def test_graph_health(self):
        """Test graph health calculation"""
        analyzer = GraphAnalyzer(self.graph)
        health = analyzer.calculate_graph_health()
        self.assertIn("health_score", health)
        self.assertIn("status", health)
        self.assertGreaterEqual(health["health_score"], 0.0)
        self.assertLessEqual(health["health_score"], 100.0)

    def test_graph_quality(self):
        """Test graph quality check"""
        analyzer = GraphAnalyzer(self.graph)
        quality = analyzer.check_graph_quality()
        self.assertIn("node_count", quality)
        self.assertIn("edge_count", quality)

    def test_total_cost(self):
        """Test total cost calculation"""
        analyzer = GraphAnalyzer(self.graph)
        costs = analyzer.calculate_total_cost()
        self.assertIn("total_duration_sequential", costs)
        self.assertIn("critical_path_duration", costs)

    def test_analysis_report(self):
        """Test comprehensive analysis report"""
        analyzer = GraphAnalyzer(self.graph)
        report = analyzer.get_analysis_report()
        self.assertIn("health", report)
        self.assertIn("quality", report)
        self.assertIn("costs", report)


# ==================== GraphExporter Tests ====================

class TestGraphExporter(unittest.TestCase):
    """Test GraphExporter functionality"""

    def setUp(self):
        """Set up test graph"""
        self.graph = TaskGraph(graph_id="test_graph")
        self.graph.add_node(TaskNode("task1", "Task 1", priority=8))
        self.graph.add_node(TaskNode("task2", "Task 2", priority=7))
        self.graph.add_edge(TaskEdge("task1", "task2"))

    def test_exporter_creation(self):
        """Test exporter creation"""
        exporter = create_graph_exporter(self.graph)
        self.assertIsInstance(exporter, GraphExporter)

    def test_export_json(self):
        """Test JSON export"""
        exporter = GraphExporter(self.graph)
        json_str = exporter.export_json()
        data = json.loads(json_str)

        self.assertEqual(data["graph_id"], "test_graph")
        self.assertEqual(data["node_count"], 2)

    def test_export_dot(self):
        """Test DOT export"""
        exporter = GraphExporter(self.graph)
        dot_str = exporter.export_dot()

        self.assertIn("digraph TaskGraph", dot_str)
        self.assertIn("task1", dot_str)
        self.assertIn("task2", dot_str)

    def test_export_markdown(self):
        """Test Markdown export"""
        exporter = GraphExporter(self.graph)
        md_str = exporter.export_markdown()

        self.assertIn("# TaskGraph", md_str)
        self.assertIn("## Statistics", md_str)
        self.assertIn("## Nodes", md_str)

    def test_export_yaml(self):
        """Test YAML export"""
        exporter = GraphExporter(self.graph)
        yaml_str = exporter.export_yaml()

        self.assertIn("graph_id: test_graph", yaml_str)
        self.assertIn("node_count: 2", yaml_str)

    def test_save_to_file(self):
        """Test save to file"""
        exporter = GraphExporter(self.graph)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_graph.json"
            exporter.save_to_file(str(filepath), format="json")
            self.assertTrue(filepath.exists())

    def test_export_with_analysis(self):
        """Test export with analysis"""
        exporter = GraphExporter(self.graph)
        json_str = exporter.export_with_analysis(format="json")
        data = json.loads(json_str)

        self.assertIn("analysis", data)


# ==================== GraphMonitor Tests ====================

class TestGraphMonitor(unittest.TestCase):
    """Test GraphMonitor functionality"""

    def setUp(self):
        """Set up test graph"""
        self.graph = TaskGraph()
        self.graph.add_node(TaskNode("task1", "Task 1"))
        self.graph.add_node(TaskNode("task2", "Task 2"))
        self.graph.add_edge(TaskEdge("task1", "task2"))

    def test_monitor_creation(self):
        """Test monitor creation"""
        monitor = create_graph_monitor(self.graph)
        self.assertIsInstance(monitor, GraphMonitor)

    def test_node_start(self):
        """Test node start tracking"""
        monitor = GraphMonitor(self.graph)
        monitor.start_monitoring()
        monitor.on_node_start("task1")

        node = self.graph.get_node("task1")
        self.assertEqual(node.status, NodeStatus.RUNNING)
        self.assertEqual(monitor.stats["nodes_running"], 1)

    def test_node_complete(self):
        """Test node completion tracking"""
        monitor = GraphMonitor(self.graph)
        monitor.start_monitoring()
        monitor.on_node_start("task1")
        monitor.on_node_complete("task1", 5.0)

        node = self.graph.get_node("task1")
        self.assertEqual(node.status, NodeStatus.COMPLETED)
        self.assertEqual(monitor.stats["nodes_completed"], 1)

    def test_node_fail(self):
        """Test node failure tracking"""
        monitor = GraphMonitor(self.graph)
        monitor.start_monitoring()
        monitor.on_node_start("task1")
        monitor.on_node_fail("task1", "Test error")

        node = self.graph.get_node("task1")
        self.assertEqual(node.status, NodeStatus.FAILED)
        self.assertEqual(monitor.stats["nodes_failed"], 1)

    def test_live_stats(self):
        """Test live statistics"""
        monitor = GraphMonitor(self.graph)
        monitor.start_monitoring()
        monitor.on_node_start("task1")
        monitor.on_node_complete("task1", 5.0)

        stats = monitor.get_live_stats()
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["total_nodes"], 2)

    def test_progress(self):
        """Test progress calculation"""
        monitor = GraphMonitor(self.graph)
        monitor.start_monitoring()
        monitor.on_node_start("task1")
        monitor.on_node_complete("task1", 5.0)

        progress = monitor.get_progress()
        self.assertEqual(progress, 50.0)  # 1 of 2 completed

    def test_health_report(self):
        """Test health report"""
        monitor = GraphMonitor(self.graph)
        monitor.start_monitoring()

        report = monitor.get_health_report()
        self.assertIn("health_score", report)
        self.assertIn("status", report)

    def test_meta_metrics(self):
        """Test meta-layer metrics"""
        monitor = GraphMonitor(self.graph)
        monitor.start_monitoring()

        metrics = monitor.get_meta_metrics()
        self.assertIn("quality", metrics)
        self.assertIn("costs", metrics)
        self.assertIn("live_stats", metrics)


# ==================== Main ====================

if __name__ == "__main__":
    unittest.main()
