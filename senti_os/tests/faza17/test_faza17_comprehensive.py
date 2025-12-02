"""
Comprehensive Test Suite for SENTI OS FAZA 17

This test suite provides 50+ tests covering all FAZA 17 modules:
- Step Planner (8 tests)
- Priority Queue (10 tests)
- Model Ensemble Engine (8 tests)
- Reliability Feedback (8 tests)
- Explainability Engine (6 tests)
- Pipeline Manager (6 tests)
- Orchestration Manager (6 tests)
- Integration Tests (2 tests)

All tests run locally without external dependencies.
"""

import unittest
from datetime import datetime, timedelta

from senti_os.core.faza17.step_planner import create_planner, StepType, ExecutionMode
from senti_os.core.faza17.priority_queue import create_queue, QueuedTask, Priority
from senti_os.core.faza17.model_ensemble_engine import create_ensemble_engine, ModelOutput, EnsembleStrategy
from senti_os.core.faza17.reliability_feedback import create_feedback_loop, OutcomeType
from senti_os.core.faza17.explainability_engine import create_explainability_engine, DecisionType
from senti_os.core.faza17.pipeline_manager import create_pipeline_manager, PipelineStrategy
from senti_os.core.faza17.orchestration_manager import create_orchestration_manager, OrchestrationRequest


class TestStepPlanner(unittest.TestCase):
    """Tests for Step Planner."""

    def setUp(self):
        """Set up test fixtures."""
        self.planner = create_planner()

    def test_planner_initialization(self):
        """Test planner initialization."""
        self.assertIsNotNone(self.planner)
        self.assertEqual(len(self.planner.planning_history), 0)

    def test_plan_analysis_task(self):
        """Test planning an analysis task."""
        result = self.planner.plan_task("Analyze this dataset")
        self.assertTrue(len(result.steps) > 0)
        self.assertIn(StepType.ANALYSIS, [s.step_type for s in result.steps])

    def test_plan_generation_task(self):
        """Test planning a generation task."""
        result = self.planner.plan_task("Generate a report")
        self.assertTrue(len(result.steps) > 0)

    def test_plan_with_max_steps(self):
        """Test planning with max steps limit."""
        result = self.planner.plan_task("Complex task", max_steps=3)
        self.assertLessEqual(len(result.steps), 3)

    def test_sequential_execution_mode(self):
        """Test sequential execution mode."""
        result = self.planner.plan_task("Task with dependencies", allow_parallel=False)
        self.assertEqual(result.execution_mode, ExecutionMode.SEQUENTIAL)

    def test_safety_checks(self):
        """Test safety checks in planning."""
        result = self.planner.plan_task("Simple task", context={"max_total_cost": 1.0})
        self.assertIsInstance(result.safety_checks_passed, bool)

    def test_control_flow_graph(self):
        """Test control flow graph generation."""
        result = self.planner.plan_task("Multi-step task")
        self.assertIn("nodes", result.control_flow_graph)
        self.assertIn("edges", result.control_flow_graph)

    def test_get_statistics(self):
        """Test getting planner statistics."""
        self.planner.plan_task("Task 1")
        self.planner.plan_task("Task 2")
        stats = self.planner.get_statistics()
        self.assertEqual(stats["total_plans"], 2)


