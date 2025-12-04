"""
FAZA 26 - Intelligent Action Layer
Comprehensive Test Suite

Tests all components:
- IntentParser
- SemanticPlanner
- PolicyEngine
- ActionMapper
- ActionLayer (full pipeline)
"""

import asyncio
from unittest.mock import Mock, MagicMock, patch

from senti_os.core.faza26.intent_parser import IntentParser, create_intent_parser
from senti_os.core.faza26.semantic_planner import SemanticPlanner, create_semantic_planner
from senti_os.core.faza26.policy_engine import (
    PolicyEngine,
    RejectedTaskError,
    create_policy_engine
)
from senti_os.core.faza26.action_mapper import ActionMapper, create_action_mapper
from senti_os.core.faza26.action_layer import ActionLayer, create_action_layer, get_action_layer


class TestIntentParser:
    """Tests for IntentParser"""

    def test_parser_creation(self):
        """Test parser initialization"""
        parser = create_intent_parser()
        assert parser is not None
        assert isinstance(parser, IntentParser)

    def test_parse_sentiment_command(self):
        """Test parsing sentiment analysis command"""
        parser = IntentParser()
        result = parser.parse("analyze sentiment count=200 dataset=articles with plot")

        assert result["intent"] == "analyze_sentiment"
        assert result["parameters"]["count"] == 200
        assert result["parameters"]["dataset"] == "articles"
        assert result["parameters"]["generate_plot"] is True

    def test_parse_compute_command(self):
        """Test parsing compute command"""
        parser = IntentParser()
        result = parser.parse("compute statistics")

        assert result["intent"] == "compute"
        assert "parameters" in result

    def test_parse_plot_command(self):
        """Test parsing plot generation command"""
        parser = IntentParser()
        result = parser.parse("generate plot format=png")

        assert result["intent"] == "generate_plot"
        assert result["parameters"]["format"] == "png"

    def test_parse_invalid_command(self):
        """Test that invalid commands raise ValueError"""
        parser = IntentParser()

        try:
            parser.parse("invalid nonsense command xyz")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Could not determine intent" in str(e)

    def test_parse_empty_command(self):
        """Test that empty commands raise ValueError"""
        parser = IntentParser()

        try:
            parser.parse("")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "cannot be empty" in str(e)

    def test_validate_valid_intent(self):
        """Test validation of valid intent"""
        parser = IntentParser()
        valid_intent = {
            "intent": "analyze_sentiment",
            "parameters": {"count": 100},
            "raw_text": "test"
        }

        # Should not raise
        parser.validate(valid_intent)

    def test_validate_invalid_intent(self):
        """Test validation of invalid intent structure"""
        parser = IntentParser()

        try:
            parser.validate({"parameters": {}})  # Missing intent
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_get_supported_intents(self):
        """Test getting supported intents"""
        parser = IntentParser()
        intents = parser.get_supported_intents()

        assert isinstance(intents, list)
        assert len(intents) > 0
        assert "analyze_sentiment" in intents


class TestSemanticPlanner:
    """Tests for SemanticPlanner"""

    def test_planner_creation(self):
        """Test planner initialization"""
        planner = create_semantic_planner()
        assert planner is not None
        assert isinstance(planner, SemanticPlanner)

    def test_plan_sentiment_analysis(self):
        """Test planning sentiment analysis workflow"""
        planner = SemanticPlanner()
        intent = {
            "intent": "analyze_sentiment",
            "parameters": {
                "count": 200,
                "dataset": "articles",
                "generate_plot": True
            }
        }

        tasks = planner.plan(intent)

        # Should generate 4 tasks: fetch, compute, aggregate, plot
        assert len(tasks) == 4
        assert tasks[0]["task"] == "fetch_data"
        assert tasks[1]["task"] == "compute_sentiment"
        assert tasks[2]["task"] == "aggregate_results"
        assert tasks[3]["task"] == "generate_plot"

    def test_plan_sentiment_without_plot(self):
        """Test planning sentiment analysis without plot"""
        planner = SemanticPlanner()
        intent = {
            "intent": "analyze_sentiment",
            "parameters": {"count": 100, "generate_plot": False}
        }

        tasks = planner.plan(intent)

        # Should generate 3 tasks (no plot)
        assert len(tasks) == 3
        assert all(t["task"] != "generate_plot" for t in tasks)

    def test_plan_compute(self):
        """Test planning compute task"""
        planner = SemanticPlanner()
        intent = {
            "intent": "compute",
            "parameters": {}
        }

        tasks = planner.plan(intent)

        assert len(tasks) == 1
        assert tasks[0]["task"] == "compute"

    def test_plan_data_processing(self):
        """Test planning data processing workflow"""
        planner = SemanticPlanner()
        intent = {
            "intent": "process_data",
            "parameters": {"dataset": "test", "save": True}
        }

        tasks = planner.plan(intent)

        # Should have load, transform, validate, save
        assert len(tasks) == 4
        assert tasks[0]["task"] == "load_data"
        assert tasks[-1]["task"] == "save_data"

    def test_plan_unsupported_intent(self):
        """Test planning with unsupported intent"""
        planner = SemanticPlanner()
        intent = {
            "intent": "unsupported_action",
            "parameters": {}
        }

        try:
            planner.plan(intent)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unsupported intent" in str(e)

    def test_task_structure(self):
        """Test that planned tasks have correct structure"""
        planner = SemanticPlanner()
        intent = {
            "intent": "compute",
            "parameters": {}
        }

        tasks = planner.plan(intent)

        for task in tasks:
            assert "task" in task
            assert "priority" in task
            assert "metadata" in task
            assert isinstance(task["priority"], int)
            assert isinstance(task["metadata"], dict)


