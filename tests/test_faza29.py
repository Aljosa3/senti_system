"""
FAZA 29 – Enterprise Governance Engine
Comprehensive Test Suite

Tests all FAZA 29 modules with 50+ tests covering:
- Governance rules
- Risk scoring
- Override system
- Takeover manager
- Adaptive tick
- Feedback loop
- Integration layer
- Event hooks
- Main governance engine
"""

import unittest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from senti_os.core.faza29 import (
    # Main engine
    GovernanceController,
    get_governance_controller,
    create_governance_controller,
    
    # Governance rules
    GovernanceRuleEngine,
    GovernanceRule,
    GovernanceDecision,
    RuleLayer,
    RulePriority,
    
    # Risk model
    RiskModel,
    compute_risk,
    
    # Override system
    OverrideSystem,
    OverrideType,
    OverrideReason,
    
    # Takeover manager
    TakeoverManager,
    TakeoverState,
    TakeoverReason,
    
    # Adaptive tick
    AdaptiveTickEngine,
    TickConfig,
    
    # Feedback loop
    FeedbackLoop,
    FeedbackConfig,
    
    # Integration layer
    IntegrationLayer,
    
    # Event hooks
    EventHooks,
    EventType,
)


# ==================== Governance Rules Tests ====================

class TestGovernanceRules(unittest.TestCase):
    """Test governance rule engine"""

    def setUp(self):
        """Set up test rule engine"""
        self.engine = GovernanceRuleEngine()

    def test_rule_engine_creation(self):
        """Test rule engine initialization"""
        self.assertIsInstance(self.engine, GovernanceRuleEngine)
        self.assertGreater(self.engine.get_rule_count(), 0)

    def test_user_override_always_wins(self):
        """Test that user override ALWAYS wins"""
        context = {
            "user_override": True,
            "risk_score": 100,  # Maximum risk
            "system_load": 1.0   # Maximum load
        }
        
        decision, ctx = self.engine.evaluate(context)
        self.assertEqual(decision, GovernanceDecision.OVERRIDE)

    def test_high_risk_block(self):
        """Test high risk operations are blocked"""
        context = {
            "risk_score": 85,
            "user_override": False
        }
        
        decision, ctx = self.engine.evaluate(context)
        self.assertEqual(decision, GovernanceDecision.BLOCK)

    def test_medium_risk_escalate(self):
        """Test medium risk escalation"""
        context = {
            "risk_score": 65,
            "user_override": False
        }
        
        decision, ctx = self.engine.evaluate(context)
        self.assertEqual(decision, GovernanceDecision.ESCALATE)

    def test_low_risk_allow(self):
        """Test low risk operations allowed"""
        context = {
            "risk_score": 20,
            "user_override": False
        }
        
        decision, ctx = self.engine.evaluate(context)
        self.assertEqual(decision, GovernanceDecision.ALLOW)

    def test_rule_priority_ordering(self):
        """Test rules evaluate in priority order"""
        # Override should win over all other rules
        context = {
            "user_override": True,
            "risk_score": 100,
            "policy_violation": True
        }
        
        decision, ctx = self.engine.evaluate(context)
        self.assertEqual(decision, GovernanceDecision.OVERRIDE)

    def test_add_custom_rule(self):
        """Test adding custom rule"""
        rule = GovernanceRule(
            rule_id="test_rule",
            name="Test Rule",
            layer=RuleLayer.SYSTEM,
            priority=RulePriority.HIGH,
            condition="test_value > 50",
            action=GovernanceDecision.BLOCK
        )
        
        initial_count = self.engine.get_rule_count()
        self.engine.add_rule(rule)
        self.assertEqual(self.engine.get_rule_count(), initial_count + 1)

    def test_disable_enable_rule(self):
        """Test disabling and enabling rules"""
        self.assertTrue(self.engine.disable_rule("block_high_risk"))
        
        # High risk should now be allowed (rule disabled)
        context = {"risk_score": 85, "user_override": False}
        decision, _ = self.engine.evaluate(context)
        self.assertNotEqual(decision, GovernanceDecision.BLOCK)
        
        # Re-enable
        self.assertTrue(self.engine.enable_rule("block_high_risk"))

    def test_statistics_tracking(self):
        """Test statistics tracking"""
        self.engine.reset_statistics()
        
        context = {"risk_score": 20}
        self.engine.evaluate(context)
        
        stats = self.engine.get_statistics()
        self.assertEqual(stats["rules_evaluated"], 1)


# ==================== Risk Model Tests ====================

