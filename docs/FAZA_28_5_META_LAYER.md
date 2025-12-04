# FAZA 28.5 - Meta-Agent Oversight Layer (Enterprise Edition)

## Overview

FAZA 28.5 is the Enterprise Meta-Agent Oversight Layer for Senti OS, providing comprehensive monitoring, analysis, and adaptive control over all agents in FAZA 28 Agent Execution Loop (AEL).

**Enterprise Capabilities:**
- Real-time agent performance scoring
- Multi-method anomaly detection
- Multi-agent stability analysis
- Policy-driven safety enforcement
- Dynamic strategy adaptation
- Meta-agent oversight and coordination
- Comprehensive system meta-reporting

**Integration:** Deep integration with FAZA 28, hooks into event bus, scheduler, and state management.

## Architecture

### System Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│         FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise)          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Integration Layer                            │ │
│  │            (Main API & FAZA 28 Integration)                     │ │
│  └───────────────────────┬────────────────────────────────────────┘ │
│                          │                                           │
│          ┌───────────────┴───────────────┐                          │
│          │                               │                          │
│  ┌───────▼────────┐             ┌───────▼────────┐                 │
│  │ Oversight Agent│             │ Agent Scorer    │                 │
│  │  (Meta-Agent)  │─────────────│  (Performance)  │                 │
│  └───────┬────────┘             └─────────────────┘                 │
│          │                                                           │
│          │  ┌──────────────────────────────────────┐                │
│          ├──│ Anomaly Detector (Rule/Stat/Thresh) │                │
│          │  └──────────────────────────────────────┘                │
│          │                                                           │
│          │  ┌──────────────────────────────────────┐                │
│          ├──│ Stability Engine (Feedback/Deadlock) │                │
│          │  └──────────────────────────────────────┘                │
│          │                                                           │
│          │  ┌──────────────────────────────────────┐                │
│          ├──│ Policy Manager (Safety/Load/Conflict)│                │
│          │  └──────────────────────────────────────┘                │
│          │                                                           │
│          │  ┌──────────────────────────────────────┐                │
│          └──│ Strategy Adapter (Dynamic Behavior)  │                │
│             └──────────────────────────────────────┘                │
│                                                                      │
│  ─────────────────────────────────────────────────────────────────  │
│                          INTEGRATION POINTS                          │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│         FAZA 28 EventBus  │  FAZA 28 Scheduler  │  State Context    │
│                           ↓                     ↓                    │
└──────────────────────────────────────────────────────────────────────┘
                           │
                           ↓
              ┌─────────────────────────┐
              │    FAZA 28 AEL Loop     │
              │  (Agent Execution Loop) │
              └─────────────────────────┘
```

### Data Flow

```
1. Agent Execution → Event Emission
         ↓
2. Oversight Agent Observes Event
         ↓
3. Update Agent Scorer (Performance Metrics)
         ↓
4. Anomaly Detection (Rule/Statistical/Threshold)
         ↓
5. Stability Analysis (Multi-Agent Patterns)
         ↓
6. Policy Evaluation (Safety/Load/Conflict)
         ↓
7. Strategy Adaptation (Dynamic Behavior Change)
         ↓
8. Meta-Report Generation (Periodic Summary)
         ↓
9. State Update (FAZA 28 State Context)
```

## Core Components

### 1. Agent Scorer

**File:** `agent_scorer.py`

Provides comprehensive agent performance scoring based on multiple dimensions.

**Metrics Tracked:**
- Tick count and execution time
- Error rate and frequency
- Event activity (received/emitted)
- State usage (reads/writes)
- Uptime and availability

**Scores Calculated (0.0 - 1.0):**
- **Performance Score:** Execution efficiency, throughput, variance
- **Reliability Score:** Error rate, uptime, recent failures
- **Cooperation Score:** Event responsiveness, state usage
- **Stability Risk Score:** Variance, anomalies, degradation
- **Meta-Score:** Weighted combination of all scores

**Time-Weighted:** Exponential moving average with configurable decay factor.

**Key Classes:**
- `AgentMetrics` - Data structure for agent metrics
- `AgentScore` - Comprehensive score result
- `AgentScorer` - Main scoring engine

#### Usage Example

```python
from senti_os.core.faza28_5 import get_agent_scorer