class TestPolicyEngine:
    """Tests for PolicyEngine"""

    def test_policy_engine_creation(self):
        """Test policy engine initialization"""
        engine = create_policy_engine()
        assert engine is not None
        assert isinstance(engine, PolicyEngine)

    def test_apply_policies_to_tasks(self):
        """Test applying policies to task list"""
        engine = PolicyEngine()
        tasks = [
            {"task": "test1", "priority": 5, "metadata": {"task_type": "generic"}},
            {"task": "test2", "priority": 12, "metadata": {"task_type": "generic"}},  # Too high
        ]

        modified = engine.apply_policies(tasks)

        assert len(modified) == 2
        # Priority should be clamped to max (10)
        assert modified[1]["priority"] == 10

    def test_priority_clamping(self):
        """Test that priorities are clamped to valid range"""
        engine = PolicyEngine()
        tasks = [
            {"task": "low", "priority": -5, "metadata": {"task_type": "generic"}},
            {"task": "high", "priority": 20, "metadata": {"task_type": "generic"}},
        ]

        modified = engine.apply_policies(tasks)

        assert modified[0]["priority"] == 0  # Clamped to min
        assert modified[1]["priority"] == 10  # Clamped to max

    def test_heavy_task_limit(self):
        """Test heavy task limiting"""
        engine = PolicyEngine(max_parallel_heavy=2)
        tasks = [
            {"task": "heavy1", "priority": 9, "metadata": {"task_type": "computation"}},
            {"task": "heavy2", "priority": 9, "metadata": {"task_type": "inference"}},
            {"task": "heavy3", "priority": 9, "metadata": {"task_type": "computation"}},
        ]

        modified = engine.apply_policies(tasks)

        # Third heavy task should have reduced priority
        assert modified[2]["priority"] < modified[0]["priority"]

    def test_retry_policy_injection(self):
        """Test that retry policy is injected"""
        engine = PolicyEngine()
        tasks = [
            {"task": "test", "priority": 8, "metadata": {"task_type": "generic"}},
        ]

        modified = engine.apply_policies(tasks)

        assert "retry_count" in modified[0]
        assert "retry_on_error" in modified[0]
        assert modified[0]["retry_on_error"] is True  # Priority >= 8

    def test_validate_submission_valid(self):
        """Test validation of valid task"""
        engine = PolicyEngine()
        task = {
            "task": "test",
            "priority": 5,
            "metadata": {"task_type": "generic"}
        }

        # Should not raise
        engine.validate_submission(task)

    def test_validate_submission_invalid_priority(self):
        """Test validation rejects invalid priority"""
        engine = PolicyEngine()
        task = {
            "task": "test",
            "priority": 15,  # Too high
            "metadata": {"task_type": "generic"}
        }

        try:
            engine.validate_submission(task)
            assert False, "Should have raised RejectedTaskError"
        except RejectedTaskError:
            pass

    def test_validate_submission_missing_metadata(self):
        """Test validation rejects task without metadata"""
        engine = PolicyEngine()
        task = {
            "task": "test",
            "priority": 5,
            "metadata": {}  # Empty metadata
        }

        try:
            engine.validate_submission(task)
            assert False, "Should have raised RejectedTaskError"
        except RejectedTaskError:
            pass

    def test_get_policy_status(self):
        """Test getting policy status"""
        engine = PolicyEngine(max_parallel_heavy=3)
        status = engine.get_policy_status()

        assert "max_parallel_heavy" in status
        assert status["max_parallel_heavy"] == 3
        assert "current_heavy_tasks" in status
        assert "priority_range" in status