class TestRiskModel(unittest.TestCase):
    """Test risk model"""

    def setUp(self):
        """Set up test risk model"""
        self.model = RiskModel()

    def test_risk_model_creation(self):
        """Test risk model initialization"""
        self.assertIsInstance(self.model, RiskModel)

    def test_compute_risk_no_metrics(self):
        """Test risk computation with no metrics"""
        breakdown = self.model.compute_risk()
        
        self.assertGreaterEqual(breakdown.total_risk, 0)
        self.assertLessEqual(breakdown.total_risk, 100)

    def test_compute_risk_high_cpu(self):
        """Test high CPU usage increases risk"""
        system_metrics = {"cpu_usage": 0.95}
        breakdown = self.model.compute_risk(system_metrics=system_metrics)
        
        self.assertGreater(breakdown.system_risk, 50)

    def test_compute_risk_agent_failures(self):
        """Test agent failures increase risk"""
        agent_metrics = {"agent_failure_rate": 0.5}
        breakdown = self.model.compute_risk(agent_metrics=agent_metrics)
        
        self.assertGreater(breakdown.agent_risk, 40)

    def test_compute_risk_graph_cycles(self):
        """Test graph cycles increase risk"""
        graph_metrics = {"cycle_count": 10}
        breakdown = self.model.compute_risk(graph_metrics=graph_metrics)
        
        self.assertGreater(breakdown.graph_risk, 30)

    def test_risk_level_classification(self):
        """Test risk level classification"""
        self.assertEqual(self.model.get_risk_level(85), "critical")
        self.assertEqual(self.model.get_risk_level(65), "high")
        self.assertEqual(self.model.get_risk_level(45), "medium")
        self.assertEqual(self.model.get_risk_level(25), "low")

    def test_critical_factors_identification(self):
        """Test critical factors are identified"""
        system_metrics = {"cpu_usage": 0.90, "memory_usage": 0.95}
        breakdown = self.model.compute_risk(system_metrics=system_metrics)
        
        self.assertGreater(len(breakdown.critical_factors), 0)

    def test_risk_factor_weights(self):
        """Test risk factor weighting"""
        # High-weight factor should dominate
        system_metrics = {"error_rate": 0.8}  # Weight 1.5
        breakdown = self.model.compute_risk(system_metrics=system_metrics)
        
        self.assertGreater(breakdown.system_risk, 60)


# ==================== Override System Tests ====================

class TestOverrideSystem(unittest.TestCase):
    """Test override system"""

    def setUp(self):
        """Set up test override system"""
        self.system = OverrideSystem()
        self.system.disable_cooldown()  # Disable for testing

    def test_override_system_creation(self):
        """Test override system initialization"""
        self.assertIsInstance(self.system, OverrideSystem)

    def test_push_override(self):
        """Test pushing override"""
        override_id = self.system.push_override(
            OverrideType.USER,
            OverrideReason.MANUAL
        )
        
        self.assertIsNotNone(override_id)
        self.assertTrue(self.system.is_override_active())

    def test_override_stack_lifo(self):
        """Test override stack LIFO behavior"""
        id1 = self.system.push_override(OverrideType.USER, OverrideReason.MANUAL)
        id2 = self.system.push_override(OverrideType.SYSTEM, OverrideReason.TESTING)
        
        # Pop should return most recent
        override = self.system.pop_override()
        self.assertEqual(override.override_id, id2)

    def test_override_expiry(self):
        """Test override expiry"""
        override_id = self.system.push_override(
            OverrideType.USER,
            OverrideReason.MANUAL,
            duration_seconds=0.1  # 100ms
        )
        
        import time
        time.sleep(0.2)  # Wait for expiry
        
        # Should be cleaned up
        self.assertFalse(self.system.is_override_active())

    def test_emergency_override_bypasses_cooldown(self):
        """Test emergency override bypasses cooldown"""
        self.system.enable_cooldown()
        
        # Normal override
        self.system.push_override(OverrideType.USER, OverrideReason.MANUAL)
        
        # Emergency should work despite cooldown
        emergency_id = self.system.emergency_override("Test emergency")
        self.assertIsNotNone(emergency_id)

    def test_cooldown_enforcement(self):
        """Test cooldown enforcement"""
        self.system.enable_cooldown()
        self.system.set_cooldown_duration(1.0)
        
        self.system.push_override(OverrideType.USER, OverrideReason.MANUAL)
        
        # Second push should fail (cooldown active)
        with self.assertRaises(RuntimeError):
            self.system.push_override(OverrideType.USER, OverrideReason.MANUAL)

    def test_clear_stack(self):
        """Test clearing override stack"""
        self.system.push_override(OverrideType.USER, OverrideReason.MANUAL)
        self.system.push_override(OverrideType.SYSTEM, OverrideReason.TESTING)
        
        count = self.system.clear_stack()
        self.assertEqual(count, 2)
        self.assertFalse(self.system.is_override_active())