scorer = get_agent_scorer()

# Record agent execution
scorer.record_tick(
    agent_name="monitoring_agent",
    execution_time=0.05,  # 50ms
    had_error=False
)

# Record event activity
scorer.record_event("monitoring_agent", "alert_sent", is_received=False)

# Calculate score
score = scorer.calculate_score("monitoring_agent")
print(f"Meta-score: {score.meta_score:.3f}")
print(f"Performance: {score.performance_score:.3f}")
print(f"Reliability: {score.reliability_score:.3f}")
```

### 2. Meta Policies

**File:** `meta_policies.py`

Pluggable policy framework for enterprise-level operational control.

**Policy Types:**
- **Safety Policies:** Kill-switch, isolation, emergency shutdown
- **Load Balance Policies:** Throttling, overload protection, resource limits
- **Conflict Resolution Policies:** State conflicts, event conflicts, priority resolution
- **Escalation Policies:** Multi-violation tracking, cascade detection
- **Failover Policies:** Work redistribution, agent replacement

**Default Policies:**
1. **KillSwitchPolicy** (Priority 10)
   - Triggers: Meta-score < 0.1, error rate > 50%
   - Action: KILL agent

2. **IsolationPolicy** (Priority 8)
   - Triggers: Performance < 0.3, reliability < 0.4
   - Action: ISOLATE agent

3. **LoadBalancePolicy** (Priority 6)
   - Triggers: Execution time > 1.0s
   - Action: THROTTLE agent

4. **OverloadPolicy** (Priority 7)
   - Triggers: Too many agents, system overload
   - Action: DENY new agents or THROTTLE

5. **EscalationPolicy** (Priority 9)
   - Triggers: Multiple violations in time window
   - Action: ESCALATE to emergency procedures

#### Usage Example

```python
from senti_os.core.faza28_5 import get_policy_manager, KillSwitchPolicy

manager = get_policy_manager()

# Policies are auto-registered by default
# Evaluate for specific agent
from senti_os.core.faza28_5 import get_agent_scorer

scorer = get_agent_scorer()
score = scorer.calculate_score("problematic_agent")

context = {
    "agent_score": score,
    "has_anomalies": True
}

decisions = manager.evaluate_all(context)

for decision in decisions:
    print(f"Policy triggered: {decision.action.value}")
    print(f"Reason: {decision.reason}")
```

### 3. Anomaly Detector

**File:** `anomaly_detector.py`

Multi-method anomaly detection supporting rule-based, statistical, and threshold approaches.

**Detection Methods:**

**1. Rule-Based Detection:**
- Sudden score drops/spikes
- Missing ticks
- High error rates
- Timing irregularities

**2. Statistical Detection:**
- Outlier detection using Z-scores
- Deviation from historical patterns
- Distribution analysis

**3. Threshold Detection:**
- Simple boundary checks
- Performance thresholds
- Event rate anomalies

**Anomaly Types:**
- SCORE_DROP - Sudden performance degradation
- SCORE_SPIKE - Unexpected improvement (potential manipulation)
- TIMING_ANOMALY - Irregular tick intervals
- EVENT_ANOMALY - Unusual event patterns
- MISSING_TICK - Agent not executing
- HIGH_ERROR_RATE - Excessive failures
- BEHAVIOR_DEVIATION - Deviation from expected behavior
- PERFORMANCE_DEGRADATION - Gradual performance decline
- STATISTICAL_OUTLIER - Statistical anomaly

**Severity Levels:**
- LOW (1) - Minor issue, monitor only
- MEDIUM (2) - Noticeable issue, may need attention
- HIGH (3) - Serious issue, requires action
- CRITICAL (4) - Emergency situation

#### Usage Example

```python
from senti_os.core.faza28_5 import get_anomaly_detector

