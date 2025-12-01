"""
FAZA 15 - Strategy Engine Comprehensive Tests

Tests for:
- StrategyEngine (goal decomposition, planning, optimization)
- ReasoningEngine (chain-of-thought, decision trees, simulation)
- StrategyManager (orchestration, validation, events)
- StrategyRules (security validation, constraints)
- OptimizerService (periodic optimization)
- Plan Templates (data structures)
- Strategy Events (event emission)
"""

import unittest
import time
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from senti_core_module.senti_strategy import (
    StrategyEngine,
    ReasoningEngine,
    StrategyManager,
    StrategyRules,
    OptimizerService,
    HighLevelPlan,
    MidLevelStep,
    AtomicAction,
    ActionPriority,
    ActionStatus,
    StrategyTemplate,
    StrategyEvent,
    StrategyCreatedEvent,
    StrategyOptimizedEvent,
    StrategyRejectedEvent,
    HighRiskStrategyEvent,
    StrategyExecutedEvent,
    StrategySimulationEvent,
    STRATEGY_CREATED,
    STRATEGY_OPTIMIZED,
    STRATEGY_REJECTED,
    HIGH_RISK_STRATEGY,
    STRATEGY_EXECUTED,
    STRATEGY_SIMULATION_RESULT
)


# =============================================================================
# Mock Memory Manager
# =============================================================================

class MockMemoryManager:
    """Mock FAZA 12 Memory Manager"""

    def __init__(self):
        self.episodic_memory = MockEpisodicMemory()
        self.semantic_memory = MockSemanticMemory()
        self.working_memory = MockWorkingMemory()


class MockEpisodicMemory:
    """Mock episodic memory"""

    def __init__(self):
        self.events = []

    def store(self, event_type, data, tags=None):
        self.events.append({
            "event_type": event_type,
            "data": data,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat()
        })

    def query(self, event_type=None, tags=None, limit=10):
        results = self.events
        if event_type:
            results = [e for e in results if e["event_type"] == event_type]
        if tags:
            results = [e for e in results if any(tag in e["tags"] for tag in tags)]
        return results[-limit:]


class MockSemanticMemory:
    """Mock semantic memory"""

    def __init__(self):
        self.concepts = {}

    def store_concept(self, concept, data):
        self.concepts[concept] = data

    def get_concept(self, concept):
        return self.concepts.get(concept, {})


class MockWorkingMemory:
    """Mock working memory"""

    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def get_all(self):
        return self.data.copy()


# =============================================================================
# Mock Prediction Manager
# =============================================================================

class MockPredictionManager:
    """Mock FAZA 13 Prediction Manager"""

    def __init__(self):
        self.predictions = []

    def predict_state(self, context):
        prediction = {
            "prediction": "System stable",
            "confidence": 0.8,
            "risk_score": 20
        }
        self.predictions.append(prediction)
        return prediction

    def predict_failure(self):
        return {
            "prediction": "No failures expected",
            "confidence": 0.9,
            "risk_score": 10
        }


# =============================================================================
# Mock Anomaly Manager
# =============================================================================

class MockAnomalyManager:
    """Mock FAZA 14 Anomaly Manager"""

    def __init__(self):
        self.detections = []

    def detect_for(self, component, context):
        detection = {
            "score": 0,
            "severity": "LOW",
            "reason": "No anomalies"
        }
        self.detections.append(detection)
        return Mock(
            score=detection["score"],
            severity=detection["severity"],
            reason=detection["reason"]
        )


# =============================================================================
# Mock Security Manager
# =============================================================================

class MockSecurityManager:
    """Mock FAZA 8 Security Manager"""

    def __init__(self):
        self.checks = []

    def check_permission(self, operation, context):
        self.checks.append({"operation": operation, "context": context})
        return True  # Allow by default


# =============================================================================
# Mock EventBus
# =============================================================================

class MockEventBus:
    """Mock EventBus"""

    def __init__(self):
        self.events = []

    def emit(self, event_type, data):
        self.events.append({"type": event_type, "data": data})


# =============================================================================
# Plan Template Tests
# =============================================================================

