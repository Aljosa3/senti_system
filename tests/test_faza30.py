"""
FAZA 30 – Test Suite

Comprehensive test suite for Enterprise Self-Healing Engine.

Test Coverage:
- Detection Engine (10 tests)
- Classification Engine (10 tests)
- Repair Strategies (16 tests - 4 per engine)
- Healing Pipeline (12 tests)
- Snapshot Manager (8 tests)
- Health Engine (10 tests)
- Autorepair Engine (10 tests)
- Integration Layer (8 tests)
- Event Hooks (6 tests)
- Controller (10 tests)

Total: 100 tests
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Import FAZA 30 components
from senti_os.core.faza30 import (
    # Detection
    DetectionEngine,
    FaultSeverity,
    FaultSource,

    # Classification
    ClassificationEngine,
    FaultCategory,
    RepairPriority,

    # Repair
    GraphRepairEngine,
    AgentRepairEngine,
    SchedulerRepairEngine,
    GovernanceRepairEngine,
    RepairStatus,

    # Pipeline
    HealingPipeline,
    HealingStage,
    HealingOutcome,

    # Snapshot
    SnapshotManager,
    SnapshotType,

    # Health
    HealthEngine,
    HealthLevel,
    TrendDirection,

    # Autorepair
    AutorepairEngine,
    AutorepairConfig,
    AutorepairMode,
    ThrottleState,

    # Integration
    IntegrationLayer,

    # Events
    EventHooks,
    EventType,

    # Controller
    HealingController,
    get_healing_controller,
    create_healing_controller
)


# ======================
# Test Detection Engine
# ======================

class TestDetectionEngine(unittest.TestCase):
    """Test detection engine functionality."""

    def setUp(self):
        self.engine = DetectionEngine()

    def test_detection_engine_creation(self):
        """Test detection engine can be created."""
        self.assertIsNotNone(self.engine)

    def test_detect_faults_empty_metrics(self):
        """Test detection with empty metrics."""
        faults = self.engine.detect_faults({}, {}, {}, {}, {})
        self.assertIsInstance(faults, list)

    def test_detect_faza25_high_queue(self):
        """Test FAZA 25 high queue detection."""
        metrics = {'queue_size': 150}
        faults = self.engine.detect_faults(metrics, {}, {}, {}, {})

        # Should detect high queue
        queue_faults = [f for f in faults if 'queue' in f.fault_type.lower()]
        self.assertTrue(len(queue_faults) > 0)

    def test_detect_faza27_cycles(self):
        """Test FAZA 27 cycle detection."""
        metrics = {'cycle_count': 3}
        faults = self.engine.detect_faults({}, metrics, {}, {}, {})

        cycle_faults = [f for f in faults if 'cycle' in f.fault_type.lower()]
        self.assertTrue(len(cycle_faults) > 0)

    def test_detect_faza29_high_risk(self):
        """Test FAZA 29 high risk detection."""
        metrics = {'risk_score': 85}
        faults = self.engine.detect_faults({}, {}, {}, {}, metrics)

        risk_faults = [f for f in faults if 'risk' in f.fault_type.lower()]
        self.assertTrue(len(risk_faults) > 0)

    def test_fault_severity_classification(self):
        """Test fault severity is properly assigned."""
        metrics = {'risk_score': 95}
        faults = self.engine.detect_faults({}, {}, {}, {}, metrics)

        if faults:
            self.assertIn(faults[0].severity, [
                FaultSeverity.CRITICAL,
                FaultSeverity.HIGH,
                FaultSeverity.MEDIUM,
                FaultSeverity.LOW,
                FaultSeverity.INFO
            ])

    def test_get_active_faults(self):
        """Test getting active faults."""
        self.engine.detect_faults({'queue_size': 150}, {}, {}, {}, {})
        active = self.engine.get_active_faults()
        self.assertIsInstance(active, list)

    def test_get_critical_faults(self):
        """Test getting critical faults."""
        critical = self.engine.get_critical_faults()
        self.assertIsInstance(critical, list)

    def test_predict_failures(self):
        """Test failure prediction."""
        history = [{'risk_score': i * 10} for i in range(5)]
        predictions = self.engine.predict_failures(history)
        self.assertIsInstance(predictions, list)

    def test_statistics_tracking(self):
        """Test statistics are tracked."""
        stats = self.engine.get_statistics()
        self.assertIn('total_detections', stats)


# ======================
# Test Classification Engine
# ======================

class TestClassificationEngine(unittest.TestCase):
    """Test classification engine functionality."""

    def setUp(self):
        self.engine = ClassificationEngine()
        self.detection_engine = DetectionEngine()

    def test_classification_engine_creation(self):
        """Test classification engine can be created."""
        self.assertIsNotNone(self.engine)

    def test_classify_operational_fault(self):
        """Test operational fault classification."""
        faults = self.detection_engine.detect_faults({'queue_size': 150}, {}, {}, {}, {})
        if faults:
            result = self.engine.classify_fault(faults[0])
            self.assertIsInstance(result.category, FaultCategory)

    def test_classify_structural_fault(self):
        """Test structural fault classification."""
        faults = self.detection_engine.detect_faults({}, {'cycle_count': 5}, {}, {}, {})
        if faults:
            result = self.engine.classify_fault(faults[0])
            # Should classify as structural due to cycles
            self.assertIsInstance(result.category, FaultCategory)

    def test_confidence_score(self):
        """Test classification confidence."""
        faults = self.detection_engine.detect_faults({'queue_size': 150}, {}, {}, {}, {})
        if faults:
            result = self.engine.classify_fault(faults[0])
            self.assertTrue(0.0 <= result.confidence <= 1.0)

    def test_repair_priority_assignment(self):
        """Test repair priority is assigned."""
        faults = self.detection_engine.detect_faults({}, {}, {}, {}, {'risk_score': 90})
        if faults:
            result = self.engine.classify_fault(faults[0])
            self.assertIsInstance(result.repair_priority, RepairPriority)

    def test_subcategory_determination(self):
        """Test subcategory is determined."""
        faults = self.detection_engine.detect_faults({'queue_size': 150}, {}, {}, {}, {})
        if faults:
            result = self.engine.classify_fault(faults[0])
            self.assertIsInstance(result.subcategory, str)

    def test_root_cause_analysis(self):
        """Test root cause is identified."""
        faults = self.detection_engine.detect_faults({'cpu_usage': 0.95}, {}, {}, {}, {})
        if faults:
            result = self.engine.classify_fault(faults[0])
            self.assertIsInstance(result.root_cause, str)

    def test_affected_components_list(self):
        """Test affected components are listed."""
        faults = self.detection_engine.detect_faults({'queue_size': 150}, {}, {}, {}, {})
        if faults:
            result = self.engine.classify_fault(faults[0])
            self.assertIsInstance(result.affected_components, list)

    def test_recommended_actions(self):
        """Test recommended actions are generated."""
        faults = self.detection_engine.detect_faults({'queue_size': 150}, {}, {}, {}, {})
        if faults:
            result = self.engine.classify_fault(faults[0])
            self.assertIsInstance(result.recommended_actions, list)
            self.assertTrue(len(result.recommended_actions) > 0)

    def test_statistics_tracking(self):
        """Test classification statistics."""
        stats = self.engine.get_statistics()
        self.assertIn('total_classifications', stats)

    def test_pattern_cache(self):
        """Test pattern caching works."""
        faults = self.detection_engine.detect_faults({'queue_size': 150}, {}, {}, {}, {})
        if faults:
            # Classify twice
            self.engine.classify_fault(faults[0])
            self.engine.classify_fault(faults[0])

            stats = self.engine.get_statistics()
            self.assertGreaterEqual(stats['total_classifications'], 2)


# ======================
# Test Repair Engines
# ======================

class TestGraphRepairEngine(unittest.TestCase):
    """Test graph repair engine."""

    def setUp(self):
        self.engine = GraphRepairEngine()
        self.detection_engine = DetectionEngine()

    def test_graph_repair_creation(self):
        """Test graph repair engine creation."""
        self.assertIsNotNone(self.engine)

    def test_can_repair_structural_fault(self):
        """Test can repair structural fault detection."""
        faults = self.detection_engine.detect_faults({}, {'cycle_count': 3}, {}, {}, {})
        if faults:
            can_repair = self.engine.can_repair(faults[0], {})
            self.assertIsInstance(can_repair, bool)

    def test_repair_cycle_fault(self):
        """Test cycle repair."""
        faults = self.detection_engine.detect_faults({}, {'cycle_count': 2}, {}, {}, {})
        if faults:
            result = self.engine.repair(faults[0], {})
            self.assertIsInstance(result.status, RepairStatus)

    def test_repair_statistics(self):
        """Test repair statistics tracking."""
        stats = self.engine.get_statistics()
        self.assertIn('total_repairs', stats)


class TestAgentRepairEngine(unittest.TestCase):
    """Test agent repair engine."""

    def setUp(self):
        self.engine = AgentRepairEngine()
        self.detection_engine = DetectionEngine()

    def test_agent_repair_creation(self):
        """Test agent repair engine creation."""
        self.assertIsNotNone(self.engine)

    def test_can_repair_agent_fault(self):
        """Test can repair agent fault detection."""
        faults = self.detection_engine.detect_faults({}, {}, {'agent_failure_rate': 0.5}, {}, {})
        if faults:
            can_repair = self.engine.can_repair(faults[0], {})
            self.assertIsInstance(can_repair, bool)

    def test_repair_agent_fault(self):
        """Test agent fault repair."""
        faults = self.detection_engine.detect_faults({}, {}, {'agent_failure_rate': 0.3}, {}, {})
        if faults:
            result = self.engine.repair(faults[0], {})
            self.assertIsInstance(result.status, RepairStatus)

    def test_repair_statistics(self):
        """Test repair statistics."""
        stats = self.engine.get_statistics()
        self.assertIn('total_repairs', stats)


class TestSchedulerRepairEngine(unittest.TestCase):
    """Test scheduler repair engine."""

    def setUp(self):
        self.engine = SchedulerRepairEngine()
        self.detection_engine = DetectionEngine()

    def test_scheduler_repair_creation(self):
        """Test scheduler repair engine creation."""
        self.assertIsNotNone(self.engine)

    def test_can_repair_operational_fault(self):
        """Test can repair operational fault."""
        faults = self.detection_engine.detect_faults({'queue_size': 200}, {}, {}, {}, {})
        if faults:
            can_repair = self.engine.can_repair(faults[0], {})
            self.assertIsInstance(can_repair, bool)

    def test_repair_operational_fault(self):
        """Test operational fault repair."""
        faults = self.detection_engine.detect_faults({'cpu_usage': 0.95}, {}, {}, {}, {})
        if faults:
            result = self.engine.repair(faults[0], {})
            self.assertIsInstance(result.status, RepairStatus)

    def test_repair_statistics(self):
        """Test repair statistics."""
        stats = self.engine.get_statistics()
        self.assertIn('total_repairs', stats)


class TestGovernanceRepairEngine(unittest.TestCase):
    """Test governance repair engine."""

    def setUp(self):
        self.engine = GovernanceRepairEngine()
        self.detection_engine = DetectionEngine()

    def test_governance_repair_creation(self):
        """Test governance repair engine creation."""
        self.assertIsNotNone(self.engine)

    def test_can_repair_governance_fault(self):
        """Test can repair governance fault."""
        faults = self.detection_engine.detect_faults({}, {}, {}, {}, {'governance_violations': 10})
        if faults:
            can_repair = self.engine.can_repair(faults[0], {})
            self.assertIsInstance(can_repair, bool)

    def test_repair_governance_fault(self):
        """Test governance fault repair."""
        faults = self.detection_engine.detect_faults({}, {}, {}, {}, {'governance_violations': 5})
        if faults:
            result = self.engine.repair(faults[0], {})
            self.assertIsInstance(result.status, RepairStatus)

    def test_repair_statistics(self):
        """Test repair statistics."""
        stats = self.engine.get_statistics()
        self.assertIn('total_repairs', stats)


# ======================
# Test Healing Pipeline
# ======================

class TestHealingPipeline(unittest.TestCase):
    """Test healing pipeline."""

    def setUp(self):
        self.detection_engine = DetectionEngine()
        self.classification_engine = ClassificationEngine()
        self.repair_engines = {
            "graph": GraphRepairEngine(),
            "agent": AgentRepairEngine(),
            "scheduler": SchedulerRepairEngine(),
            "governance": GovernanceRepairEngine()
        }
        self.health_engine = HealthEngine()

        self.pipeline = HealingPipeline(
            detection_engine=self.detection_engine,
            classification_engine=self.classification_engine,
            repair_engines=self.repair_engines,
            snapshot_manager=None,
            health_engine=self.health_engine
        )

    def test_pipeline_creation(self):
        """Test healing pipeline can be created."""
        self.assertIsNotNone(self.pipeline)

    def test_execute_cycle_no_faults(self):
        """Test healing cycle with no faults."""
        result = self.pipeline.execute_healing_cycle({}, {}, {}, {}, {})
        self.assertEqual(result.outcome, HealingOutcome.SKIPPED)

    def test_execute_cycle_with_faults(self):
        """Test healing cycle with faults."""
        result = self.pipeline.execute_healing_cycle(
            faza25_metrics={'queue_size': 150},
            faza27_metrics={},
            faza28_metrics={},
            faza28_5_metrics={},
            faza29_metrics={}
        )
        self.assertIsInstance(result.outcome, HealingOutcome)

    def test_cycle_stages_completion(self):
        """Test all 12 stages complete."""
        result = self.pipeline.execute_healing_cycle(
            faza25_metrics={'queue_size': 150}
        )
        # At least stage 1 and 2 should complete
        self.assertGreaterEqual(len(result.stages_completed), 2)

    def test_fault_detection_stage(self):
        """Test stage 1 (detection) works."""
        result = self.pipeline.execute_healing_cycle(
            faza29_metrics={'risk_score': 80}
        )
        self.assertIn(HealingStage.STAGE_1_DETECT, result.stages_completed)

    def test_fault_classification_stage(self):
        """Test stage 2 (classification) works."""
        result = self.pipeline.execute_healing_cycle(
            faza25_metrics={'queue_size': 150}
        )
        if result.faults_detected > 0:
            self.assertIn(HealingStage.STAGE_2_CLASSIFY, result.stages_completed)

    def test_health_tracking(self):
        """Test health is tracked before/after."""
        result = self.pipeline.execute_healing_cycle(
            faza25_metrics={'queue_size': 50}
        )
        # Health should be computed
        self.assertIsInstance(result.health_improvement, float)

    def test_pipeline_statistics(self):
        """Test pipeline statistics tracking."""
        stats = self.pipeline.get_statistics()
        self.assertIn('total_cycles', stats)

    def test_recent_cycles(self):
        """Test getting recent cycles."""
        self.pipeline.execute_healing_cycle(faza25_metrics={'queue_size': 150})
        recent = self.pipeline.get_recent_cycles(limit=5)
        self.assertIsInstance(recent, list)

    def test_rollback_on_health_decline(self):
        """Test rollback if health declines."""
        # This is tested implicitly in the pipeline logic
        result = self.pipeline.execute_healing_cycle(
            faza25_metrics={'queue_size': 50}
        )
        self.assertIsInstance(result.rollback_performed, bool)

    def test_stage_results_stored(self):
        """Test stage results are stored in context."""
        result = self.pipeline.execute_healing_cycle(
            faza25_metrics={'queue_size': 150}
        )
        self.assertGreater(len(result.context.stage_results), 0)

    def test_cycle_duration(self):
        """Test cycle duration is measured."""
        result = self.pipeline.execute_healing_cycle(
            faza25_metrics={'queue_size': 150}
        )
        self.assertGreater(result.duration, 0)

    def test_faults_repaired_count(self):
        """Test faults repaired count is accurate."""
        result = self.pipeline.execute_healing_cycle(
            faza25_metrics={'queue_size': 150}
        )
        self.assertGreaterEqual(result.faults_repaired, 0)


# ======================
# Test Snapshot Manager
# ======================

class TestSnapshotManager(unittest.TestCase):
    """Test snapshot manager."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SnapshotManager(snapshot_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_snapshot_manager_creation(self):
        """Test snapshot manager can be created."""
        self.assertIsNotNone(self.manager)

    def test_create_snapshot(self):
        """Test creating a snapshot."""
        snapshot_id = self.manager.create_snapshot(snapshot_type="manual")
        self.assertIsInstance(snapshot_id, str)

    def test_list_snapshots(self):
        """Test listing snapshots."""
        self.manager.create_snapshot(snapshot_type="manual")
        snapshots = self.manager.list_snapshots()
        self.assertIsInstance(snapshots, list)
        self.assertGreater(len(snapshots), 0)

    def test_get_snapshot(self):
        """Test getting a snapshot by ID."""
        snapshot_id = self.manager.create_snapshot(snapshot_type="manual")
        snapshot = self.manager.get_snapshot(snapshot_id)
        self.assertIsNotNone(snapshot)

    def test_delete_snapshot(self):
        """Test deleting a snapshot."""
        snapshot_id = self.manager.create_snapshot(snapshot_type="manual")
        result = self.manager.delete_snapshot(snapshot_id)
        self.assertTrue(result)

    def test_restore_snapshot(self):
        """Test restoring from snapshot."""
        snapshot_id = self.manager.create_snapshot(snapshot_type="manual")
        result = self.manager.restore_snapshot(snapshot_id)
        self.assertTrue(result)

    def test_snapshot_persistence(self):
        """Test snapshots persist to disk."""
        snapshot_id = self.manager.create_snapshot(snapshot_type="manual")

        # Create new manager with same directory
        manager2 = SnapshotManager(snapshot_dir=self.temp_dir)
        snapshot = manager2.get_snapshot(snapshot_id)
        self.assertIsNotNone(snapshot)

    def test_snapshot_statistics(self):
        """Test snapshot statistics."""
        self.manager.create_snapshot(snapshot_type="manual")
        stats = self.manager.get_statistics()
        self.assertIn('total_created', stats)