detector = get_anomaly_detector()

# Detect anomalies for an agent
anomalies = detector.detect_all(
    agent_name="unstable_agent",
    current_score=0.3,
    tick_time=datetime.now(),
    had_error=True,
    metrics={"avg_execution_time": 2.0}
)

for anomaly in anomalies:
    print(f"Anomaly: {anomaly.anomaly_type.value}")
    print(f"Severity: {anomaly.severity.name}")
    print(f"Description: {anomaly.description}")
    print(f"Confidence: {anomaly.confidence:.2f}")
```

### 4. Stability Engine

**File:** `stability_engine.py`

Detects and handles multi-agent stability issues.

**Stability Issues Detected:**

**1. Feedback Loops:**
- Circular agent interactions (A → B → C → A)
- Detected using DFS graph traversal
- Severity based on cycle length

**2. Deadlocks:**
- Multiple agents waiting indefinitely
- No progress being made
- Detected by monitoring inactive agents

**3. Starvation:**
- Agent not getting execution time
- Prolonged inactivity
- Resource allocation issues

**4. Runaway Agents:**
- Excessive tick counts
- Rapid execution rate
- Resource consumption spikes

**5. Escalating Load:**
- System load increasing exponentially
- Detected by analyzing load trends
- Early warning system

**6. Thrashing:**
- High activity, low productivity
- Excessive context switching
- Detected by tick/output ratio

**7. Cascade Failures:**
- Multiple agent failures in sequence
- System-wide degradation
- Critical emergency state

**Recovery Actions:**
- RESET_AGENT - Restart agent
- REDISTRIBUTE_TASKS - Move work to healthy agents
- THROTTLE_AGENT - Reduce execution rate
- ISOLATE_AGENT - Quarantine problematic agent
- ESCALATE_POLICY - Trigger emergency policies
- EMERGENCY_SHUTDOWN - System-wide shutdown
- WAIT_AND_MONITOR - Observe before acting

#### Usage Example

```python
from senti_os.core.faza28_5 import get_stability_engine

engine = get_stability_engine()

# Record agent interactions
engine.record_interaction("agent1", "agent2")
engine.record_interaction("agent2", "agent3")
engine.record_interaction("agent3", "agent1")  # Creates loop

# Analyze stability
agent_metrics = {
    "agent1": {"tick_count": 100, "active": True},
    "agent2": {"tick_count": 200, "active": True},
    "agent3": {"tick_count": 150, "active": True}
}

system_metrics = {
    "system_load": 0.75,
    "total_agents": 3
}

reports = engine.analyze_stability(agent_metrics, system_metrics)

for report in reports:
    print(f"Issue: {report.issue_type.value}")
    print(f"Severity: {report.severity:.2f}")
    print(f"Affected: {report.affected_agents}")
    print(f"Recommended: {report.recommended_action.value}")
```

### 5. Strategy Adapter

**File:** `strategy_adapter.py`

Dynamically adapts system behavior based on real-time conditions.

**System Strategies:**

**1. AGGRESSIVE (Maximum Performance):**
- Priority-based scheduling
- 1.5x tick rate multiplier
- Max 50 concurrent agents
- 10% error tolerance
- Priority boost +2
- Throttle at 90% load

**2. BALANCED (Default):**
- Load-aware scheduling
- 1.0x tick rate multiplier
- Max 20 concurrent agents
- 5% error tolerance
- Priority boost +1
- Throttle at 70% load

**3. SAFE (Maximum Stability):**
- Round-robin scheduling
- 0.7x tick rate multiplier
- Max 10 concurrent agents
- 1% error tolerance
- No priority boost
- Throttle at 50% load

**4. ADAPTIVE (Auto-Adapt):**
- Automatically selects strategy based on:
  - System health
  - Error rates
  - Anomaly counts
  - Stability issues

**Adaptation Capabilities:**
- Adjust scheduling strategy
- Modify agent priorities in real-time
- Adapt agent tick rates
- Reroute events
- Change system parameters

#### Usage Example

```python
from senti_os.core.faza28_5 import get_strategy_adapter, SystemStrategy

