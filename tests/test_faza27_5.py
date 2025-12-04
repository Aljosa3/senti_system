"""
FAZA 27.5 - Execution Optimizer Layer
Comprehensive Test Suite

Tests all components:
- TaskGraph creation and manipulation
- Graph validation
- Cycle detection
- Redundancy elimination
- Task batching
- DAG reordering
- Short-circuiting
- Optimizer Manager integration
- Report generation
"""

from senti_os.core.faza27_5 import (
    TaskGraph,
    TaskNode,
    TaskType,
    create_sample_graph,
    GraphValidator,
    ValidationError,
    Pass1_DAGReordering,
    Pass2_RedundancyElimination,
    Pass3_TaskBatching,
    Pass4_ShortCircuiting,
    Pass5_CostBasedSorting,
    OptimizationPipeline,
    OptimizationReport,
    ReportBuilder,
    OptimizerManager,
    get_optimizer
)


class TestTaskGraph:
    """Tests for TaskGraph creation and manipulation"""

    def test_graph_creation(self):
        """Test creating empty graph"""
        graph = TaskGraph("test_graph")
        assert graph.name == "test_graph"
        assert len(graph) == 0

    def test_add_node(self):
        """Test adding nodes to graph"""
        graph = TaskGraph()
        node = TaskNode(id="node1", name="Test Node")
        graph.add_node(node)

        assert len(graph) == 1
        assert "node1" in graph.nodes
        assert "node1" in graph.root_nodes
        assert "node1" in graph.leaf_nodes

    def test_add_edge(self):
        """Test adding dependencies between nodes"""
        graph = TaskGraph()
        n1 = TaskNode(id="n1", name="Node 1")
        n2 = TaskNode(id="n2", name="Node 2")

        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_edge("n1", "n2")

        assert "n1" in n2.dependencies
        assert "n2" in n1.dependents
        assert "n1" in graph.root_nodes
        assert "n2" in graph.leaf_nodes
        assert "n1" not in graph.leaf_nodes

    def test_get_execution_order(self):
        """Test topological sort"""
        graph = create_sample_graph()
        order = graph.get_execution_order()

        assert len(order) == 4  # 4 levels
        assert "task1" in order[0]
        assert "task2" in order[1]
        assert "task3" in order[2]
        assert "task4" in order[3]

    def test_get_critical_path(self):
        """Test critical path calculation"""
        graph = create_sample_graph()
        critical = graph.get_critical_path()

        assert len(critical) == 4
        assert "task3" in critical  # Longest duration task

    def test_graph_clone(self):
        """Test graph cloning"""
        graph = create_sample_graph()
        cloned = graph.clone()

        assert len(cloned) == len(graph)
        assert cloned.name == graph.name
        # Verify it's a deep copy
        assert cloned is not graph
        assert cloned.nodes is not graph.nodes