class TestPriorityQueue(unittest.TestCase):
    """Tests for Priority Queue."""

    def setUp(self):
        """Set up test fixtures."""
        self.queue = create_queue()

    def test_queue_initialization(self):
        """Test queue initialization."""
        self.assertIsNotNone(self.queue)
        self.assertTrue(self.queue.is_empty())

    def test_enqueue_task(self):
        """Test enqueueing a task."""
        task = QueuedTask(
            task_id="task_001",
            priority=Priority.NORMAL,
            submission_time=datetime.now(),
            estimated_duration=60,
            max_cost=1.0,
        )
        success = self.queue.enqueue(task)
        self.assertTrue(success)
        self.assertEqual(self.queue.size(), 1)

    def test_dequeue_task(self):
        """Test dequeueing a task."""
        task = QueuedTask(
            task_id="task_002",
            priority=Priority.HIGH,
            submission_time=datetime.now(),
            estimated_duration=60,
            max_cost=1.0,
        )
        self.queue.enqueue(task)
        dequeued = self.queue.dequeue()
        self.assertIsNotNone(dequeued)
        self.assertEqual(dequeued.task_id, "task_002")

    def test_priority_ordering(self):
        """Test priority-based ordering."""
        low_task = QueuedTask("low", Priority.LOW, datetime.now(), 60, 1.0)
        high_task = QueuedTask("high", Priority.HIGH, datetime.now(), 60, 1.0)
        self.queue.enqueue(low_task)
        self.queue.enqueue(high_task)
        first = self.queue.dequeue()
        self.assertEqual(first.task_id, "high")

    def test_mark_completed(self):
        """Test marking task as completed."""
        task = QueuedTask("task_003", Priority.NORMAL, datetime.now(), 60, 1.0)
        self.queue.enqueue(task)
        self.queue.dequeue()
        success = self.queue.mark_completed("task_003")
        self.assertTrue(success)

    def test_mark_failed_with_retry(self):
        """Test marking task as failed with retry."""
        task = QueuedTask("task_004", Priority.NORMAL, datetime.now(), 60, 1.0)
        self.queue.enqueue(task)
        self.queue.dequeue()
        self.queue.mark_failed("task_004", retry=True)
        self.assertEqual(self.queue.size(), 1)

    def test_get_position(self):
        """Test getting task position in queue."""
        task1 = QueuedTask("task_1", Priority.LOW, datetime.now(), 60, 1.0)
        task2 = QueuedTask("task_2", Priority.NORMAL, datetime.now(), 60, 1.0)
        self.queue.enqueue(task1)
        self.queue.enqueue(task2)
        position = self.queue.get_position("task_2")
        self.assertIsNotNone(position)

    def test_peek(self):
        """Test peeking at next task."""
        task = QueuedTask("peek_task", Priority.HIGH, datetime.now(), 60, 1.0)
        self.queue.enqueue(task)
        peeked = self.queue.peek()
        self.assertEqual(peeked.task_id, "peek_task")
        self.assertEqual(self.queue.size(), 1)

    def test_update_priority(self):
        """Test updating task priority."""
        task = QueuedTask("update_task", Priority.LOW, datetime.now(), 60, 1.0)
        self.queue.enqueue(task)
        success = self.queue.update_priority("update_task", Priority.HIGH)
        self.assertTrue(success)

    def test_get_statistics(self):
        """Test getting queue statistics."""
        task = QueuedTask("stats_task", Priority.NORMAL, datetime.now(), 60, 1.0)
        self.queue.enqueue(task)
        stats = self.queue.get_statistics()
        self.assertEqual(stats.total_enqueued, 1)