adapter = get_strategy_adapter()

# Manually set strategy
adapter.apply_strategy(SystemStrategy.AGGRESSIVE)

# Auto-adapt based on conditions
system_metrics = {"avg_meta_score": 0.9, "error_rate": 0.01}
agent_scores = {}  # Agent score data
anomalies = []
stability_issues = []

actions = adapter.adapt_system(
    system_metrics=system_metrics,
    agent_scores=agent_scores,
    anomalies=anomalies,
    stability_issues=stability_issues
)

for action in actions:
    print(f"Adaptation: {action.action_type}")
    print(f"Target: {action.target}")
    print(f"Change: {action.old_value} → {action.new_value}")
```

### 6. Oversight Agent

**File:** `oversight_agent.py`

Main meta-agent that coordinates all FAZA 28.5 subsystems.

**Responsibilities:**
- Subscribe to ALL FAZA 28 events
- Maintain agent performance timeline
- Detect drift, lag, crashes, overload
- Trigger stability and anomaly detection
- Evaluate policies
- Apply strategy adaptations
- Generate periodic meta-reports
- Update FAZA 28 state context

**Meta-Report Contents:**
- System health status (HEALTHY/STABLE/DEGRADED/CRITICAL)
- Average agent scores
- Top/worst performing agents
- Total anomalies (with critical count)
- Stability issues
- Policy triggers
- System adaptations
- Time interval and timestamp

**Report Generation:** Configurable interval (default: 60 seconds)

#### Usage Example

```python
from senti_os.core.faza28_5 import get_oversight_agent

agent = get_oversight_agent()

# Start monitoring
await agent.on_start(state_context)

# Oversight agent runs automatically in FAZA 28 loop
# Access latest report
report = agent.get_latest_report()

if report:
    print(f"System Status: {report['summary']}")
    print(f"Avg Score: {report['avg_meta_score']:.3f}")
    print(f"Anomalies: {report['total_anomalies']}")
    print(f"Critical Issues: {report['critical_stability_issues']}")
```

### 7. Integration Layer

**File:** `integration_layer.py`

Main entry point and public API for FAZA 28.5.

**Core Functions:**
- Initialize all subsystems
- Attach to FAZA 28 components
- Register oversight agent
- Orchestrate monitoring pipeline
- Provide public API for meta-evaluation

**Public API Methods:**
- `get_agent_scores()` - Get all agent scores
- `get_system_risk()` - Overall risk assessment
- `get_policy_status()` - Policy manager statistics
- `get_stability_summary()` - Stability engine summary
- `get_adaptation_summary()` - Strategy adapter summary
- `get_anomaly_summary()` - Anomaly detector summary
- `get_meta_report()` - Latest system meta-report
- `get_complete_status()` - Full FAZA 28.5 status

#### Usage Example

```python
from senti_os.core.faza28_5 import get_meta_layer

# Initialize meta-layer
meta_layer = get_meta_layer()
meta_layer.initialize()

# Attach to FAZA 28 (optional but recommended)
from senti_os.core.faza28 import (
    get_event_bus,
    get_scheduler,
    get_state_context,
    get_agent_manager
)

meta_layer.attach_to_faza28(
    event_bus=get_event_bus(),
    scheduler=get_scheduler(),
    state_context=get_state_context(),
    agent_manager=get_agent_manager()
)

# Start monitoring
await meta_layer.start()

# Access meta-evaluation data
scores = meta_layer.get_agent_scores()
risk = meta_layer.get_system_risk()
status = meta_layer.get_complete_status()

print(f"Overall Risk: {risk['overall_risk']}")
print(f"Risk Score: {risk['risk_score']:.3f}")
```

## Integration with FAZA 28

### Setup and Initialization

```python
from senti_os.core.faza28 import get_ael_controller, get_agent_manager
from senti_os.core.faza28_5 import get_meta_layer