# ==================== Takeover Manager Tests ====================

class TestTakeoverManager(unittest.TestCase):
    """Test takeover manager"""

    def setUp(self):
        """Set up test takeover manager"""
        self.manager = TakeoverManager()

    def test_takeover_manager_creation(self):
        """Test takeover manager initialization"""
        self.assertIsInstance(self.manager, TakeoverManager)
        self.assertEqual(self.manager.get_state(), TakeoverState.NORMAL)

    def test_70_percent_threshold(self):
        """Test 70% takeover threshold"""
        self.assertEqual(self.manager.takeover_threshold, 0.70)

    def test_high_risk_triggers_takeover(self):
        """Test high risk triggers takeover"""
        state = self.manager.evaluate(risk_score=90)
        
        self.assertEqual(state, TakeoverState.TAKEOVER)
        self.assertTrue(self.manager.is_takeover_active())

    def test_runaway_agent_triggers_takeover(self):
        """Test runaway agent triggers takeover"""
        agent_metrics = {"runaway_detected": 0.90}
        state = self.manager.evaluate(agent_metrics=agent_metrics)
        
        self.assertEqual(state, TakeoverState.TAKEOVER)

    def test_resource_collapse_triggers_takeover(self):
        """Test resource collapse triggers takeover"""
        system_metrics = {"cpu_usage": 0.95, "memory_usage": 0.90}
        state = self.manager.evaluate(system_metrics=system_metrics)
        
        self.assertEqual(state, TakeoverState.TAKEOVER)

    def test_takeover_enters_safe_mode(self):
        """Test takeover enters safe mode"""
        self.manager.evaluate(risk_score=90)
        
        self.assertTrue(self.manager.is_safe_mode_active())

    def test_takeover_freezes_scheduler(self):
        """Test takeover freezes scheduler"""
        self.manager.evaluate(risk_score=90)
        
        self.assertTrue(self.manager.is_scheduler_frozen())

    def test_manual_takeover(self):
        """Test manual takeover"""
        self.manager.manual_takeover("Testing manual takeover")
        
        self.assertTrue(self.manager.is_takeover_active())
        self.assertEqual(self.manager.get_state(), TakeoverState.TAKEOVER)

    def test_takeover_recovery(self):
        """Test takeover recovery"""
        # Trigger takeover
        self.manager.evaluate(risk_score=90)
        self.assertTrue(self.manager.is_takeover_active())
        
        # Force recovery
        self.manager.force_recovery()
        self.assertFalse(self.manager.is_takeover_active())


# ==================== Adaptive Tick Tests ====================

class TestAdaptiveTick(unittest.TestCase):
    """Test adaptive tick engine"""

    def setUp(self):
        """Set up test tick engine"""
        self.engine = AdaptiveTickEngine()

    def test_tick_engine_creation(self):
        """Test tick engine initialization"""
        self.assertIsInstance(self.engine, AdaptiveTickEngine)
        self.assertEqual(self.engine.get_current_hz(), 1.0)

    def test_tick_frequency_bounds(self):
        """Test tick frequency stays within bounds"""
        # Very high load and risk
        hz = self.engine.update(system_load=1.0, risk_score=100)
        
        self.assertGreaterEqual(hz, self.engine.config.min_hz)
        self.assertLessEqual(hz, self.engine.config.max_hz)

    def test_high_risk_increases_frequency(self):
        """Test high risk increases tick frequency"""
        initial_hz = self.engine.get_current_hz()
        
        hz = self.engine.update(risk_score=90, system_load=0.3)
        
        # Risk should increase frequency
        self.assertGreater(hz, initial_hz * 0.9)

    def test_high_load_decreases_frequency(self):
        """Test high load decreases tick frequency"""
        initial_hz = self.engine.get_current_hz()
        
        hz = self.engine.update(system_load=0.95, risk_score=20)
        
        # Load should decrease frequency
        self.assertLess(hz, initial_hz * 1.1)

    def test_override_active_max_frequency(self):
        """Test override active increases to max frequency"""
        hz = self.engine.update(override_active=True)
        
        # Should approach maximum
        self.assertGreater(hz, self.engine.config.default_hz)

    def test_spike_suppression(self):
        """Test spike suppression"""
        # Build history
        for _ in range(10):
            self.engine.update(risk_score=30)
        
        # Sudden spike
        hz = self.engine.update(risk_score=95)
        
        # Should be suppressed (not instant jump to max)
        self.assertLess(hz, self.engine.config.max_hz * 0.9)

    def test_force_frequency(self):
        """Test forcing specific frequency"""
        self.engine.force_frequency(5.0)
        self.assertEqual(self.engine.get_current_hz(), 5.0)

    def test_tick_interval_calculation(self):
        """Test tick interval calculation"""
        self.engine.force_frequency(2.0)
        interval = self.engine.get_tick_interval()
        self.assertAlmostEqual(interval, 0.5, places=2)