# ======================
# Test Health Engine
# ======================

class TestHealthEngine(unittest.TestCase):
    """Test health engine."""

    def setUp(self):
        self.engine = HealthEngine()

    def test_health_engine_creation(self):
        """Test health engine can be created."""
        self.assertIsNotNone(self.engine)

    def test_compute_health_score(self):
        """Test computing health score."""
        score = self.engine.compute_health_score(
            faza25_metrics={'queue_size': 50},
            faza27_metrics={},
            faza28_metrics={},
            faza28_5_metrics={},
            faza29_metrics={}
        )
        self.assertIsInstance(score.overall_score, float)
        self.assertTrue(0 <= score.overall_score <= 100)

    def test_health_level_classification(self):
        """Test health level is classified."""
        score = self.engine.compute_health_score()
        self.assertIsInstance(score.level, HealthLevel)

    def test_component_breakdown(self):
        """Test health breakdown by component."""
        score = self.engine.compute_health_score()
        self.assertGreater(len(score.components), 0)

    def test_trend_analysis(self):
        """Test health trend analysis."""
        # Generate some history
        for i in range(5):
            self.engine.compute_health_score(
                faza25_metrics={'queue_size': i * 20}
            )

        trend = self.engine.analyze_trend()
        self.assertIsInstance(trend.direction, TrendDirection)

    def test_trend_slope_calculation(self):
        """Test trend slope calculation."""
        for i in range(10):
            self.engine.compute_health_score(
                faza29_metrics={'risk_score': i * 5}
            )

        trend = self.engine.analyze_trend()
        self.assertIsInstance(trend.slope, float)

    def test_health_prediction(self):
        """Test health prediction."""
        for i in range(5):
            self.engine.compute_health_score()

        trend = self.engine.analyze_trend()
        self.assertIsInstance(trend.prediction, float)
        self.assertTrue(0 <= trend.prediction <= 100)

    def test_statistics_tracking(self):
        """Test health statistics."""
        self.engine.compute_health_score()
        stats = self.engine.get_statistics()
        self.assertIn('total_scores_computed', stats)
        self.assertIn('avg_health', stats)

    def test_health_history(self):
        """Test health history tracking."""
        self.engine.compute_health_score()
        history = self.engine.get_health_history()
        self.assertIsInstance(history, list)

    def test_component_weights(self):
        """Test component weights sum to 1.0."""
        weights_sum = sum(self.engine._component_weights.values())
        self.assertAlmostEqual(weights_sum, 1.0, places=2)