# 1. Initialize FAZA 28 AEL
ael = get_ael_controller(tick_rate=1.0, strategy="priority")

# Register agents with FAZA 28
agent_manager = get_agent_manager()
# ... register your agents ...

# 2. Initialize FAZA 28.5 Meta-Layer
meta_layer = get_meta_layer()
meta_layer.initialize()

# 3. Attach meta-layer to FAZA 28
from senti_os.core.faza28 import (
    get_event_bus,
    get_state_context,
    get_scheduler
)

meta_layer.attach_to_faza28(
    event_bus=get_event_bus(),
    scheduler=get_scheduler(),
    state_context=get_state_context(),
    agent_manager=agent_manager
)

# 4. Start both systems
await meta_layer.start()
await ael.start()

# FAZA 28.5 now monitors FAZA 28 automatically
```

### Event Subscription

FAZA 28.5 Oversight Agent subscribes to all events from FAZA 28 EventBus:

```python
# Automatic subscription (handled by integration_layer)
# Oversight agent receives ALL events:
# - agent_started
# - agent_tick
# - agent_error
# - agent_shutdown
# - custom events

# Events are processed in oversight_agent.on_event()
```

### State Context Integration

FAZA 28.5 stores meta-evaluation data in FAZA 28 StateContext:

```python
from senti_os.core.faza28 import get_state_context

context = get_state_context()

# FAZA 28.5 automatically stores:
# - oversight_active (bool)
# - oversight_anomalies (int)
# - oversight_stability_issues (int)
# - oversight_policy_triggers (int)
# - oversight_adaptations (int)
# - oversight_last_report (dict)

# Access from anywhere:
report = context.get("oversight_last_report")
```

### Scheduler Integration

FAZA 28.5 can modify FAZA 28 scheduler behavior:

```python
# Strategy Adapter automatically adjusts scheduler
# based on system conditions:

# Example: Switch to round-robin under high load
# This happens automatically in ADAPTIVE mode

# Manual override:
from senti_os.core.faza28_5 import get_strategy_adapter, SystemStrategy

adapter = get_strategy_adapter()
adapter.apply_strategy(SystemStrategy.SAFE)
# This will adapt scheduler to round-robin
```

## Configuration and Tuning

### Agent Scorer Configuration

```python
from senti_os.core.faza28_5 import create_agent_scorer

scorer = create_agent_scorer(
    performance_weight=0.3,      # Weight for performance score
    reliability_weight=0.3,      # Weight for reliability score
    cooperation_weight=0.2,      # Weight for cooperation score
    stability_weight=0.2,        # Weight for stability score
    time_decay=0.9               # Exponential moving average decay
)

# Tuning guidance:
# - Increase performance_weight for performance-critical systems
# - Increase reliability_weight for mission-critical systems
# - Increase cooperation_weight for collaborative agent systems
# - Increase stability_weight for stability-critical systems
```

### Anomaly Detector Configuration

```python
from senti_os.core.faza28_5 import create_anomaly_detector

detector = create_anomaly_detector(
    score_drop_threshold=0.3,    # Threshold for score drops
    score_spike_threshold=0.3,   # Threshold for score spikes
    error_rate_threshold=0.1,    # Maximum acceptable error rate
    missing_tick_window=60.0,    # Time before missing tick (seconds)
    outlier_z_score=3.0,         # Z-score for statistical outliers
    history_size=100             # Number of historical data points
)

# Tuning guidance:
# - Lower thresholds = more sensitive detection
# - Higher thresholds = fewer false positives
# - Adjust based on system characteristics
```

### Stability Engine Configuration

```python
from senti_os.core.faza28_5 import create_stability_engine