class TestGraphValidator:
    """Tests for graph validation"""

    def test_validator_creation(self):
        """Test validator initialization"""
        validator = GraphValidator()
        assert validator is not None

    def test_validate_empty_graph(self):
        """Test validating empty graph"""
        validator = GraphValidator()
        graph = TaskGraph()

        result = validator.validate(graph)
        assert result["valid"] is True
        assert len(result["warnings"]) == 1  # Empty graph warning

    def test_validate_valid_graph(self):
        """Test validating correct graph"""
        validator = GraphValidator()
        graph = create_sample_graph()

        result = validator.validate(graph)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_detect_missing_dependency(self):
        """Test detection of missing dependencies"""
        validator = GraphValidator()
        graph = TaskGraph()

        n1 = TaskNode(id="n1", name="Node 1")
        n1.dependencies.add("missing_node")
        graph.add_node(n1)

        result = validator.validate(graph)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "missing dependency" in result["errors"][0]

    def test_detect_cycle(self):
        """Test cycle detection"""
        validator = GraphValidator()
        graph = TaskGraph()

        n1 = TaskNode(id="n1")
        n2 = TaskNode(id="n2")
        n3 = TaskNode(id="n3")

        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_node(n3)

        # Create cycle: n1 -> n2 -> n3 -> n1
        graph.add_edge("n1", "n2")
        graph.add_edge("n2", "n3")
        graph.add_edge("n3", "n1")

        result = validator.validate(graph)
        assert result["valid"] is False
        assert any("Cycle detected" in err for err in result["errors"])

    def test_detect_orphan_nodes(self):
        """Test detection of orphan nodes"""
        validator = GraphValidator()
        graph = TaskGraph()

        # Add orphan node (no deps, no dependents)
        orphan = TaskNode(id="orphan", name="Orphan")
        graph.add_node(orphan)

        result = validator.validate(graph)
        assert result["valid"] is True  # Not an error, just a warning
        assert len(result["warnings"]) > 0
        assert any("Orphan" in w for w in result["warnings"])

    def test_schema_validation(self):
        """Test node schema validation"""
        validator = GraphValidator()
        graph = TaskGraph()

        # Node with invalid priority
        bad_node = TaskNode(id="bad", name="Bad", priority=15)
        graph.add_node(bad_node)

        result = validator.validate(graph)
        assert len(result["warnings"]) > 0
        assert any("priority" in w for w in result["warnings"])


class TestOptimizationPasses:
    """Tests for individual optimization passes"""

    def test_pass1_dag_reordering(self):
        """Test DAG reordering pass"""
        pass1 = Pass1_DAGReordering()
        graph = create_sample_graph()

        optimized = pass1.apply(graph)
        assert optimized is not None
        assert pass1.changes_made >= 0

    def test_pass2_redundancy_elimination(self):
        """Test redundancy elimination"""
        pass2 = Pass2_RedundancyElimination()
        graph = TaskGraph()

        # Create duplicate nodes
        n1 = TaskNode(id="n1", name="Task", task_type=TaskType.COMPUTE)
        n2 = TaskNode(id="n2", name="Task", task_type=TaskType.COMPUTE)  # Duplicate

        graph.add_node(n1)
        graph.add_node(n2)

        optimized = pass2.apply(graph)
        assert len(optimized) == 1  # One removed
        assert pass2.changes_made == 1

    def test_pass3_task_batching(self):
        """Test task batching"""
        pass3 = Pass3_TaskBatching()
        graph = TaskGraph()

        # Create similar tasks at same level
        n1 = TaskNode(id="n1", name="Compute1", task_type=TaskType.COMPUTE)
        n2 = TaskNode(id="n2", name="Compute2", task_type=TaskType.COMPUTE)

        graph.add_node(n1)
        graph.add_node(n2)

        optimized = pass3.apply(graph)

        # Check batching metadata
        assert optimized.nodes["n1"].metadata.get("batchable") is True
        assert optimized.nodes["n2"].metadata.get("batchable") is True
        assert optimized.nodes["n1"].metadata.get("batch_id") == \
               optimized.nodes["n2"].metadata.get("batch_id")

    def test_pass4_short_circuiting(self):
        """Test short-circuiting"""
        pass4 = Pass4_ShortCircuiting()
        graph = TaskGraph()

        # Create cacheable node
        n1 = TaskNode(id="n1", name="Cacheable", cacheable=True, cache_key="key1")
        graph.add_node(n1)

        optimized = pass4.apply(graph)
        assert optimized.nodes["n1"].metadata.get("can_skip") is True

    def test_pass5_cost_based_sorting(self):
        """Test cost-based sorting"""
        pass5 = Pass5_CostBasedSorting()
        graph = TaskGraph()

        # Create nodes with different costs
        n1 = TaskNode(id="n1", estimated_duration=1.0, estimated_cost=0.1)
        n2 = TaskNode(id="n2", estimated_duration=10.0, estimated_cost=1.0)

        graph.add_node(n1)
        graph.add_node(n2)

        optimized = pass5.apply(graph)
        assert optimized is not None


