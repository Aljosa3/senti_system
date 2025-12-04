# FAZA 30 - Enterprise Self-Healing Engine
## Complete Documentation

**Version:** 1.0.0
**Status:** ✅ PRODUCTION READY
**Date:** 2024-12-04

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Integration Guide](#integration-guide)
8. [Event System](#event-system)
9. [Troubleshooting](#troubleshooting)
10. [Performance Tuning](#performance-tuning)
11. [Best Practices](#best-practices)
12. [FAQ](#faq)

---

## Overview

### What is FAZA 30?

FAZA 30 is the Enterprise Self-Healing Engine for Senti OS, providing automated fault detection, classification, and repair capabilities across all system layers.

### Key Features

- **Automatic Fault Detection**: Monitors all FAZA layers (25/27/27.5/28/28.5/29)
- **5-Category Classification**: Intelligent fault taxonomy
- **4 Repair Engines**: Specialized repair strategies
- **12-Step Healing Pipeline**: Orchestrated healing workflow
- **Health Scoring (0-100)**: Real-time system health assessment
- **Snapshot/Rollback**: State preservation and recovery
- **Healing Throttle**: Prevents repair storms
- **Non-Intrusive Integration**: Optional integration with other layers

### System Requirements

- Python 3.8+
- No external dependencies (stdlib only)
- FAZA 25/27/28/28.5/29 (optional)
- Disk space for snapshots (~/.senti_system/snapshots/)

---

## Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              FAZA 30 Healing Controller                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │   Detection    │  │Classification  │  │ Repair Engines │ │
│  │    Engine      │  │    Engine      │  │   (Graph,      │ │
│  │  (All FAZA)    │  │  (5 Categories)│  │   Agent,       │ │
│  └───────┬────────┘  └───────┬────────┘  │   Scheduler,   │ │
│          │                   │            │   Governance)  │ │
│          └──────────┬────────┘            └───────┬────────┘ │
│                     │                             │          │
│          ┌──────────┴─────────────────────────────┘          │
│          │                                                   │
│  ┌───────▼─────────────────────────────────────────────┐    │
│  │          12-Step Healing Pipeline                   │    │
│  │  1.Detect → 2.Classify → 3.Snapshot → 4.Select     │    │
│  │  5.Prepare → 6.Repair → 7.Verify → 8.HealthCheck   │    │
│  │  9.Rollback → 10.Stabilize → 11.Learn → 12.Report  │    │
│  └───────────────────────────────────────────────────┬─┘    │
│                                                       │      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────▼────┐ │
│  │   Snapshot   │  │    Health    │  │   Autorepair      │ │
│  │   Manager    │  │    Engine    │  │    Engine         │ │
│  │ (~/.senti/)  │  │ (Score 0-100)│  │ (Continuous Loop) │ │
│  └──────────────┘  └──────────────┘  └───────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           Integration Layer & Event Hooks              │  │
│  │   FAZA 25 | FAZA 27/27.5 | FAZA 28 | FAZA 28.5/29    │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User/System → Controller.start()
                 ↓
        Autorepair Engine (continuous loop)
                 ↓
        Integration Layer (gather metrics)
                 ↓
        Detection Engine (detect faults)
                 ↓
        Classification Engine (categorize)
                 ↓
        Healing Pipeline (12 steps)
                 ↓
        Repair Engines (fix faults)
                 ↓
        Health Engine (verify improvement)
                 ↓
        Event Hooks (notify results)
```

---

## Core Components

### 1. Detection Engine

**Purpose**: Detect faults from all FAZA layers

**Features**:
- Multi-layer fault detection
- Predictive failure analysis
- Anomaly detection (z-score)
- Severity classification
- Active fault tracking

**Detects**:
- FAZA 25: Queue backlogs, resource exhaustion
- FAZA 27: Cycles, bottlenecks, complexity
- FAZA 28: Agent failures, cooperation issues
- FAZA 28.5: Stability threats, anomalies
- FAZA 29: High risk, governance violations

### 2. Classification Engine

**Purpose**: Classify faults into actionable categories

**5 Categories**:
1. **OPERATIONAL**: Runtime execution issues
2. **STRUCTURAL**: Graph/topology problems
3. **AGENT_FAULT**: Agent-specific failures
4. **GOVERNANCE_DRIFT**: Policy violations
5. **STABILITY_THREAT**: System stability risks

**Output**:
- Category with confidence score
- Repair priority (IMMEDIATE/URGENT/HIGH/MEDIUM/LOW/DEFERRED)
- Root cause analysis
- Affected components
- Recommended actions

### 3. Repair Engines

**4 Specialized Engines**:

#### GraphRepairEngine
- Repairs: Cycles, bottlenecks, deadlocks
- Strategy: Break dependencies, parallelize, simplify

#### AgentRepairEngine
- Repairs: Crashes, cooperation, communication
- Strategy: Restart, reset protocols, flush queues

#### SchedulerRepairEngine
- Repairs: Timeouts, resource exhaustion, backlogs
- Strategy: Retry, throttle, redistribute

#### GovernanceRepairEngine
- Repairs: Policy violations, threshold breaches
- Strategy: Revert policies, adjust thresholds

### 4. Healing Pipeline

**12-Step Process**:

```
Stage 1:  DETECT       - Detect faults from all layers
Stage 2:  CLASSIFY     - Classify fault category
Stage 3:  SNAPSHOT     - Take pre-repair snapshot
Stage 4:  SELECT       - Select repair strategy
Stage 5:  PREPARE      - Prepare repair context
Stage 6:  EXECUTE      - Execute repair action
Stage 7:  VERIFY       - Verify repair success
Stage 8:  HEALTH CHECK - Check post-repair health
Stage 9:  ROLLBACK     - Rollback if health declined
Stage 10: STABILIZE    - Allow system stabilization
Stage 11: LEARN        - Extract learnings
Stage 12: REPORT       - Generate report
```

### 5. Snapshot Manager

**Purpose**: System state capture and rollback

**Features**:
- State snapshots to `~/.senti_system/snapshots/`
- Multiple snapshot types (PRE_REPAIR, MANUAL, EMERGENCY)
- Snapshot verification
- Automatic cleanup (max 50 snapshots by default)
- Restore capability

**Storage**:
```
~/.senti_system/snapshots/
├── snap_20241204_143022_123456.json
├── snap_20241204_143045_789012.json
└── ...
```

### 6. Health Engine

**Purpose**: System health scoring and trend analysis

**Health Score (0-100)**:
- 90-100: EXCELLENT
- 75-89: GOOD
- 60-74: FAIR
- 40-59: POOR
- 0-39: CRITICAL

**Components** (weighted):
- FAZA 25 Orchestrator: 20%
- FAZA 27 TaskGraph: 20%
- FAZA 28 Agent Loop: 20%
- FAZA 28.5 Meta Layer: 15%
- FAZA 29 Governance: 15%
- FAZA 30 Self-Healing: 10%

**Trend Analysis**:
- IMPROVING: Health increasing
- STABLE: Health stable
- DECLINING: Health decreasing
- VOLATILE: Health fluctuating

### 7. Autorepair Engine

**Purpose**: Continuous self-healing loop

**Modes**:
- **AGGRESSIVE**: Repair all faults immediately
- **BALANCED**: Normal operation (default)
- **CONSERVATIVE**: Only critical faults
- **DISABLED**: No automatic repairs

**Throttle Protection**:
- Max repairs per minute: 10 (default)
- Max repairs per hour: 50 (default)
- Cooldown: 3 seconds (default)

**States**:
- NORMAL: Normal operation
- THROTTLED: Healing slowed (only critical)
- BLOCKED: Too many repairs, healing paused

### 8. Integration Layer

**Purpose**: Non-intrusive FAZA integration

**Integrations**:
- FAZA 25: Queue metrics, scheduler stats
- FAZA 27/27.5: Graph metrics, optimization
- FAZA 28: Agent stats, communication health
- FAZA 28.5: Stability, policy effectiveness
- FAZA 29: Risk score, governance status

**Features**:
- Optional integration (graceful degradation)
- Metric collection
- Repair action callbacks
- Event bus integration

### 9. Event Hooks

**Purpose**: Type-safe event system

**Event Categories**:
- Detection (4 events)
- Classification (2 events)
- Repair (4 events)
- Healing (4 events)
- Health (4 events)
- Snapshot (3 events)
- Autorepair (6 events)
- Controller (4 events)

**Total**: 31 event types

### 10. Healing Controller

**Purpose**: High-level unified API

**Features**:
- Component initialization
- Lifecycle management
- Global singleton support
- Comprehensive statistics
- Unified API

---

## API Reference

### Controller API

#### Basic Usage

```python
from senti_os.core.faza30 import get_healing_controller

# Get controller
controller = get_healing_controller()

# Start autorepair
await controller.start()

# Get health
health = controller.get_health()

# Stop
await controller.stop()
```

#### Controller Methods

##### `get_healing_controller(...) -> HealingController`

Get global singleton controller instance.

**Parameters**:
- `faza25_orchestrator`: Optional FAZA 25 Orchestrator
- `faza27_task_graph`: Optional FAZA 27 TaskGraph
- `faza27_5_optimizer`: Optional FAZA 27.5 Optimizer
- `faza28_agent_loop`: Optional FAZA 28 AgentLoop
- `faza28_5_meta_layer`: Optional FAZA 28.5 MetaLayer
- `faza29_governance`: Optional FAZA 29 Governance
- `event_bus`: Optional FAZA 28 EventBus
- `autorepair_config`: Optional AutorepairConfig
- `force_new`: Force creation of new instance

**Returns**: `HealingController`

##### `async start() -> None`

Start autorepair engine (enables continuous healing).

##### `async stop() -> None`

Stop autorepair engine.

##### `get_health() -> Dict[str, Any]`

Get current system health.

**Returns**:
```python
{
    "overall_score": 85.5,
    "level": "good",
    "components": [
        {
            "name": "faza25_orchestrator",
            "score": 90.0,
            "weight": 0.20
        },
        ...
    ],
    "trend": {
        "direction": "stable",
        "slope": 0.05,
        "confidence": 0.85,
        "prediction": 86.0
    },
    "timestamp": "2024-12-04T14:30:22.123456"
}
```

##### `get_status() -> Dict[str, Any]`

Get comprehensive system status.

**Returns**:
```python
{
    "running": True,
    "uptime_seconds": 3600.5,
    "autorepair_mode": "balanced",
    "throttle_state": "normal",
    "active_faults": 2,
    "critical_faults": 0,
    "recent_healing_cycles": 5,
    "last_healing_success": "success",
    "integration_status": {...},
    "timestamp": "..."
}
```

##### `get_statistics() -> Dict[str, Any]`

Get comprehensive statistics from all components.

**Returns**: Dict with statistics from:
- controller
- detection
- classification
- repair (all 4 engines)
- pipeline
- snapshots
- health
- autorepair
- integration
- events

##### `force_healing_cycle() -> Dict[str, Any]`

Force immediate healing cycle (bypasses throttle).

**Returns**: Healing result

##### `create_snapshot(snapshot_type: str = "manual") -> str`

Create system snapshot.

**Returns**: Snapshot ID

##### `restore_snapshot(snapshot_id: str) -> bool`

Restore from snapshot.

**Returns**: True if successful

##### `set_autorepair_mode(mode: str) -> None`

Change autorepair mode.

**Parameters**: mode ("aggressive" | "balanced" | "conservative" | "disabled")

##### `get_faults(include_resolved: bool = False) -> Dict[str, Any]`

Get current faults.

**Returns**:
```python
{
    "active_faults": 2,
    "critical_faults": 0,
    "faults": [
        {
            "fault_id": "f_123",
            "source": "faza27_taskgraph",
            "severity": "high",
            "fault_type": "cycle_detected",
            "description": "Circular dependency detected"
        },
        ...
    ]
}
```

### Component Access Methods

```python
# Get individual components
detection = controller.get_detection_engine()
classification = controller.get_classification_engine()
repair_engines = controller.get_repair_engines()
pipeline = controller.get_healing_pipeline()
snapshots = controller.get_snapshot_manager()
health = controller.get_health_engine()
autorepair = controller.get_autorepair_engine()
integration = controller.get_integration_layer()
events = controller.get_event_hooks()
```

---

## Usage Examples

### Example 1: Basic Autorepair

```python
import asyncio
from senti_os.core.faza30 import get_healing_controller

async def main():
    # Get controller
    controller = get_healing_controller()

    # Start autorepair
    await controller.start()

    print("Autorepair started in balanced mode")

    # Let it run for some time
    await asyncio.sleep(60)

    # Check health
    health = controller.get_health()
    print(f"System health: {health['overall_score']}/100 ({health['level']})")

    # Stop
    await controller.stop()

asyncio.run(main())
```

### Example 2: Manual Healing Cycle

```python
from senti_os.core.faza30 import get_healing_controller

# Get controller
controller = get_healing_controller()

# Check current health
health_before = controller.get_health()
print(f"Health before: {health_before['overall_score']}")

# Force healing cycle
result = controller.force_healing_cycle()
print(f"Healing outcome: {result}")

# Check health after
health_after = controller.get_health()
print(f"Health after: {health_after['overall_score']}")
print(f"Improvement: +{health_after['overall_score'] - health_before['overall_score']}")
```

### Example 3: Snapshot and Rollback

```python
from senti_os.core.faza30 import get_healing_controller

controller = get_healing_controller()

# Create snapshot before making changes
snapshot_id = controller.create_snapshot(snapshot_type="manual")
print(f"Created snapshot: {snapshot_id}")

# ... system runs, changes happen ...

# If something goes wrong, restore
success = controller.restore_snapshot(snapshot_id)
if success:
    print("Successfully restored to snapshot")
else:
    print("Restore failed")
```

### Example 4: Health Monitoring

```python
from senti_os.core.faza30 import get_healing_controller
import time

controller = get_healing_controller()

while True:
    health = controller.get_health()

    print(f"Overall: {health['overall_score']:.1f}/100 ({health['level']})")
    print(f"Trend: {health['trend']['direction']} (slope: {health['trend']['slope']:.2f})")

    # Check components
    for component in health['components']:
        print(f"  {component['name']}: {component['score']:.1f}")

    if health['level'] == "critical":
        print("⚠️ CRITICAL HEALTH - Triggering emergency healing")
        controller.force_healing_cycle()

    time.sleep(10)
```

### Example 5: Event Subscription

```python
from senti_os.core.faza30 import get_healing_controller, EventType

controller = get_healing_controller()
events = controller.get_event_hooks()

# Subscribe to fault detection
def on_fault_detected(event):
    fault_id = event.data.get('fault_id')
    severity = event.data.get('severity')
    print(f"⚠️ Fault detected: {fault_id} (severity: {severity})")

events.subscribe(EventType.FAULT_DETECTED, on_fault_detected)

# Subscribe to healing completion
def on_healing_completed(event):
    outcome = event.data.get('outcome')
    faults_repaired = event.data.get('faults_repaired')
    print(f"✓ Healing completed: {outcome} ({faults_repaired} faults repaired)")

events.subscribe(EventType.HEALING_CYCLE_COMPLETED, on_healing_completed)

# Now events will be received as they occur
```

### Example 6: Custom Autorepair Configuration

```python
import asyncio
from senti_os.core.faza30 import get_healing_controller, AutorepairConfig, AutorepairMode

async def main():
    # Custom configuration
    config = AutorepairConfig(
        mode=AutorepairMode.AGGRESSIVE,
        interval_seconds=2.0,
        max_repairs_per_minute=20,
        max_repairs_per_hour=100,
        cooldown_seconds=1.0,
        enable_snapshots=True,
        enable_rollback=True
    )

    controller = get_healing_controller(autorepair_config=config)

    # Start with aggressive mode
    await controller.start()

    print("Started aggressive autorepair")

    # ... run for a while ...

    # Switch to conservative mode if needed
    controller.set_autorepair_mode("conservative")
    print("Switched to conservative mode")

    await controller.stop()

asyncio.run(main())
```

### Example 7: FAZA Integration

```python
from senti_os.core.faza30 import get_healing_controller

# Assume we have other FAZA components
from senti_os.core.faza25 import get_orchestrator
from senti_os.core.faza29 import get_governance_controller

# Get other FAZA controllers
orchestrator = get_orchestrator()
governance = get_governance_controller()

# Create integrated healing controller
controller = get_healing_controller(
    faza25_orchestrator=orchestrator,
    faza29_governance=governance
)

# Now FAZA 30 will monitor FAZA 25 and FAZA 29
await controller.start()

# Healing will automatically detect and fix issues in integrated layers
```

---

## Configuration

### AutorepairConfig

```python
from senti_os.core.faza30 import AutorepairConfig, AutorepairMode

config = AutorepairConfig(
    mode=AutorepairMode.BALANCED,           # Operation mode
    interval_seconds=5.0,                   # Monitoring interval
    max_repairs_per_minute=10,              # Throttle limit
    max_repairs_per_hour=50,                # Hourly limit
    cooldown_seconds=3.0,                   # Cooldown after repair
    min_health_for_repair=20.0,             # Min health threshold
    enable_snapshots=True,                  # Pre-repair snapshots
    enable_rollback=True                    # Automatic rollback
)
```

### Environment Variables

FAZA 30 respects the following environment variables:

- `FAZA30_SNAPSHOT_DIR`: Snapshot directory (default: `~/.senti_system/snapshots/`)
- `FAZA30_MAX_SNAPSHOTS`: Maximum snapshots to keep (default: 50)
- `FAZA30_AUTOREPAIR_INTERVAL`: Monitoring interval in seconds (default: 5.0)

---

## Integration Guide

### Integration with FAZA 25 (Orchestrator)

```python
from senti_os.core.faza25 import get_orchestrator
from senti_os.core.faza30 import get_healing_controller

orchestrator = get_orchestrator()

controller = get_healing_controller(
    faza25_orchestrator=orchestrator
)

# FAZA 30 will now monitor:
# - Queue size
# - Task success rate
# - Scheduler efficiency
# - Resource usage
```

### Integration with FAZA 27 (Task Graph)

```python
from senti_os.core.faza27 import TaskGraph
from senti_os.core.faza30 import get_healing_controller

task_graph = TaskGraph()

controller = get_healing_controller(
    faza27_task_graph=task_graph
)

# FAZA 30 will detect and repair:
# - Circular dependencies
# - Graph bottlenecks
# - Excessive complexity
```

### Integration with FAZA 29 (Governance)

```python
from senti_os.core.faza29 import get_governance_controller
from senti_os.core.faza30 import get_healing_controller

governance = get_governance_controller()

controller = get_healing_controller(
    faza29_governance=governance
)

# FAZA 30 will monitor:
# - Risk score
# - Governance violations
# - Takeover state
# - Override usage
```

### Full Integration Example

```python
from senti_os.core.faza25 import get_orchestrator
from senti_os.core.faza27 import TaskGraph
from senti_os.core.faza28 import AgentExecutionLoop
from senti_os.core.faza28_5 import MetaLayer
from senti_os.core.faza29 import get_governance_controller
from senti_os.core.faza30 import get_healing_controller

# Get all FAZA components
orchestrator = get_orchestrator()
task_graph = TaskGraph()
agent_loop = AgentExecutionLoop()
meta_layer = MetaLayer()
governance = get_governance_controller()

# Create fully integrated healing controller
controller = get_healing_controller(
    faza25_orchestrator=orchestrator,
    faza27_task_graph=task_graph,
    faza28_agent_loop=agent_loop,
    faza28_5_meta_layer=meta_layer,
    faza29_governance=governance
)

# Now FAZA 30 monitors and heals all layers
await controller.start()
```

---

## Event System

### Available Events

**Detection Events**:
- `FAULT_DETECTED`
- `FAULT_RESOLVED`
- `CRITICAL_FAULT`
- `PREDICTION_MADE`

**Repair Events**:
- `REPAIR_STARTED`
- `REPAIR_COMPLETED`
- `REPAIR_FAILED`
- `REPAIR_VERIFIED`

**Healing Events**:
- `HEALING_CYCLE_STARTED`
- `HEALING_CYCLE_COMPLETED`
- `HEALING_CYCLE_FAILED`
- `ROLLBACK_PERFORMED`

**Health Events**:
- `HEALTH_COMPUTED`
- `HEALTH_DEGRADED`
- `HEALTH_IMPROVED`
- `HEALTH_CRITICAL`

**Autorepair Events**:
- `AUTOREPAIR_STARTED`
- `AUTOREPAIR_STOPPED`
- `AUTOREPAIR_THROTTLED`
- `AUTOREPAIR_BLOCKED`

### Event Subscription

```python
from senti_os.core.faza30 import get_healing_controller, EventType

controller = get_healing_controller()
events = controller.get_event_hooks()

def my_callback(event):
    print(f"Event: {event.event_type}")
    print(f"Data: {event.data}")
    print(f"Time: {event.timestamp}")

events.subscribe(EventType.FAULT_DETECTED, my_callback)
```

---

## Troubleshooting

### Problem: Healing Not Starting

**Symptoms**:
- `controller.is_running()` returns False after `start()`
- No healing cycles execute

**Solutions**:
1. Check if async start was awaited: `await controller.start()`
2. Verify autorepair mode is not DISABLED
3. Check logs for initialization errors

### Problem: Too Many Repairs (Repair Storm)

**Symptoms**:
- Throttle state shows BLOCKED
- Many repairs per minute
- System unstable

**Solutions**:
1. Reduce `max_repairs_per_minute` in config
2. Increase `cooldown_seconds`
3. Switch to CONSERVATIVE mode
4. Check for underlying system issues

### Problem: Health Not Improving

**Symptoms**:
- Health score stays low
- Repairs complete but no improvement

**Solutions**:
1. Check if correct FAZA layers are integrated
2. Verify repair engines are working: `get_statistics()`
3. Check if faults are being detected: `get_faults()`
4. Review recent healing cycles: `pipeline.get_recent_cycles()`

### Problem: Snapshots Not Creating

**Symptoms**:
- Snapshot directory empty
- Rollback fails

**Solutions**:
1. Check snapshot directory permissions: `~/.senti_system/snapshots/`
2. Verify `enable_snapshots=True` in config
3. Check disk space
4. Review snapshot manager statistics

### Problem: High CPU Usage

**Symptoms**:
- FAZA 30 consuming excessive CPU

**Solutions**:
1. Increase `interval_seconds` (reduce monitoring frequency)
2. Switch to CONSERVATIVE mode
3. Disable predictive failure analysis if not needed
4. Check for integration layer issues

---

## Performance Tuning

### For High-Frequency Systems

```python
config = AutorepairConfig(
    interval_seconds=1.0,              # Monitor frequently
    max_repairs_per_minute=20,         # Allow more repairs
    max_repairs_per_hour=100,
    cooldown_seconds=0.5,              # Shorter cooldown
    mode=AutorepairMode.AGGRESSIVE     # Fix quickly
)
```

### For Resource-Constrained Systems

```python
config = AutorepairConfig(
    interval_seconds=10.0,             # Monitor less frequently
    max_repairs_per_minute=5,          # Limit repairs
    max_repairs_per_hour=30,
    cooldown_seconds=5.0,              # Longer cooldown
    mode=AutorepairMode.CONSERVATIVE   # Only critical
)
```

### For Production Systems

```python
config = AutorepairConfig(
    interval_seconds=5.0,              # Balanced monitoring
    max_repairs_per_minute=10,         # Standard limit
    max_repairs_per_hour=50,
    cooldown_seconds=3.0,              # Standard cooldown
    enable_snapshots=True,             # Always snapshot
    enable_rollback=True,              # Auto rollback
    mode=AutorepairMode.BALANCED       # Balanced approach
)
```

---

## Best Practices

### 1. Always Use Snapshots in Production

```python
# GOOD
config = AutorepairConfig(enable_snapshots=True, enable_rollback=True)

# BAD (for production)
config = AutorepairConfig(enable_snapshots=False)
```

### 2. Start with BALANCED Mode

```python
# Start conservative, increase aggressiveness as needed
controller.set_autorepair_mode("balanced")
```

### 3. Monitor Health Trends

```python
health = controller.get_health()
if health['trend']['direction'] == 'declining':
    # Investigate before it becomes critical
    print("Health declining - check faults")
```

### 4. Subscribe to Critical Events

```python
def on_critical_health(event):
    # Alert operations team
    send_alert("CRITICAL: System health critical!")

events.subscribe(EventType.HEALTH_CRITICAL, on_critical_health)
```

### 5. Regular Health Checks

```python
# Check health every 30 seconds
import asyncio

async def health_monitor():
    while True:
        health = controller.get_health()
        log_health(health)
        await asyncio.sleep(30)
```

### 6. Use Statistics for Insights

```python
# Review statistics daily
stats = controller.get_statistics()
print(f"Repairs successful: {stats['repair']['graph']['successful_repairs']}")
print(f"Average health: {stats['health']['avg_health']}")
```

### 7. Integration is Optional

```python
# Start simple, add integrations as needed
controller = get_healing_controller()  # Works standalone

# Later, add FAZA 29 integration
controller = get_healing_controller(
    faza29_governance=governance
)
```

---

## FAQ

### Q: Does FAZA 30 require other FAZA layers?

**A**: No. FAZA 30 works standalone and provides self-healing even without other FAZA layers. Integration is optional and enhances capabilities.

### Q: Can I disable autorepair temporarily?

**A**: Yes, use `controller.set_autorepair_mode("disabled")` to disable automatic repairs while keeping monitoring active.

### Q: How do snapshots affect performance?

**A**: Minimal impact. Snapshots are lightweight JSON files and creation takes < 100ms typically.

### Q: What happens if healing makes things worse?

**A**: FAZA 30 checks health after repair. If health declines, it automatically rolls back to the pre-repair snapshot.

### Q: Can I extend FAZA 30 with custom repair engines?

**A**: Yes, create a custom repair engine inheriting from `RepairStrategy` and add it to the `repair_engines` dict.

### Q: How is FAZA 30 different from FAZA 29?

**A**: FAZA 29 is governance (risk management, rules, takeover). FAZA 30 is self-healing (fault detection, repair, recovery). They complement each other.

### Q: What's the overhead of FAZA 30?

**A**: Minimal. Default config with 5-second interval uses < 1% CPU and < 50MB RAM typically.

### Q: Can I use FAZA 30 in distributed systems?

**A**: Currently FAZA 30 is designed for single-system self-healing. For distributed healing, run one instance per node.

### Q: How do I know if healing is working?

**A**: Check `get_statistics()` for repair counts, and `get_health()` for health trend. If trend is IMPROVING or STABLE, healing is effective.

### Q: Can I manually trigger repairs?

**A**: Yes, use `force_healing_cycle()` to trigger immediate healing, bypassing throttle and cooldown.

---

## Conclusion

FAZA 30 Enterprise Self-Healing Engine provides comprehensive, automated fault recovery for Senti OS. With intelligent detection, classification, and repair across all system layers, it ensures high availability and system stability.

**Key Takeaways**:
- ✅ Zero-configuration default setup
- ✅ Optional integration with all FAZA layers
- ✅ Automatic throttle prevents repair storms
- ✅ Snapshot/rollback protects against bad repairs
- ✅ Health monitoring ensures effectiveness
- ✅ Production-ready enterprise features

For support or questions, consult the FAZA 30 test suite or review the inline documentation in source code.

---

**FAZA 30 - Enterprise Self-Healing Engine**
*Version 1.0.0 - Production Ready* ✅