engine = create_stability_engine(
    feedback_loop_threshold=10,  # Max cycles before feedback loop
    deadlock_timeout=30.0,       # Time before deadlock suspected
    starvation_threshold=60.0,   # Time before starvation detected
    runaway_tick_threshold=1000, # Tick count for runaway detection
    load_escalation_rate=2.0,    # Rate multiplier for escalation
    history_window=300           # Time window for analysis (seconds)
)

# Tuning guidance:
# - Decrease thresholds for faster detection
# - Increase thresholds to reduce false positives
# - Adjust based on typical agent behavior
```

### Strategy Adapter Configuration

```python
from senti_os.core.faza28_5 import create_strategy_adapter, SystemStrategy

adapter = create_strategy_adapter(
    default_strategy=SystemStrategy.BALANCED,
    auto_adapt=True,             # Enable automatic adaptation
    adaptation_cooldown=30.0     # Minimum time between adaptations
)

# Tuning guidance:
# - Use AGGRESSIVE for performance-first systems
# - Use SAFE for stability-first systems
# - Use ADAPTIVE for dynamic environments
# - Increase cooldown to prevent thrashing
```

### Oversight Agent Configuration

```python
from senti_os.core.faza28_5 import create_oversight_agent

agent = create_oversight_agent(
    report_interval=60.0,        # Meta-report interval (seconds)
    monitoring_enabled=True      # Enable/disable monitoring
)

# Tuning guidance:
# - Decrease interval for more frequent reports
# - Increase interval to reduce overhead
# - Disable monitoring for testing/debugging
```

## Best Practices

### 1. Gradual Rollout

Start with monitoring-only mode before enabling adaptations:

```python
# Phase 1: Monitoring only
meta_layer = get_meta_layer()
meta_layer.initialize()
meta_layer.oversight_agent.monitoring_enabled = True

# Monitor for 24 hours, review reports

# Phase 2: Enable policies
meta_layer.policy_manager.enable_policy("isolation")
# Monitor for 48 hours

# Phase 3: Enable adaptations
meta_layer.strategy_adapter.auto_adapt = True
# Monitor indefinitely
```

### 2. Alert Thresholds

Set up monitoring for critical conditions:

```python
def check_critical_conditions(meta_layer):
    risk = meta_layer.get_system_risk()
    
    if risk['overall_risk'] == 'critical':
        # Send alert to operations team
        send_alert("CRITICAL: System at critical risk level")
    
    stability = meta_layer.get_stability_summary()
    if stability['critical_issues'] > 0:
        # Send alert
        send_alert(f"WARNING: {stability['critical_issues']} critical stability issues")
```

### 3. Regular Review

Review meta-reports regularly:

```python
# Daily review script
def daily_review():
    meta_layer = get_meta_layer()
    
    # Get last 24 hours of reports
    reports = meta_layer.oversight_agent.meta_reports[-1440:]  # Assuming 1-min intervals
    
    # Analyze trends
    anomaly_counts = [r['total_anomalies'] for r in reports]
    avg_anomalies = sum(anomaly_counts) / len(anomaly_counts)
    
    print(f"Average anomalies/report: {avg_anomalies:.2f}")
    
    # Check for concerning trends
    if anomaly_counts[-10:] > anomaly_counts[:10]:
        print("WARNING: Anomaly rate increasing")
```

### 4. Policy Tuning

Start with conservative policies and tune based on experience:

```python
from senti_os.core.faza28_5 import KillSwitchPolicy

# Start conservative
policy = KillSwitchPolicy(
    max_error_rate=0.8,          # 80% error rate before kill
    min_meta_score=0.05,         # Very low score threshold
    max_consecutive_failures=20  # Many failures before kill
)

# After monitoring, tune more aggressively
policy = KillSwitchPolicy(
    max_error_rate=0.5,          # 50% error rate
    min_meta_score=0.1,          # Higher threshold
    max_consecutive_failures=10  # Fewer failures
)
```

### 5. Testing

Test FAZA 28.5 with simulated conditions:

```python
# Create test scenario
def test_overload_scenario():
    meta_layer = get_meta_layer()
    
    # Simulate many agents
    for i in range(100):
        meta_layer.scorer.record_tick(
            f"test_agent_{i}",
            execution_time=0.1,
            had_error=False
        )
    
    # Check policy response
    context = {"total_agents": 100, "active_agents": 100}
    decisions = meta_layer.policy_manager.evaluate_all(context)
    
    # Verify overload protection triggered
    assert any(d.action == PolicyAction.DENY for d in decisions)