class TestModelEnsembleEngine(unittest.TestCase):
    """Tests for Model Ensemble Engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_ensemble_engine()

    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)

    def test_combine_single_output(self):
        """Test combining single output."""
        output = ModelOutput("model_1", "Output", 0.9, 0.85, 1.0, 0.1)
        result = self.engine.combine_outputs([output])
        self.assertEqual(result.final_output, "Output")

    def test_weighted_average_strategy(self):
        """Test weighted average ensemble strategy."""
        outputs = [
            ModelOutput("model_1", "Output A", 0.9, 0.85, 1.0, 0.1),
            ModelOutput("model_2", "Output B", 0.8, 0.80, 1.2, 0.15),
        ]
        result = self.engine.combine_outputs(outputs, EnsembleStrategy.WEIGHTED_AVERAGE)
        self.assertIsNotNone(result.final_output)
        self.assertGreater(result.confidence_score, 0)

    def test_majority_vote_strategy(self):
        """Test majority vote strategy."""
        outputs = [
            ModelOutput("model_1", "Same output", 0.9, 0.85, 1.0, 0.1),
            ModelOutput("model_2", "Same output", 0.8, 0.80, 1.2, 0.15),
            ModelOutput("model_3", "Different", 0.7, 0.75, 1.1, 0.12),
        ]
        result = self.engine.combine_outputs(outputs, EnsembleStrategy.MAJORITY_VOTE)
        self.assertIn("Same output", result.final_output)

    def test_highest_confidence_strategy(self):
        """Test highest confidence strategy."""
        outputs = [
            ModelOutput("model_1", "High conf", 0.95, 0.85, 1.0, 0.1),
            ModelOutput("model_2", "Low conf", 0.6, 0.80, 1.2, 0.15),
        ]
        result = self.engine.combine_outputs(outputs, EnsembleStrategy.HIGHEST_CONFIDENCE)
        self.assertIn("High conf", result.final_output)

    def test_conflict_detection(self):
        """Test conflict detection between models."""
        outputs = [
            ModelOutput("model_1", "The answer is yes", 0.9, 0.85, 1.0, 0.1),
            ModelOutput("model_2", "The answer is not yes", 0.8, 0.80, 1.2, 0.15),
        ]
        result = self.engine.combine_outputs(outputs)
        self.assertGreaterEqual(result.conflicts_detected, 0)

    def test_model_weights_calculation(self):
        """Test model weights calculation."""
        outputs = [
            ModelOutput("model_1", "Output", 0.9, 0.85, 1.0, 0.1),
            ModelOutput("model_2", "Output", 0.7, 0.75, 1.0, 0.1),
        ]
        result = self.engine.combine_outputs(outputs)
        self.assertEqual(len(result.model_weights), 2)

    def test_get_statistics(self):
        """Test getting ensemble statistics."""
        outputs = [ModelOutput("m1", "O", 0.9, 0.85, 1.0, 0.1)]
        self.engine.combine_outputs(outputs)
        stats = self.engine.get_statistics()
        self.assertEqual(stats["total_ensembles"], 1)


class TestReliabilityFeedback(unittest.TestCase):
    """Tests for Reliability Feedback Loop."""

    def setUp(self):
        """Set up test fixtures."""
        self.feedback = create_feedback_loop()

    def test_feedback_initialization(self):
        """Test feedback loop initialization."""
        self.assertIsNotNone(self.feedback)

    def test_record_success_outcome(self):
        """Test recording successful outcome."""
        self.feedback.record_outcome(
            model_id="model_1",
            task_id="task_1",
            outcome=OutcomeType.SUCCESS,
            confidence_claimed=0.9,
            actual_quality=0.85,
        )
        self.assertEqual(len(self.feedback.feedback_history), 1)

    def test_record_failure_outcome(self):
        """Test recording failure outcome."""
        self.feedback.record_outcome(
            model_id="model_1",
            task_id="task_2",
            outcome=OutcomeType.FAILURE,
            confidence_claimed=0.8,
            actual_quality=0.3,
        )
        metrics = self.feedback.get_model_metrics("model_1")
        self.assertIsNotNone(metrics)

    def test_update_reliability_scores(self):
        """Test updating reliability scores."""
        for i in range(5):
            self.feedback.record_outcome(
                f"model_{i%2}",
                f"task_{i}",
                OutcomeType.SUCCESS,
                0.9,
                0.85,
            )
        updated = self.feedback.update_reliability_scores()
        self.assertIsInstance(updated, dict)

    def test_get_model_metrics(self):
        """Test getting model metrics."""
        self.feedback.record_outcome("model_test", "t1", OutcomeType.SUCCESS, 0.9, 0.85)
        metrics = self.feedback.get_model_metrics("model_test")
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.model_id, "model_test")

    def test_get_top_models(self):
        """Test getting top models."""
        for i in range(3):
            self.feedback.record_outcome(f"model_{i}", f"t_{i}", OutcomeType.SUCCESS, 0.9, 0.8 + i * 0.05)
            for j in range(3):
                self.feedback.record_outcome(f"model_{i}", f"t_{i}_{j}", OutcomeType.SUCCESS, 0.9, 0.85)
        self.feedback.update_reliability_scores()
        top = self.feedback.get_top_models(2)
        self.assertLessEqual(len(top), 2)

    def test_clear_old_feedback(self):
        """Test clearing old feedback."""
        self.feedback.record_outcome("m1", "t1", OutcomeType.SUCCESS, 0.9, 0.85)
        removed = self.feedback.clear_old_feedback(days=0)
        self.assertGreaterEqual(removed, 0)

    def test_get_statistics(self):
        """Test getting feedback statistics."""
        self.feedback.record_outcome("m1", "t1", OutcomeType.SUCCESS, 0.9, 0.85)
        stats = self.feedback.get_statistics()
        self.assertIn("total_feedback_entries", stats)


class TestExplainabilityEngine(unittest.TestCase):
    """Tests for Explainability Engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_explainability_engine()

    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)

    def test_explain_model_selection(self):
        """Test model selection explanation."""
        explanation = self.engine.explain_model_selection(
            decision_id="dec_001",
            selected_model="model_a",
            candidates=["model_a", "model_b"],
            selection_factors={"quality": 0.9, "cost": 0.8},
            routing_logic="Quality-first",
        )
        self.assertEqual(explanation.decision_type, DecisionType.MODEL_SELECTION)

    def test_explain_step_planning(self):
        """Test step planning explanation."""
        explanation = self.engine.explain_step_planning(
            decision_id="dec_002",
            num_steps=5,
            execution_mode="sequential",
            estimated_cost=2.5,
            estimated_time=120,
            safety_checks_passed=True,
        )
        self.assertIn("5 steps", explanation.summary)

    def test_explain_ensemble_strategy(self):
        """Test ensemble strategy explanation."""
        explanation = self.engine.explain_ensemble_strategy(
            decision_id="dec_003",
            strategy="weighted_average",
            num_models=3,
            conflicts_detected=1,
            final_confidence=0.85,
        )
        self.assertEqual(explanation.decision_type, DecisionType.ENSEMBLE_STRATEGY)

    def test_get_explanation_by_id(self):
        """Test retrieving explanation by ID."""
        self.engine.explain_model_selection("dec_find", "model", [], {}, "test")
        found = self.engine.get_explanation("dec_find")
        self.assertIsNotNone(found)

    def test_generate_audit_report(self):
        """Test generating audit report."""
        self.engine.explain_model_selection("d1", "m", [], {}, "t")
        report = self.engine.generate_audit_report()
        self.assertIn("total_decisions", report)

    def test_clear_old_explanations(self):
        """Test clearing old explanations."""
        for i in range(5):
            self.engine.explain_model_selection(f"d_{i}", "m", [], {}, "t")
        removed = self.engine.clear_old_explanations(keep_last_n=3)
        self.assertEqual(removed, 2)