class TestPlanTemplate(unittest.TestCase):
    """Test plan template structures"""

    def test_atomic_action_creation(self):
        """Test AtomicAction creation"""
        action = AtomicAction(
            action_id="act_001",
            name="Test Action",
            description="Test description",
            action_type="analysis",
            parameters={},
            priority=ActionPriority.HIGH,
            estimated_duration=10
        )

        self.assertEqual(action.action_id, "act_001")
        self.assertEqual(action.name, "Test Action")
        self.assertEqual(action.priority, ActionPriority.HIGH)
        self.assertEqual(action.status, ActionStatus.PENDING)

    def test_atomic_action_serialization(self):
        """Test AtomicAction to_dict"""
        action = AtomicAction(
            action_id="act_001",
            name="Test",
            description="Test",
            action_type="analysis",
            parameters={},
            priority=ActionPriority.HIGH,
            estimated_duration=10
        )

        data = action.to_dict()
        self.assertIn("action_id", data)
        self.assertIn("name", data)
        self.assertIn("priority", data)
        self.assertEqual(data["action_id"], "act_001")

    def test_mid_level_step_creation(self):
        """Test MidLevelStep creation"""
        actions = [
            AtomicAction("a1", "Action 1", "Desc", "analysis", {}, ActionPriority.HIGH, 10),
            AtomicAction("a2", "Action 2", "Desc", "optimization", {}, ActionPriority.MEDIUM, 20)
        ]

        step = MidLevelStep(
            step_id="step_001",
            name="Test Step",
            description="Test step",
            actions=actions,
            success_criteria={}
        )

        self.assertEqual(step.step_id, "step_001")
        self.assertEqual(len(step.actions), 2)
        self.assertEqual(step.status, ActionStatus.PENDING)

    def test_high_level_plan_creation(self):
        """Test HighLevelPlan creation"""
        actions = [
            AtomicAction("a1", "Action 1", "Desc", "analysis", {}, ActionPriority.HIGH, 10)
        ]
        steps = [
            MidLevelStep("s1", "Step 1", "Desc", actions, {})
        ]

        plan = HighLevelPlan(
            plan_id="plan_001",
            objective="Test Objective",
            description="Test plan",
            steps=steps,
            risk_score=50,
            expected_outcome="Success",
            constraints=[],
            metadata={}
        )

        self.assertEqual(plan.plan_id, "plan_001")
        self.assertEqual(plan.objective, "Test Objective")
        self.assertEqual(plan.risk_score, 50)
        self.assertEqual(plan.get_total_steps(), 1)
        self.assertEqual(plan.get_total_actions(), 1)

    def test_strategy_template_empty_plan(self):
        """Test StrategyTemplate empty plan creation"""
        plan = StrategyTemplate.create_empty_plan("test_plan", "Test objective")

        self.assertIsInstance(plan, HighLevelPlan)
        self.assertEqual(plan.plan_id, "test_plan")
        self.assertEqual(plan.objective, "Test objective")
        self.assertEqual(plan.get_total_steps(), 0)


# =============================================================================
# Strategy Engine Tests
# =============================================================================