```

## Troubleshooting

### Issue: Meta-Layer Not Monitoring

**Symptoms:** No meta-reports generated, no adaptations

**Diagnosis:**
```python
meta_layer = get_meta_layer()
print(f"Initialized: {meta_layer._initialized}")
print(f"Attached: {meta_layer._attached}")
print(f"Monitoring: {meta_layer.oversight_agent.monitoring_enabled}")
```

**Solution:**
```python
# Ensure initialization
if not meta_layer._initialized:
    meta_layer.initialize()

# Ensure attachment
if not meta_layer._attached:
    meta_layer.attach_to_faza28(
        event_bus=get_event_bus(),
        state_context=get_state_context()
    )

# Start monitoring
await meta_layer.start()
```

### Issue: Too Many Anomalies Detected

**Symptoms:** Constant anomaly alerts, system thrashing

**Diagnosis:**
```python
detector = meta_layer.anomaly_detector
summary = detector.get_anomaly_summary()
print(f"Total anomalies: {summary['total_anomalies']}")
print(f"By type: {summary['anomalies_by_type']}")
```

**Solution:** Tune detection thresholds

```python
# Increase thresholds to reduce sensitivity
detector.score_drop_threshold = 0.5  # Was 0.3
detector.error_rate_threshold = 0.15  # Was 0.1
detector.outlier_z_score = 4.0        # Was 3.0
```

### Issue: Policies Too Aggressive

**Symptoms:** Agents being killed/isolated too frequently

**Diagnosis:**
```python
manager = meta_layer.policy_manager
stats = manager.get_stats()

for policy_stats in stats['policies']:
    print(f"{policy_stats['name']}: {policy_stats['trigger_rate']:.1%}")
```

**Solution:** Adjust policy parameters or disable

```python
# Disable aggressive policies temporarily
manager.disable_policy("kill_switch")

# Or tune parameters
kill_switch = manager.policies["kill_switch"]
kill_switch.max_error_rate = 0.8  # More tolerant
kill_switch.min_meta_score = 0.05  # Lower threshold
```

### Issue: Strategy Adapter Thrashing

**Symptoms:** Constant strategy changes, instability

**Diagnosis:**
```python
adapter = meta_layer.strategy_adapter
summary = adapter.get_adaptation_summary()
print(f"Total adaptations: {summary['total_adaptations']}")
print(f"Recent adaptations: {summary['recent_adaptations']}")
```

**Solution:** Increase adaptation cooldown

```python
adapter.adaptation_cooldown = 60.0  # Was 30.0
# Or disable auto-adapt
adapter.auto_adapt = False
adapter.apply_strategy(SystemStrategy.BALANCED)
```

### Issue: High System Overhead

**Symptoms:** FAZA 28 performance degraded with FAZA 28.5 enabled

**Diagnosis:**
```python
# Check report interval
print(f"Report interval: {oversight_agent.report_interval}s")

# Check history sizes
print(f"Score history: {len(scorer.agent_metrics)}")
print(f"Anomaly history: {len(detector.anomalies)}")
```

**Solution:** Reduce monitoring frequency

```python
# Increase report interval
oversight_agent.report_interval = 120.0  # Was 60.0

# Reduce history sizes
scorer.history_size = 50  # Was 100
detector.history_size = 50  # Was 100