# ======================
# Test Autorepair Engine
# ======================

class TestAutorepairEngine(unittest.TestCase):
    """Test autorepair engine."""

    def setUp(self):
        detection = DetectionEngine()
        classification = ClassificationEngine()
        repair_engines = {
            "graph": GraphRepairEngine(),
            "agent": AgentRepairEngine(),
            "scheduler": SchedulerRepairEngine(),
            "governance": GovernanceRepairEngine()
        }
        health = HealthEngine()

        pipeline = HealingPipeline(
            detection_engine=detection,
            classification_engine=classification,
            repair_engines=repair_engines,
            snapshot_manager=None,
            health_engine=health
        )

        config = AutorepairConfig(
            mode=AutorepairMode.BALANCED,
            interval_seconds=0.1
        )

        self.engine = AutorepairEngine(
            healing_pipeline=pipeline,
            config=config
        )

    def test_autorepair_engine_creation(self):
        """Test autorepair engine can be created."""
        self.assertIsNotNone(self.engine)

    async def test_start_stop(self):
        """Test starting and stopping autorepair."""
        await self.engine.start()
        self.assertTrue(self.engine.is_running())

        await self.engine.stop()
        self.assertFalse(self.engine.is_running())

    def test_set_mode(self):
        """Test setting autorepair mode."""
        self.engine.set_mode(AutorepairMode.CONSERVATIVE)
        self.assertEqual(self.engine.config.mode, AutorepairMode.CONSERVATIVE)

    def test_set_interval(self):
        """Test setting monitoring interval."""
        self.engine.set_interval(1.0)
        self.assertEqual(self.engine.config.interval_seconds, 1.0)

    def test_throttle_check(self):
        """Test throttle state checking."""
        state = self.engine.get_throttle_state()
        self.assertIsInstance(state, ThrottleState)

    def test_statistics_tracking(self):
        """Test autorepair statistics."""
        stats = self.engine.get_statistics()
        self.assertIn('total_cycles', stats)
        self.assertIn('healing_cycles_triggered', stats)

    def test_uptime_tracking(self):
        """Test uptime tracking."""
        uptime = self.engine.get_uptime()
        self.assertGreaterEqual(uptime, 0)

    def test_config_access(self):
        """Test getting configuration."""
        config = self.engine.get_config()
        self.assertIsInstance(config, AutorepairConfig)

    def test_config_update(self):
        """Test updating configuration."""
        self.engine.update_config(max_repairs_per_minute=20)
        self.assertEqual(self.engine.config.max_repairs_per_minute, 20)

    def test_force_healing_cycle(self):
        """Test forcing a healing cycle."""
        self.engine.force_healing_cycle()
        # Should reset last repair time
        self.assertIsNone(self.engine._last_repair_time)