class TestActionMapper:
    """Tests for ActionMapper (with mocked orchestrator)"""

    def test_mapper_creation(self):
        """Test mapper initialization"""
        # Mock orchestrator
        mock_orch = Mock()
        mock_orch._is_running = True

        mapper = create_action_mapper(orchestrator=mock_orch)
        assert mapper is not None
        assert isinstance(mapper, ActionMapper)

    async def test_map_and_submit_single_task(self):
        """Test mapping and submitting a single task"""
        # Mock orchestrator
        mock_orch = Mock()
        mock_orch._is_running = True
        mock_orch.submit_task = Mock(return_value="test-task-id")

        mapper = ActionMapper(orchestrator=mock_orch)

        tasks = [
            {"task": "compute", "priority": 5, "metadata": {"task_type": "computation"}}
        ]

        task_ids = await mapper.map_and_submit(tasks)

        assert len(task_ids) == 1
        assert task_ids[0] == "test-task-id"
        assert mock_orch.submit_task.called

    async def test_map_and_submit_multiple_tasks(self):
        """Test mapping and submitting multiple tasks"""
        # Mock orchestrator
        mock_orch = Mock()
        mock_orch._is_running = True
        mock_orch.submit_task = Mock(side_effect=["id1", "id2", "id3"])

        mapper = ActionMapper(orchestrator=mock_orch)

        tasks = [
            {"task": "fetch_data", "priority": 7, "metadata": {"task_type": "data_fetch"}},
            {"task": "compute_sentiment", "priority": 8, "metadata": {"task_type": "computation"}},
            {"task": "generate_plot", "priority": 5, "metadata": {"task_type": "visualization"}},
        ]

        task_ids = await mapper.map_and_submit(tasks)

        assert len(task_ids) == 3
        assert mock_orch.submit_task.call_count == 3

    async def test_map_and_submit_empty_list(self):
        """Test mapping with empty task list"""
        mock_orch = Mock()
        mock_orch._is_running = True

        mapper = ActionMapper(orchestrator=mock_orch)
        task_ids = await mapper.map_and_submit([])

        assert len(task_ids) == 0

    async def test_map_and_submit_orchestrator_not_running(self):
        """Test that error is raised if orchestrator not running"""
        mock_orch = Mock()
        mock_orch._is_running = False

        mapper = ActionMapper(orchestrator=mock_orch)

        tasks = [{"task": "test", "priority": 5, "metadata": {"task_type": "generic"}}]

        try:
            await mapper.map_and_submit(tasks)
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "not running" in str(e)


class TestActionLayer:
    """Tests for ActionLayer (full pipeline)"""

    def test_action_layer_creation(self):
        """Test action layer initialization"""
        layer = create_action_layer()
        assert layer is not None
        assert isinstance(layer, ActionLayer)

    def test_get_action_layer_singleton(self):
        """Test singleton pattern"""
        layer1 = get_action_layer()
        layer2 = get_action_layer()
        assert layer1 is layer2

    async def test_execute_command_success(self):
        """Test successful command execution"""
        # Create mocks
        mock_orch = Mock()
        mock_orch._is_running = True
        mock_orch.submit_task = Mock(side_effect=["id1", "id2", "id3", "id4"])

        # Create action layer with mocked components
        layer = ActionLayer(mapper=ActionMapper(orchestrator=mock_orch))

        # Execute command
        result = await layer.execute_command("analyze sentiment count=100 with plot")

        assert result["status"] == "ok"
        assert result["intent"] == "analyze_sentiment"
        assert "tasks_submitted" in result
        assert result["count"] == 4

    async def test_execute_command_invalid_command(self):
        """Test command execution with invalid command"""
        layer = ActionLayer()

        result = await layer.execute_command("invalid nonsense xyz")

        assert result["status"] == "error"
        assert result["error_type"] == "validation_error"
        assert "message" in result

    async def test_execute_command_empty_command(self):
        """Test command execution with empty command"""
        layer = ActionLayer()

        result = await layer.execute_command("")

        assert result["status"] == "error"
        assert "message" in result

    async def test_execute_batch_commands(self):
        """Test batch command execution"""
        # Create mocks
        mock_orch = Mock()
        mock_orch._is_running = True
        mock_orch.submit_task = Mock(return_value="test-id")

        layer = ActionLayer(mapper=ActionMapper(orchestrator=mock_orch))

        commands = [
            "analyze sentiment",
            "generate plot",
            "compute statistics"
        ]

        result = await layer.execute_batch(commands)

        assert result["status"] == "batch_complete"
        assert result["total_commands"] == 3
        assert "successful" in result
        assert "results" in result

    def test_get_status(self):
        """Test getting action layer status"""
        layer = ActionLayer()
        status = layer.get_status()

        assert "action_layer" in status
        assert "parser_intents" in status
        assert "policy_status" in status
        assert "components" in status

    def test_validate_command_valid(self):
        """Test validating a valid command"""
        layer = ActionLayer()
        result = layer.validate_command("analyze sentiment count=200")

        assert result["valid"] is True
        assert result["intent"] == "analyze_sentiment"
        assert result["planned_tasks"] > 0

    def test_validate_command_invalid(self):
        """Test validating an invalid command"""
        layer = ActionLayer()
        result = layer.validate_command("invalid nonsense")

        assert result["valid"] is False
        assert "message" in result