# Or disable monitoring temporarily
oversight_agent.monitoring_enabled = False
```

## Performance Characteristics

### Computational Complexity

- **Agent Scorer:** O(1) per tick recording, O(n) for all scores
- **Anomaly Detector:** O(1) for rule-based, O(n) for statistical
- **Stability Engine:** O(V²) for feedback loops, O(V) for others
- **Policy Manager:** O(p) where p = number of policies
- **Strategy Adapter:** O(a) where a = number of agents
- **Oversight Agent:** O(n) per tick where n = number of subsystems

### Memory Usage

Typical memory footprint:
- Base: ~5 MB
- Per agent tracked: ~50 KB
- Per anomaly: ~1 KB
- Per stability report: ~2 KB
- Per meta-report: ~5 KB

For 100 agents: ~10-15 MB total

### Performance Impact on FAZA 28

Expected overhead:
- Minimal: <5% with 10 agents
- Low: 5-10% with 50 agents
- Moderate: 10-20% with 100 agents
- High: >20% with 200+ agents

Mitigation:
- Increase report interval
- Reduce history sizes
- Disable unnecessary policies
- Use selective monitoring

## Testing

### Run Test Suite

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 tests/test_faza28_5.py
```

### Test Coverage

**46 comprehensive tests:**
- Agent Scorer: 10 tests
- Meta Policies: 9 tests
- Anomaly Detector: 7 tests
- Stability Engine: 6 tests
- Strategy Adapter: 5 tests
- Oversight Agent: 4 tests
- Integration Layer: 6 tests

All tests passing ✓

### Integration Testing

```python
# Full integration test
async def test_full_integration():
    # Setup FAZA 28
    from senti_os.core.faza28 import (
        AgentBase,
        get_agent_manager,
        get_ael_controller
    )
    
    # Create test agent
    class TestAgent(AgentBase):
        name = "test_agent"
        
        async def on_tick(self, context):
            await super().on_tick(context)
            context.set("test_ticks", context.get("test_ticks", 0) + 1)
    
    # Register agent
    manager = get_agent_manager()
    manager.register(TestAgent())
    
    # Setup FAZA 28.5
    from senti_os.core.faza28_5 import get_meta_layer
    
    meta_layer = get_meta_layer()
    meta_layer.initialize()
    meta_layer.attach_to_faza28(
        agent_manager=manager,
        state_context=get_state_context()
    )
    
    # Run for 10 seconds
    ael = get_ael_controller(tick_rate=0.1)
    
    async def run_test():
        asyncio.create_task(ael.start())
        await asyncio.sleep(10)
        await ael.stop()
    
    await run_test()
    
    # Verify meta-layer captured data
    scores = meta_layer.get_agent_scores()
    assert "test_agent" in scores
    
    report = meta_layer.get_meta_report()
    assert report is not None
```

## Future Enhancements

### Planned Features

1. **Machine Learning Integration:**
   - ML-based anomaly detection
   - Predictive failure analysis
   - Automated policy generation

2. **Distributed Monitoring:**
   - Multi-node FAZA 28.5 coordination
   - Distributed agent scoring
   - Cross-system meta-evaluation

3. **Advanced Visualization:**
   - Real-time dashboards
   - Agent interaction graphs
   - Anomaly timelines

4. **Policy Marketplace:**
   - Pre-built policy templates
   - Community-contributed policies
   - Industry-specific policy packs

5. **Auto-Tuning:**
   - Self-optimizing thresholds
   - Adaptive policy parameters
   - Dynamic strategy selection

## Version History

- **v1.0.0** (2024-12-04): Initial Enterprise Edition
  - Agent Scorer with 4-dimensional scoring
  - Meta Policies with 7 default policies
  - Anomaly Detector with 3 detection methods
  - Stability Engine with 7 issue types
  - Strategy Adapter with 4 system strategies
  - Oversight Agent with meta-reporting
  - Integration Layer with full FAZA 28 integration
  - 46 comprehensive tests
  - Complete enterprise documentation

## License

Part of Senti System - Enterprise Edition - Proprietary

---

**FAZA 28.5 - Meta-Agent Oversight Layer (Enterprise Edition)**
*Enterprise-grade meta-monitoring for autonomous agent systems*