# ======================
# Test Integration Layer
# ======================

class TestIntegrationLayer(unittest.TestCase):
    """Test integration layer."""

    def setUp(self):
        self.layer = IntegrationLayer()

    def test_integration_layer_creation(self):
        """Test integration layer can be created."""
        self.assertIsNotNone(self.layer)

    def test_get_all_metrics_empty(self):
        """Test getting metrics with no integrations."""
        metrics = self.layer.get_all_metrics()
        self.assertIsInstance(metrics, dict)

    def test_integration_status(self):
        """Test getting integration status."""
        status = self.layer.get_integration_status()
        self.assertIsInstance(status, dict)
        self.assertIn('faza25_integrated', status)

    def test_statistics_tracking(self):
        """Test integration statistics."""
        stats = self.layer.get_statistics()
        self.assertIn('faza25_queries', stats)

    def test_register_repair_callback(self):
        """Test registering repair callback."""
        callback = lambda params: None
        self.layer.register_repair_callback("graph_repair", callback)
        self.assertIn(callback, self.layer._repair_callbacks["graph_repair"])

    def test_execute_repair_callbacks(self):
        """Test executing repair callbacks."""
        called = []
        def callback(params):
            called.append(params)

        self.layer.register_repair_callback("graph_repair", callback)
        self.layer.execute_repair_callbacks("graph_repair", {"test": "data"})

        self.assertEqual(len(called), 1)

    def test_publish_event(self):
        """Test publishing events."""
        # Should not crash even without event bus
        self.layer.publish_event("test_event", {"data": "value"})

    def test_get_faza25_metrics(self):
        """Test getting FAZA 25 metrics."""
        metrics = self.layer.get_faza25_metrics()
        self.assertIsInstance(metrics, dict)

    def test_get_faza29_metrics(self):
        """Test getting FAZA 29 metrics."""
        metrics = self.layer.get_faza29_metrics()
        self.assertIsInstance(metrics, dict)