class TestStrategyEngine(unittest.TestCase):
    """Test StrategyEngine core logic"""

    def setUp(self):
        self.memory_manager = MockMemoryManager()
        self.prediction_manager = MockPredictionManager()
        self.anomaly_manager = MockAnomalyManager()

        self.engine = StrategyEngine(
            self.memory_manager,
            self.prediction_manager,
            self.anomaly_manager
        )

    def test_decompose_goal_basic(self):
        """Test basic goal decomposition"""
        sub_goals = self.engine.decompose_goal("Optimize system performance", {})

        self.assertIsInstance(sub_goals, list)
        self.assertGreater(len(sub_goals), 0)
        self.assertIn("Analyze current state", sub_goals)

    def test_decompose_goal_with_context(self):
        """Test goal decomposition with context"""
        context = {"target": "memory", "threshold": 80}
        sub_goals = self.engine.decompose_goal("Reduce resource usage", context)

        self.assertIsInstance(sub_goals, list)
        self.assertGreater(len(sub_goals), 0)

    def test_score_goal_basic(self):
        """Test goal scoring"""
        scores = self.engine.score_goal("Optimize system", {})

        self.assertIn("urgency", scores)
        self.assertIn("value", scores)
        self.assertIn("risk", scores)

        self.assertGreaterEqual(scores["urgency"], 0)
        self.assertLessEqual(scores["urgency"], 1.0)

    def test_generate_plan_basic(self):
        """Test basic plan generation"""
        plan = self.engine.generate_plan("Optimize performance", {})

        self.assertIsInstance(plan, HighLevelPlan)
        self.assertEqual(plan.objective, "Optimize performance")
        self.assertGreater(plan.get_total_steps(), 0)
        self.assertGreaterEqual(plan.risk_score, 0)
        self.assertLessEqual(plan.risk_score, 100)

    def test_generate_plan_with_context(self):
        """Test plan generation with context"""
        context = {"priority": "high", "component": "memory"}
        plan = self.engine.generate_plan("Fix memory leak", context)

        self.assertIsInstance(plan, HighLevelPlan)
        self.assertGreater(plan.get_total_steps(), 0)

    def test_refine_plan_basic(self):
        """Test plan refinement"""
        plan = self.engine.generate_plan("Optimize system", {})
        original_steps = plan.get_total_steps()

        refined_plan = self.engine.refine_plan(plan, {"simplify": True})

        self.assertIsInstance(refined_plan, HighLevelPlan)
        self.assertEqual(refined_plan.plan_id, plan.plan_id)
        # Refined plan should have same or fewer steps
        self.assertLessEqual(refined_plan.get_total_steps(), original_steps)

    def test_map_risk_basic(self):
        """Test risk mapping"""
        plan = self.engine.generate_plan("Test objective", {})
        risk_score = self.engine.map_risk(plan)

        self.assertIsInstance(risk_score, int)
        self.assertGreaterEqual(risk_score, 0)
        self.assertLessEqual(risk_score, 100)

    def test_detect_conflicts_no_conflicts(self):
        """Test conflict detection with no conflicts"""
        plan = self.engine.generate_plan("Test objective", {})
        conflicts = self.engine.detect_conflicts(plan)

        self.assertIsInstance(conflicts, list)

    def test_plan_statistics(self):
        """Test plan statistics tracking"""
        self.engine.generate_plan("Test 1", {})
        self.engine.generate_plan("Test 2", {})

        stats = self.engine.get_plan_stats()

        self.assertIn("total_plans", stats)
        self.assertEqual(stats["total_plans"], 2)


# =============================================================================
# Reasoning Engine Tests
# =============================================================================

class TestReasoningEngine(unittest.TestCase):
    """Test ReasoningEngine logic"""

    def setUp(self):
        self.memory_manager = MockMemoryManager()
        self.prediction_manager = MockPredictionManager()
        self.anomaly_manager = MockAnomalyManager()

        self.engine = ReasoningEngine(
            self.memory_manager,
            self.prediction_manager,
            self.anomaly_manager
        )

    def test_chain_of_thought_basic(self):
        """Test basic chain-of-thought reasoning"""
        steps = self.engine.chain_of_thought("Optimize memory usage", {})

        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0)
        self.assertTrue(any("Problem" in step for step in steps))

    def test_chain_of_thought_with_context(self):
        """Test chain-of-thought with context"""
        context = {"priority": "high", "component": "memory"}
        steps = self.engine.chain_of_thought("Fix memory leak", context)

        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 3)  # Should have multiple reasoning steps

    def test_build_decision_tree_basic(self):
        """Test decision tree building"""
        options = ["Option A", "Option B", "Option C"]
        weights = {"urgency": 0.5, "value": 0.3, "risk": 0.2}

        tree = self.engine.build_decision_tree(options, weights)

        self.assertIsInstance(tree, dict)
        self.assertIn("branches", tree)
        self.assertEqual(len(tree["branches"]), 3)

    def test_build_decision_tree_ranking(self):
        """Test decision tree ranking logic"""
        options = ["A", "B", "C"]
        weights = {"urgency": 1.0, "value": 0.0, "risk": 0.0}

        tree = self.engine.build_decision_tree(options, weights)

        # First option should have highest score
        branches = tree["branches"]
        self.assertGreater(branches[0]["total_score"], 0)

    def test_simulate_outcome_basic(self):
        """Test outcome simulation"""
        simulation = self.engine.simulate_outcome("Optimize system", {})

        self.assertIsInstance(simulation, dict)
        self.assertIn("action", simulation)
        self.assertIn("probability", simulation)
        self.assertIn("risks", simulation)

    def test_simulate_outcome_with_context(self):
        """Test outcome simulation with context"""
        context = {"current_state": "degraded", "target": "optimal"}
        simulation = self.engine.simulate_outcome("Improve performance", context)

        self.assertIsInstance(simulation, dict)
        self.assertIn("action", simulation)
        self.assertGreaterEqual(simulation["probability"], 0.0)
        self.assertLessEqual(simulation["probability"], 1.0)

    def test_reasoning_statistics(self):
        """Test reasoning statistics tracking"""
        self.engine.chain_of_thought("Problem 1", {})
        self.engine.chain_of_thought("Problem 2", {})

        stats = self.engine.get_reasoning_stats()

        self.assertIn("total_reasonings", stats)
        self.assertGreaterEqual(stats["total_reasonings"], 2)