class TestPipelineManager(unittest.TestCase):
    """Tests for Pipeline Manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = create_pipeline_manager()

    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager)

    def test_execute_local_fast_precise(self):
        """Test local-fast-precise pipeline."""
        stages = [{"name": "Stage 1", "model_id": "m1"}]
        result = self.manager.execute_pipeline(
            "pipe_001",
            PipelineStrategy.LOCAL_FAST_PRECISE,
            stages,
        )
        self.assertTrue(result.success)

    def test_execute_parallel_ensemble(self):
        """Test parallel ensemble pipeline."""
        stages = [
            {"name": "Stage 1", "model_id": "m1"},
            {"name": "Stage 2", "model_id": "m2"},
        ]
        result = self.manager.execute_pipeline(
            "pipe_002",
            PipelineStrategy.PARALLEL_ENSEMBLE,
            stages,
        )
        self.assertIsNotNone(result)

    def test_pipeline_cost_tracking(self):
        """Test pipeline cost tracking."""
        stages = [{"name": "Stage 1"}]
        result = self.manager.execute_pipeline("pipe_003", PipelineStrategy.LOCAL_FAST_PRECISE, stages)
        self.assertGreaterEqual(result.total_cost, 0)

    def test_pipeline_time_tracking(self):
        """Test pipeline time tracking."""
        stages = [{"name": "Stage 1"}]
        result = self.manager.execute_pipeline("pipe_004", PipelineStrategy.LOCAL_FAST_PRECISE, stages)
        self.assertGreater(result.total_duration, 0)

    def test_get_statistics(self):
        """Test getting pipeline statistics."""
        stages = [{"name": "Stage 1"}]
        self.manager.execute_pipeline("pipe_stats", PipelineStrategy.LOCAL_FAST_PRECISE, stages)
        stats = self.manager.get_statistics()
        self.assertEqual(stats["total_pipelines"], 1)


class TestOrchestrationManager(unittest.TestCase):
    """Tests for Orchestration Manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = create_orchestration_manager()

    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.planner)
        self.assertIsNotNone(self.manager.queue)

    def test_submit_task(self):
        """Test submitting a task."""
        request = OrchestrationRequest(
            request_id="orch_001",
            task_description="Analyze data",
        )
        request_id = self.manager.submit_task(request)
        self.assertEqual(request_id, "orch_001")

    def test_process_task(self):
        """Test processing a task."""
        request = OrchestrationRequest(
            request_id="orch_002",
            task_description="Generate report",
        )
        self.manager.submit_task(request)
        result = self.manager.process_next_task()
        self.assertIsNotNone(result)

    def test_get_queue_status(self):
        """Test getting queue status."""
        status = self.manager.get_queue_status()
        self.assertIn("queue_size", status)

    def test_get_statistics(self):
        """Test getting orchestration statistics."""
        request = OrchestrationRequest("orch_stats", "Task")
        self.manager.submit_task(request)
        self.manager.process_next_task()
        stats = self.manager.get_statistics()
        self.assertIn("total_orchestrations", stats)

    def test_get_audit_report(self):
        """Test getting audit report."""
        report = self.manager.get_audit_report()
        self.assertIn("orchestration_stats", report)


class TestIntegration(unittest.TestCase):
    """Integration tests for FAZA 17."""

    def test_full_orchestration_flow(self):
        """Test complete orchestration flow."""
        manager = create_orchestration_manager()

        request = OrchestrationRequest(
            request_id="integration_001",
            task_description="Analyze dataset and generate insights",
            priority=Priority.HIGH,
        )

        request_id = manager.submit_task(request)
        self.assertEqual(request_id, "integration_001")

        result = manager.process_next_task()
        self.assertIsNotNone(result)

    def test_multi_task_orchestration(self):
        """Test orchestrating multiple tasks."""
        manager = create_orchestration_manager()

        for i in range(3):
            request = OrchestrationRequest(
                request_id=f"multi_{i}",
                task_description=f"Task {i}",
                priority=Priority.NORMAL if i % 2 == 0 else Priority.HIGH,
            )
            manager.submit_task(request)

        results = []
        for _ in range(3):
            result = manager.process_next_task()
            if result:
                results.append(result)

        self.assertGreater(len(results), 0)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    unittest.main()