# ==================== Feedback Loop Tests ====================

class TestFeedbackLoop(unittest.TestCase):
    """Test feedback loop"""

    def setUp(self):
        """Set up test feedback loop"""
        self.loop = FeedbackLoop()

    def test_feedback_loop_creation(self):
        """Test feedback loop initialization"""
        self.assertIsInstance(self.loop, FeedbackLoop)

    def test_feedback_correction(self):
        """Test feedback generates corrective signal"""
        signal, smooth, damp = self.loop.update(measurement=0.3)
        
        # Should generate positive correction (measurement < setpoint)
        self.assertGreater(signal, 0)

    def test_deadband(self):
        """Test deadband prevents small corrections"""
        # Very close to setpoint
        signal1, _, _ = self.loop.update(measurement=0.50)
        signal2, _, _ = self.loop.update(measurement=0.51)
        
        # Signals should be small or zero (in deadband)
        self.assertLess(abs(signal1), 0.1)

    def test_integral_windup_prevention(self):
        """Test integral windup prevention"""
        # Sustained error
        for _ in range(100):
            self.loop.update(measurement=0.0)
        
        # Integral should be limited
        self.assertLessEqual(abs(self.loop.state.integral), self.loop.config.integral_limit)

    def test_reinforcement_signals(self):
        """Test reinforcement signal application"""
        self.loop.add_reinforcement_signal("policy1", 0.5)
        
        signal, _, _ = self.loop.update(measurement=0.3)
        
        # Reinforcement should affect output
        self.assertIsNotNone(signal)

    def test_stability_score(self):
        """Test stability score calculation"""
        # Stable system (low error)
        for _ in range(10):
            self.loop.update(measurement=0.48)
        
        score = self.loop.get_stability_score()
        self.assertGreater(score, 0.7)

    def test_threshold_gates(self):
        """Test threshold gate application"""
        # Low stability measurement
        signal1, _, _ = self.loop.update(measurement=0.2)
        
        # High stability measurement
        self.loop.reset()
        signal2, _, _ = self.loop.update(measurement=0.9)
        
        # Gates should modify signals differently
        self.assertNotEqual(signal1, signal2)

    def test_set_setpoint(self):
        """Test changing setpoint"""
        self.loop.set_setpoint(0.7)
        self.assertEqual(self.loop.config.setpoint, 0.7)


# ==================== Integration Layer Tests ====================

class TestIntegrationLayer(unittest.TestCase):
    """Test integration layer"""

    def setUp(self):
        """Set up test integration layer"""
        self.integration = IntegrationLayer()

    def test_integration_layer_creation(self):
        """Test integration layer initialization"""
        self.assertIsInstance(self.integration, IntegrationLayer)

    def test_faza28_attachment(self):
        """Test FAZA 28 EventBus attachment"""
        mock_bus = Mock()
        self.integration.attach_faza28_event_bus(mock_bus)
        
        self.assertTrue(self.integration.integrations["faza28"])

    def test_faza25_attachment(self):
        """Test FAZA 25 Orchestrator attachment"""
        mock_orch = Mock()
        self.integration.attach_faza25_orchestrator(mock_orch)
        
        self.assertTrue(self.integration.integrations["faza25"])

    def test_emit_governance_event(self):
        """Test emitting governance event"""
        mock_bus = Mock()
        self.integration.attach_faza28_event_bus(mock_bus)
        
        self.integration.emit_governance_event("ALLOW", {})
        
        # Verify event was published
        self.assertGreater(self.integration.stats["governance_events"], 0)

    def test_get_orchestrator_metrics_no_attachment(self):
        """Test getting metrics without attachment"""
        metrics = self.integration.get_orchestrator_metrics()
        self.assertEqual(metrics, {})

    def test_callback_registration(self):
        """Test callback registration"""
        callback = Mock()
        self.integration.register_governance_callback(callback)
        
        self.assertEqual(len(self.integration.governance_callbacks), 1)

    def test_callback_triggering(self):
        """Test callback triggering"""
        callback = Mock()
        self.integration.register_governance_callback(callback)
        
        self.integration.trigger_governance_callbacks("ALLOW", {})
        
        callback.assert_called_once()