# =============================================================================
# Strategy Rules Tests
# =============================================================================

class TestStrategyRules(unittest.TestCase):
    """Test StrategyRules validation"""

    def setUp(self):
        self.security_manager = MockSecurityManager()
        self.rules = StrategyRules(self.security_manager)

    def test_validate_plan_basic(self):
        """Test basic plan validation"""
        actions = [
            AtomicAction("a1", "Test", "Desc", "analysis", {}, ActionPriority.HIGH, 10)
        ]
        steps = [
            MidLevelStep("s1", "Step 1", "Desc", actions, {})
        ]
        plan = HighLevelPlan(
            "plan_001", "Test", "Description", steps, 50, "Success", [], {}
        )

        result = self.rules.validate_plan(plan)
        self.assertTrue(result)

    def test_validate_plan_too_many_steps(self):
        """Test plan validation with too many steps"""
        steps = []
        for i in range(25):  # Exceeds MAX_STEPS=20
            actions = [AtomicAction(f"a{i}", f"Action {i}", "D", "analysis", {}, ActionPriority.HIGH, 10)]
            steps.append(MidLevelStep(f"s{i}", f"Step {i}", "D", actions, {}))

        plan = HighLevelPlan("plan_001", "Test", "Desc", steps, 50, "Success", [], {})

        result = self.rules.validate_plan(plan)
        self.assertFalse(result)
        self.assertGreater(len(self.rules.get_violations()), 0)

    def test_validate_plan_forbidden_keyword(self):
        """Test plan validation with forbidden keywords"""
        actions = [AtomicAction("a1", "Test", "Desc", "analysis", {}, ActionPriority.HIGH, 10)]
        steps = [MidLevelStep("s1", "Step 1", "Desc", actions, {})]
        plan = HighLevelPlan(
            "plan_001", "delete_all user data", "Dangerous", steps, 50, "Success", [], {}
        )

        result = self.rules.validate_plan(plan)
        self.assertFalse(result)
        violations = self.rules.get_violations()
        self.assertTrue(any("Forbidden keyword" in v for v in violations))

    def test_validate_plan_invalid_action_type(self):
        """Test plan validation with invalid action type"""
        actions = [AtomicAction("a1", "Test", "Desc", "invalid_type", {}, ActionPriority.HIGH, 10)]
        steps = [MidLevelStep("s1", "Step 1", "Desc", actions, {})]
        plan = HighLevelPlan("plan_001", "Test", "Desc", steps, 50, "Success", [], {})

        result = self.rules.validate_plan(plan)
        self.assertFalse(result)
        violations = self.rules.get_violations()
        self.assertTrue(any("Invalid action type" in v for v in violations))

    def test_check_risk_threshold_within(self):
        """Test risk threshold check within limit"""
        actions = [AtomicAction("a1", "Test", "Desc", "analysis", {}, ActionPriority.HIGH, 10)]
        steps = [MidLevelStep("s1", "Step 1", "Desc", actions, {})]
        plan = HighLevelPlan("plan_001", "Test", "Desc", steps, 50, "Success", [], {})

        result = self.rules.check_risk_threshold(plan, max_risk=80)
        self.assertTrue(result)

    def test_check_risk_threshold_exceeded(self):
        """Test risk threshold check exceeded"""
        actions = [AtomicAction("a1", "Test", "Desc", "analysis", {}, ActionPriority.HIGH, 10)]
        steps = [MidLevelStep("s1", "Step 1", "Desc", actions, {})]
        plan = HighLevelPlan("plan_001", "Test", "Desc", steps, 90, "Success", [], {})

        result = self.rules.check_risk_threshold(plan, max_risk=80)
        self.assertFalse(result)

    def test_validate_action_whitelist_allowed(self):
        """Test action whitelist validation - allowed"""
        result = self.rules.validate_action_whitelist("analysis")
        self.assertTrue(result)

    def test_validate_action_whitelist_forbidden(self):
        """Test action whitelist validation - forbidden"""
        result = self.rules.validate_action_whitelist("delete_all")
        self.assertFalse(result)

    def test_get_validation_report(self):
        """Test validation report generation"""
        report = self.rules.get_validation_report()

        self.assertIn("has_violations", report)
        self.assertIn("violation_count", report)
        self.assertIn("violations", report)
        self.assertIn("max_steps", report)