class TestOptimizationPipeline:
    """Tests for optimization pipeline"""

    def test_pipeline_creation(self):
        """Test creating pipeline"""
        pipeline = OptimizationPipeline()
        assert len(pipeline.passes) == 5

    def test_pipeline_apply_all(self):
        """Test applying all passes"""
        pipeline = OptimizationPipeline()
        graph = create_sample_graph()

        optimized = pipeline.apply_all(graph)
        assert optimized is not None
        assert len(optimized) <= len(graph)

    def test_pipeline_get_stats(self):
        """Test getting pipeline statistics"""
        pipeline = OptimizationPipeline()
        graph = create_sample_graph()

        pipeline.apply_all(graph)
        stats = pipeline.get_stats()

        assert len(stats) == 5  # 5 passes
        for stat in stats:
            assert "pass_name" in stat
            assert "changes" in stat


class TestOptimizationReport:
    """Tests for optimization reports"""

    def test_report_creation(self):
        """Test creating report"""
        report = OptimizationReport()
        assert report.timestamp is not None
        assert report.nodes_before == 0
        assert report.nodes_after == 0

    def test_report_calculations(self):
        """Test report calculations"""
        report = OptimizationReport()
        report.nodes_before = 10
        report.nodes_after = 8
        report.estimated_time_before = 100.0
        report.estimated_time_after = 80.0

        assert report.get_node_reduction() == 2
        assert report.get_time_savings() == 20.0
        assert report.get_time_savings_percent() == 20.0

    def test_report_format_text(self):
        """Test text formatting"""
        report = OptimizationReport()
        report.graph_name = "test"
        report.nodes_before = 5
        report.nodes_after = 4

        text = report.format_text()
        assert "test" in text
        assert "5" in text
        assert "4" in text

    def test_report_format_summary(self):
        """Test summary formatting"""
        report = OptimizationReport()
        report.graph_name = "test"
        report.nodes_before = 10
        report.nodes_after = 8

        summary = report.format_summary()
        assert "test" in summary
        assert "10" in summary
        assert "8" in summary

    def test_report_builder(self):
        """Test report builder"""
        builder = ReportBuilder()
        report = (builder
                  .set_graph_name("test")
                  .set_before_stats(10, 15)
                  .set_after_stats(8, 12)
                  .build())

        assert report.graph_name == "test"
        assert report.nodes_before == 10
        assert report.nodes_after == 8


class TestOptimizerManager:
    """Tests for optimizer manager"""

    def test_manager_creation(self):
        """Test manager initialization"""
        manager = OptimizerManager()
        assert manager is not None
        assert manager.validator is not None
        assert manager.pipeline is not None

    def test_optimize_valid_graph(self):
        """Test optimizing valid graph"""
        manager = OptimizerManager()
        graph = create_sample_graph()

        optimized, report = manager.optimize(graph)

        assert optimized is not None
        assert report is not None
        assert report.nodes_before >= report.nodes_after

    def test_validate_only(self):
        """Test validation without optimization"""
        manager = OptimizerManager()
        graph = create_sample_graph()

        result = manager.validate_only(graph)
        assert result["valid"] is True

    def test_quick_optimize(self):
        """Test quick optimization"""
        manager = OptimizerManager()
        graph = create_sample_graph()

        optimized = manager.quick_optimize(graph)
        assert optimized is not None

    def test_export_to_faza25(self):
        """Test FAZA 25 export"""
        manager = OptimizerManager()
        graph = create_sample_graph()

        task_specs = manager.export_to_faza25(graph)
        assert isinstance(task_specs, list)
        assert len(task_specs) > 0  # At least some tasks exported

    def test_singleton_pattern(self):
        """Test get_optimizer singleton"""
        opt1 = get_optimizer()
        opt2 = get_optimizer()
        assert opt1 is opt2