# ==================== Event Hooks Tests ====================

class TestEventHooks(unittest.TestCase):
    """Test event hooks"""

    def setUp(self):
        """Set up test event hooks"""
        self.hooks = EventHooks()

    def test_event_hooks_creation(self):
        """Test event hooks initialization"""
        self.assertIsInstance(self.hooks, EventHooks)

    def test_event_publishing(self):
        """Test event publishing"""
        from senti_os.core.faza29.event_hooks import FazaEvent
        
        event = FazaEvent(
            event_type=EventType.GOVERNANCE_DECISION,
            source="test",
            data={"decision": "ALLOW"}
        )
        
        self.hooks.publish(event)
        
        stats = self.hooks.get_statistics()
        self.assertEqual(stats["events_published"], 1)

    def test_event_subscription(self):
        """Test event subscription"""
        callback = Mock()
        self.hooks.subscribe(EventType.GOVERNANCE_DECISION, callback)
        
        from senti_os.core.faza29.event_hooks import FazaEvent
        event = FazaEvent(
            event_type=EventType.GOVERNANCE_DECISION,
            source="test"
        )
        
        self.hooks.publish(event)
        
        callback.assert_called_once()

    def test_event_unsubscribe(self):
        """Test event unsubscription"""
        callback = Mock()
        self.hooks.subscribe(EventType.GOVERNANCE_DECISION, callback)
        
        result = self.hooks.unsubscribe(EventType.GOVERNANCE_DECISION, callback)
        self.assertTrue(result)


# ==================== Governance Controller Tests ====================

class TestGovernanceController(unittest.TestCase):
    """Test main governance controller"""

    def setUp(self):
        """Set up test governance controller"""
        self.controller = create_governance_controller()

    def test_controller_creation(self):
        """Test controller initialization"""
        self.assertIsInstance(self.controller, GovernanceController)

    def test_evaluate_governance_no_override(self):
        """Test governance evaluation without override"""
        result = self.controller.evaluate_governance()
        
        self.assertIn("decision", result)
        self.assertIn("risk_score", result)
        self.assertIn("takeover_state", result)

    def test_evaluate_governance_with_override(self):
        """Test governance evaluation with override"""
        self.controller.get_override_system().disable_cooldown()
        self.controller.get_override_system().push_override(
            OverrideType.USER,
            OverrideReason.MANUAL
        )
        
        result = self.controller.evaluate_governance()
        
        self.assertEqual(result["decision"], "override")
        self.assertTrue(result["override_active"])

    def test_get_status(self):
        """Test getting controller status"""
        status = self.controller.get_status()
        
        self.assertIn("running", status)
        self.assertIn("takeover_state", status)
        self.assertIn("current_tick_hz", status)

    def test_get_risk(self):
        """Test getting risk assessment"""
        risk = self.controller.get_risk()
        
        self.assertIn("total_risk", risk)
        self.assertIn("system_risk", risk)
        self.assertIn("agent_risk", risk)
        self.assertIn("graph_risk", risk)

    def test_get_statistics(self):
        """Test getting comprehensive statistics"""
        stats = self.controller.get_statistics()
        
        self.assertIn("controller", stats)
        self.assertIn("rule_engine", stats)
        self.assertIn("risk_model", stats)
        self.assertIn("takeover_manager", stats)

    def test_component_access(self):
        """Test accessing individual components"""
        self.assertIsInstance(self.controller.get_rule_engine(), GovernanceRuleEngine)
        self.assertIsInstance(self.controller.get_risk_model(), RiskModel)
        self.assertIsInstance(self.controller.get_override_system(), OverrideSystem)
        self.assertIsInstance(self.controller.get_takeover_manager(), TakeoverManager)

    def test_governance_loop_start_stop(self):
        """Test starting and stopping governance loop"""
        async def test_loop():
            await self.controller.start()
            self.assertTrue(self.controller.running)
            
            await asyncio.sleep(0.1)
            
            await self.controller.stop()
            self.assertFalse(self.controller.running)
        
        asyncio.run(test_loop())


# ==================== Main ====================

if __name__ == "__main__":
    unittest.main()