# =============================================================================
# Strategy Manager Tests
# =============================================================================

class TestStrategyManager(unittest.TestCase):
    """Test StrategyManager orchestration"""

    def setUp(self):
        self.memory_manager = MockMemoryManager()
        self.prediction_manager = MockPredictionManager()
        self.anomaly_manager = MockAnomalyManager()
        self.event_bus = MockEventBus()
        self.security_manager = MockSecurityManager()

        self.manager = StrategyManager(
            memory_manager=self.memory_manager,
            prediction_manager=self.prediction_manager,
            anomaly_manager=self.anomaly_manager,
            event_bus=self.event_bus,
            security_manager=self.security_manager
        )

    def test_create_strategy_basic(self):
        """Test basic strategy creation"""
        plan = self.manager.create_strategy("Optimize system performance", {})

        self.assertIsInstance(plan, HighLevelPlan)
        self.assertEqual(plan.objective, "Optimize system performance")
        self.assertGreater(plan.get_total_steps(), 0)

    def test_create_strategy_with_context(self):
        """Test strategy creation with context"""
        context = {"priority": "high", "component": "memory"}
        plan = self.manager.create_strategy("Fix memory issue", context)

        self.assertIsInstance(plan, HighLevelPlan)
        self.assertIn(plan.plan_id, self.manager.get_active_strategies())

    def test_create_strategy_stores_in_memory(self):
        """Test strategy is stored in episodic memory"""
        plan = self.manager.create_strategy("Test objective", {})

        events = self.memory_manager.episodic_memory.query(event_type="STRATEGY")
        self.assertGreater(len(events), 0)

    def test_create_strategy_emits_event(self):
        """Test strategy creation emits event"""
        plan = self.manager.create_strategy("Test objective", {})

        events = [e for e in self.event_bus.events if e["type"] == STRATEGY_CREATED]
        self.assertGreater(len(events), 0)

    def test_create_strategy_high_risk_event(self):
        """Test high-risk strategy emits event"""
        # Create a complex strategy that will have high risk
        context = {"complexity": "very_high", "critical": True}
        plan = self.manager.create_strategy("Critical system overhaul", context)

        # Check if high-risk event was emitted (risk > 80)
        if plan.risk_score > 80:
            events = [e for e in self.event_bus.events if e["type"] == HIGH_RISK_STRATEGY]
            self.assertGreater(len(events), 0)

    def test_evaluate_strategy_basic(self):
        """Test strategy evaluation"""
        plan = self.manager.create_strategy("Test objective", {})
        evaluation = self.manager.evaluate_strategy(plan)

        self.assertIn("plan_id", evaluation)
        self.assertIn("reasoning_steps", evaluation)
        self.assertIn("simulation", evaluation)
        self.assertIn("decision_tree", evaluation)
        self.assertIn("recommendation", evaluation)

    def test_evaluate_strategy_recommendation(self):
        """Test strategy evaluation recommendation logic"""
        plan = self.manager.create_strategy("Low risk task", {})
        plan.risk_score = 30  # Low risk

        evaluation = self.manager.evaluate_strategy(plan)
        self.assertIn(evaluation["recommendation"], ["proceed", "review"])

    def test_optimize_strategy_basic(self):
        """Test basic strategy optimization"""
        plan = self.manager.create_strategy("Test objective", {})
        original_risk = plan.risk_score

        optimized_plan = self.manager.optimize_strategy(plan.plan_id, {"simplify": True})

        self.assertIsInstance(optimized_plan, HighLevelPlan)
        self.assertEqual(optimized_plan.plan_id, plan.plan_id)

    def test_optimize_strategy_emits_event(self):
        """Test strategy optimization emits event"""
        plan = self.manager.create_strategy("Test objective", {})

        # Clear previous events
        self.event_bus.events.clear()

        optimized_plan = self.manager.optimize_strategy(plan.plan_id, {})

        events = [e for e in self.event_bus.events if e["type"] == STRATEGY_OPTIMIZED]
        self.assertGreater(len(events), 0)

    def test_optimize_strategy_not_found(self):
        """Test optimizing non-existent strategy"""
        with self.assertRaises(KeyError):
            self.manager.optimize_strategy("nonexistent_plan", {})

    def test_simulate_outcome_basic(self):
        """Test outcome simulation"""
        plan = self.manager.create_strategy("Test objective", {})
        simulation = self.manager.simulate_outcome(plan)

        self.assertIsInstance(simulation, dict)
        self.assertIn("action", simulation)

    def test_get_active_strategies(self):
        """Test getting active strategies"""
        plan1 = self.manager.create_strategy("Objective 1", {})
        plan2 = self.manager.create_strategy("Objective 2", {})

        active = self.manager.get_active_strategies()

        self.assertIn(plan1.plan_id, active)
        self.assertIn(plan2.plan_id, active)
        self.assertEqual(len(active), 2)

    def test_get_statistics(self):
        """Test statistics retrieval"""
        self.manager.create_strategy("Test 1", {})
        self.manager.create_strategy("Test 2", {})

        stats = self.manager.get_statistics()

        self.assertIn("total_strategies", stats)
        self.assertIn("active_strategies", stats)
        self.assertIn("enabled", stats)
        self.assertEqual(stats["total_strategies"], 2)
        self.assertEqual(stats["active_strategies"], 2)

    def test_enable_disable(self):
        """Test enabling/disabling strategy manager"""
        self.manager.disable()
        self.assertFalse(self.manager.enabled)

        self.manager.enable()
        self.assertTrue(self.manager.enabled)