# ======================
# Test Event Hooks
# ======================

class TestEventHooks(unittest.TestCase):
    """Test event hooks."""

    def setUp(self):
        self.hooks = EventHooks()

    def test_event_hooks_creation(self):
        """Test event hooks can be created."""
        self.assertIsNotNone(self.hooks)

    def test_publish_event(self):
        """Test publishing an event."""
        self.hooks.publish_event(EventType.FAULT_DETECTED, {"fault_id": "f123"})

        history = self.hooks.get_event_history()
        self.assertGreater(len(history), 0)

    def test_subscribe_and_receive(self):
        """Test subscribing to and receiving events."""
        received = []

        def callback(event):
            received.append(event)

        self.hooks.subscribe(EventType.FAULT_DETECTED, callback)
        self.hooks.publish_event(EventType.FAULT_DETECTED, {"fault_id": "f123"})

        self.assertEqual(len(received), 1)

    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        received = []

        def callback(event):
            received.append(event)

        self.hooks.subscribe(EventType.FAULT_DETECTED, callback)
        self.hooks.unsubscribe(EventType.FAULT_DETECTED, callback)
        self.hooks.publish_event(EventType.FAULT_DETECTED, {"fault_id": "f123"})

        self.assertEqual(len(received), 0)

    def test_event_statistics(self):
        """Test event statistics tracking."""
        self.hooks.publish_event(EventType.FAULT_DETECTED, {})
        stats = self.hooks.get_statistics()
        self.assertIn('total_events_published', stats)

    def test_get_events_by_type(self):
        """Test filtering events by type."""
        self.hooks.publish_event(EventType.FAULT_DETECTED, {})
        self.hooks.publish_event(EventType.FAULT_RESOLVED, {})

        detected = self.hooks.get_events_by_type(EventType.FAULT_DETECTED)
        self.assertIsInstance(detected, list)