def run_all_tests():
    """Run all test suites"""
    print("="*70)
    print("FAZA 27.5 - Execution Optimizer Layer - Test Suite")
    print("="*70)

    # TaskGraph tests
    print("\n" + "="*70)
    print("Running TaskGraph Tests")
    print("="*70)

    test_graph = TestTaskGraph()
    test_graph.test_graph_creation()
    print("✓ Graph creation")

    test_graph.test_add_node()
    print("✓ Add node")

    test_graph.test_add_edge()
    print("✓ Add edge")

    test_graph.test_get_execution_order()
    print("✓ Execution order")

    test_graph.test_get_critical_path()
    print("✓ Critical path")

    test_graph.test_graph_clone()
    print("✓ Graph clone")

    # Validator tests
    print("\n" + "="*70)
    print("Running Graph Validator Tests")
    print("="*70)

    test_validator = TestGraphValidator()
    test_validator.test_validator_creation()
    print("✓ Validator creation")

    test_validator.test_validate_empty_graph()
    print("✓ Validate empty graph")

    test_validator.test_validate_valid_graph()
    print("✓ Validate valid graph")

    test_validator.test_detect_missing_dependency()
    print("✓ Detect missing dependency")

    test_validator.test_detect_cycle()
    print("✓ Detect cycle")

    test_validator.test_detect_orphan_nodes()
    print("✓ Detect orphan nodes")

    test_validator.test_schema_validation()
    print("✓ Schema validation")

    # Optimization passes tests
    print("\n" + "="*70)
    print("Running Optimization Passes Tests")
    print("="*70)

    test_passes = TestOptimizationPasses()
    test_passes.test_pass1_dag_reordering()
    print("✓ Pass 1: DAG reordering")

    test_passes.test_pass2_redundancy_elimination()
    print("✓ Pass 2: Redundancy elimination")

    test_passes.test_pass3_task_batching()
    print("✓ Pass 3: Task batching")

    test_passes.test_pass4_short_circuiting()
    print("✓ Pass 4: Short-circuiting")

    test_passes.test_pass5_cost_based_sorting()
    print("✓ Pass 5: Cost-based sorting")

    # Pipeline tests
    print("\n" + "="*70)
    print("Running Optimization Pipeline Tests")
    print("="*70)

    test_pipeline = TestOptimizationPipeline()
    test_pipeline.test_pipeline_creation()
    print("✓ Pipeline creation")

    test_pipeline.test_pipeline_apply_all()
    print("✓ Pipeline apply all")

    test_pipeline.test_pipeline_get_stats()
    print("✓ Pipeline statistics")

    # Report tests
    print("\n" + "="*70)
    print("Running Optimization Report Tests")
    print("="*70)

    test_report = TestOptimizationReport()
    test_report.test_report_creation()
    print("✓ Report creation")

    test_report.test_report_calculations()
    print("✓ Report calculations")

    test_report.test_report_format_text()
    print("✓ Report text format")

    test_report.test_report_format_summary()
    print("✓ Report summary format")

    test_report.test_report_builder()
    print("✓ Report builder")

    # Manager tests
    print("\n" + "="*70)
    print("Running Optimizer Manager Tests")
    print("="*70)

    test_manager = TestOptimizerManager()
    test_manager.test_manager_creation()
    print("✓ Manager creation")

    test_manager.test_optimize_valid_graph()
    print("✓ Optimize valid graph")

    test_manager.test_validate_only()
    print("✓ Validate only")

    test_manager.test_quick_optimize()
    print("✓ Quick optimize")

    test_manager.test_export_to_faza25()
    print("✓ Export to FAZA 25")

    test_manager.test_singleton_pattern()
    print("✓ Singleton pattern")

    print("\n" + "="*70)
    print("✓ ALL 31 TESTS PASSED")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