# =============================================================================
# Optimizer Service Tests
# =============================================================================

class TestOptimizerService(unittest.TestCase):
    """Test OptimizerService periodic optimization"""

    def setUp(self):
        self.memory_manager = MockMemoryManager()
        self.prediction_manager = MockPredictionManager()
        self.anomaly_manager = MockAnomalyManager()
        self.event_bus = MockEventBus()
        self.security_manager = MockSecurityManager()

        self.strategy_manager = StrategyManager(
            memory_manager=self.memory_manager,
            prediction_manager=self.prediction_manager,
            anomaly_manager=self.anomaly_manager,
            event_bus=self.event_bus,
            security_manager=self.security_manager
        )

        self.optimizer = OptimizerService(
            strategy_manager=self.strategy_manager,
            interval=1  # Short interval for testing
        )

    def test_start_stop(self):
        """Test service start/stop"""
        self.assertFalse(self.optimizer.is_running())

        self.optimizer.start()
        self.assertTrue(self.optimizer.is_running())

        self.optimizer.stop()
        self.assertFalse(self.optimizer.is_running())

    def test_optimize_cycle_no_strategies(self):
        """Test optimization cycle with no strategies"""
        # Should not raise exception
        self.optimizer.optimize_cycle()

    def test_optimize_cycle_with_high_risk_strategy(self):
        """Test optimization cycle optimizes high-risk strategies"""
        # Create a high-risk strategy
        plan = self.strategy_manager.create_strategy("High risk operation", {})
        plan.risk_score = 75  # High risk
        self.strategy_manager.active_strategies[plan.plan_id] = plan

        initial_stats = self.optimizer.get_statistics()
        initial_count = initial_stats["total_optimizations"]

        # Run optimization cycle
        self.optimizer.optimize_cycle()

        # Check that optimization count increased
        stats = self.optimizer.get_statistics()
        self.assertGreater(stats["total_optimizations"], initial_count)

    def test_get_statistics(self):
        """Test statistics retrieval"""
        stats = self.optimizer.get_statistics()

        self.assertIn("running", stats)
        self.assertIn("interval", stats)
        self.assertIn("total_optimizations", stats)
        self.assertIn("last_run", stats)

        self.assertEqual(stats["interval"], 1)


# =============================================================================
# Event Tests
# =============================================================================