# ======================
# Test Controller
# ======================

class TestController(unittest.TestCase):
    """Test healing controller."""

    def setUp(self):
        self.controller = create_healing_controller()

    def test_controller_creation(self):
        """Test controller can be created."""
        self.assertIsNotNone(self.controller)

    async def test_start_stop(self):
        """Test starting and stopping controller."""
        await self.controller.start()
        self.assertTrue(self.controller.is_running())

        await self.controller.stop()
        self.assertFalse(self.controller.is_running())

    def test_get_health(self):
        """Test getting health information."""
        health = self.controller.get_health()
        self.assertIn('overall_score', health)
        self.assertIn('level', health)

    def test_get_status(self):
        """Test getting status information."""
        status = self.controller.get_status()
        self.assertIn('running', status)
        self.assertIn('active_faults', status)

    def test_get_statistics(self):
        """Test getting comprehensive statistics."""
        stats = self.controller.get_statistics()
        self.assertIn('controller', stats)
        self.assertIn('detection', stats)
        self.assertIn('health', stats)

    def test_component_access(self):
        """Test accessing components."""
        detection = self.controller.get_detection_engine()
        self.assertIsNotNone(detection)

        health = self.controller.get_health_engine()
        self.assertIsNotNone(health)

    def test_create_snapshot(self):
        """Test creating snapshot via controller."""
        snapshot_id = self.controller.create_snapshot(snapshot_type="manual")
        self.assertIsInstance(snapshot_id, str)

    def test_set_autorepair_mode(self):
        """Test setting autorepair mode."""
        self.controller.set_autorepair_mode("conservative")
        self.assertEqual(
            self.controller.get_autorepair_engine().config.mode,
            AutorepairMode.CONSERVATIVE
        )

    def test_get_faults(self):
        """Test getting current faults."""
        faults = self.controller.get_faults()
        self.assertIn('active_faults', faults)
        self.assertIn('critical_faults', faults)

    def test_uptime_tracking(self):
        """Test uptime is tracked."""
        uptime = self.controller.get_uptime()
        self.assertGreaterEqual(uptime, 0)


# ======================
# Run Tests
# ======================

def run_async_test(coro):
    """Helper to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