async def run_async_tests():
    """Run all async tests"""
    print("\n" + "="*70)
    print("Running ActionMapper Tests")
    print("="*70)

    test_mapper = TestActionMapper()
    await test_mapper.test_map_and_submit_single_task()
    print("✓ Map and submit single task")

    await test_mapper.test_map_and_submit_multiple_tasks()
    print("✓ Map and submit multiple tasks")

    await test_mapper.test_map_and_submit_empty_list()
    print("✓ Map and submit empty list")

    await test_mapper.test_map_and_submit_orchestrator_not_running()
    print("✓ Orchestrator not running error")

    print("\n" + "="*70)
    print("Running ActionLayer Tests (Full Pipeline)")
    print("="*70)

    test_layer = TestActionLayer()

    await test_layer.test_execute_command_success()
    print("✓ Execute command successfully")

    await test_layer.test_execute_command_invalid_command()
    print("✓ Handle invalid command")

    await test_layer.test_execute_command_empty_command()
    print("✓ Handle empty command")

    await test_layer.test_execute_batch_commands()
    print("✓ Execute batch commands")


def run_sync_tests():
    """Run all synchronous tests"""
    print("="*70)
    print("FAZA 26 - Intelligent Action Layer - Test Suite")
    print("="*70)

    # IntentParser tests
    print("\n" + "="*70)
    print("Running IntentParser Tests")
    print("="*70)

    test_parser = TestIntentParser()
    test_parser.test_parser_creation()
    print("✓ Parser creation")

    test_parser.test_parse_sentiment_command()
    print("✓ Parse sentiment command")

    test_parser.test_parse_compute_command()
    print("✓ Parse compute command")

    test_parser.test_parse_plot_command()
    print("✓ Parse plot command")

    test_parser.test_parse_invalid_command()
    print("✓ Invalid command handling")

    test_parser.test_parse_empty_command()
    print("✓ Empty command handling")

    test_parser.test_validate_valid_intent()
    print("✓ Validate valid intent")

    test_parser.test_validate_invalid_intent()
    print("✓ Validate invalid intent")

    test_parser.test_get_supported_intents()
    print("✓ Get supported intents")

    # SemanticPlanner tests
    print("\n" + "="*70)
    print("Running SemanticPlanner Tests")
    print("="*70)

    test_planner = TestSemanticPlanner()
    test_planner.test_planner_creation()
    print("✓ Planner creation")

    test_planner.test_plan_sentiment_analysis()
    print("✓ Plan sentiment analysis")

    test_planner.test_plan_sentiment_without_plot()
    print("✓ Plan sentiment without plot")

    test_planner.test_plan_compute()
    print("✓ Plan compute task")

    test_planner.test_plan_data_processing()
    print("✓ Plan data processing")

    test_planner.test_plan_unsupported_intent()
    print("✓ Unsupported intent handling")

    test_planner.test_task_structure()
    print("✓ Task structure validation")

    # PolicyEngine tests
    print("\n" + "="*70)
    print("Running PolicyEngine Tests")
    print("="*70)

    test_policy = TestPolicyEngine()
    test_policy.test_policy_engine_creation()
    print("✓ Policy engine creation")

    test_policy.test_apply_policies_to_tasks()
    print("✓ Apply policies to tasks")

    test_policy.test_priority_clamping()
    print("✓ Priority clamping")

    test_policy.test_heavy_task_limit()
    print("✓ Heavy task limiting")

    test_policy.test_retry_policy_injection()
    print("✓ Retry policy injection")

    test_policy.test_validate_submission_valid()
    print("✓ Validate valid submission")

    test_policy.test_validate_submission_invalid_priority()
    print("✓ Reject invalid priority")

    test_policy.test_validate_submission_missing_metadata()
    print("✓ Reject missing metadata")

    test_policy.test_get_policy_status()
    print("✓ Get policy status")

    # ActionLayer sync tests
    print("\n" + "="*70)
    print("Running ActionLayer Sync Tests")
    print("="*70)

    test_layer = TestActionLayer()
    test_layer.test_action_layer_creation()
    print("✓ Action layer creation")

    test_layer.test_get_action_layer_singleton()
    print("✓ Singleton pattern")

    test_layer.test_get_status()
    print("✓ Get status")

    test_layer.test_validate_command_valid()
    print("✓ Validate valid command")

    test_layer.test_validate_command_invalid()
    print("✓ Validate invalid command")


if __name__ == "__main__":
    # Run synchronous tests
    run_sync_tests()

    # Run asynchronous tests
    asyncio.run(run_async_tests())

    print("\n" + "="*70)
    print("✓ ALL TESTS PASSED")
    print("="*70)