class TestStrategyEvents(unittest.TestCase):
    """Test strategy event structures"""

    def test_strategy_created_event(self):
        """Test StrategyCreatedEvent"""
        event = StrategyCreatedEvent(
            plan_id="plan_001",
            objective="Test objective",
            risk_score=50,
            details={"steps": 3, "actions": 10}
        )

        self.assertEqual(event.event_type, STRATEGY_CREATED)

        data = event.to_dict()
        self.assertIn("payload", data)
        self.assertIn("plan_id", data["payload"])
        self.assertIn("objective", data["payload"])
        self.assertIn("risk_score", data["payload"])

    def test_strategy_optimized_event(self):
        """Test StrategyOptimizedEvent"""
        event = StrategyOptimizedEvent(
            plan_id="plan_001",
            optimization_count=2,
            improvements={"risk_reduced": True}
        )

        self.assertEqual(event.event_type, STRATEGY_OPTIMIZED)

        data = event.to_dict()
        self.assertIn("payload", data)
        self.assertIn("optimization_count", data["payload"])

    def test_strategy_rejected_event(self):
        """Test StrategyRejectedEvent"""
        event = StrategyRejectedEvent(
            plan_id="plan_001",
            reason="Validation failed",
            violations=["Too many steps"]
        )

        self.assertEqual(event.event_type, STRATEGY_REJECTED)

        data = event.to_dict()
        self.assertIn("payload", data)
        self.assertIn("reason", data["payload"])
        self.assertIn("violations", data["payload"])

    def test_high_risk_strategy_event(self):
        """Test HighRiskStrategyEvent"""
        event = HighRiskStrategyEvent(
            plan_id="plan_001",
            risk_score=85,
            objective="Critical operation",
            risk_factors=["complexity", "impact"]
        )

        self.assertEqual(event.event_type, HIGH_RISK_STRATEGY)

        data = event.to_dict()
        self.assertIn("payload", data)
        self.assertIn("risk_score", data["payload"])
        self.assertIn("risk_factors", data["payload"])


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration(unittest.TestCase):
    """Test end-to-end integration scenarios"""

    def setUp(self):
        self.memory_manager = MockMemoryManager()
        self.prediction_manager = MockPredictionManager()
        self.anomaly_manager = MockAnomalyManager()
        self.event_bus = MockEventBus()
        self.security_manager = MockSecurityManager()

        self.manager = StrategyManager(
            memory_manager=self.memory_manager,
            prediction_manager=self.prediction_manager,
            anomaly_manager=self.anomaly_manager,
            event_bus=self.event_bus,
            security_manager=self.security_manager
        )

    def test_full_strategy_workflow(self):
        """Test complete strategy creation → evaluation → optimization workflow"""
        # 1. Create strategy
        plan = self.manager.create_strategy("Optimize system performance", {})
        self.assertIsInstance(plan, HighLevelPlan)

        # 2. Evaluate strategy
        evaluation = self.manager.evaluate_strategy(plan)
        self.assertIn("recommendation", evaluation)

        # 3. Simulate outcome
        simulation = self.manager.simulate_outcome(plan)
        self.assertIn("action", simulation)

        # 4. Optimize strategy
        optimized = self.manager.optimize_strategy(plan.plan_id, {"simplify": True})
        self.assertEqual(optimized.plan_id, plan.plan_id)

        # 5. Verify events emitted
        event_types = [e["type"] for e in self.event_bus.events]
        self.assertIn(STRATEGY_CREATED, event_types)
        self.assertIn(STRATEGY_OPTIMIZED, event_types)

    def test_memory_integration(self):
        """Test integration with FAZA 12 Memory Manager"""
        # Create strategy
        plan = self.manager.create_strategy("Test memory integration", {})

        # Verify stored in episodic memory
        events = self.memory_manager.episodic_memory.query(event_type="STRATEGY")
        self.assertGreater(len(events), 0)

        # Verify has correct tags
        stored_event = events[0]
        self.assertIn("strategy", stored_event["tags"])

    def test_security_integration(self):
        """Test integration with FAZA 8 Security Manager"""
        # Create strategy
        plan = self.manager.create_strategy("Test security integration", {})

        # Verify security check was performed
        checks = self.security_manager.checks
        self.assertGreater(len(checks), 0)
        self.assertTrue(any("strategy.execute" in c["operation"] for c in checks))

    def test_optimizer_service_integration(self):
        """Test OptimizerService integration with StrategyManager"""
        optimizer = OptimizerService(self.manager, interval=1)

        # Create high-risk strategy
        plan = self.manager.create_strategy("High risk task", {})
        plan.risk_score = 75
        self.manager.active_strategies[plan.plan_id] = plan

        # Run optimization
        optimizer.optimize_cycle()

        # Verify optimization occurred
        stats = optimizer.get_statistics()
        self.assertGreater(stats["total_optimizations"], 0)


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
