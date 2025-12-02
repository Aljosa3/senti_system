# FAZA 20 — Implementation Guide
## Practical User Experience Layer Setup

**Version:** 1.0.0
**Audience:** Developers, System Administrators, Integration Engineers
**Tone:** Calm, Confidence-Building, Practical
**Last Updated:** 2025-12-02

---

## Table of Contents

1. [First-Run Playbook](#first-run-playbook)
2. [Onboarding Wizard Flow](#onboarding-wizard-flow)
3. [Terminal Comfort Dashboard](#terminal-comfort-dashboard)
4. [Common Integration Patterns](#common-integration-patterns)
5. [Error Handling & Recovery](#error-handling--recovery)
6. [Monitoring & Observability](#monitoring--observability)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

---

## First-Run Playbook

### What to Expect on First Launch

When you start SENTI OS for the first time with FAZA 20 enabled, here's what happens:

```
┌─────────────────────────────────────────────────────┐
│  First Launch Timeline                              │
├─────────────────────────────────────────────────────┤
│  0-1s:   FAZA 20 stack initializes                  │
│  1-2s:   Components wire together                   │
│  2-3s:   Heartbeat monitoring starts                │
│  3-4s:   Status collection begins                   │
│  4-5s:   Onboarding wizard activates                │
│  5s+:    System ready for interaction               │
└─────────────────────────────────────────────────────┘
```

### Step-by-Step First Launch

#### Step 1: Import and Initialize

```python
from senti_os.core.faza20 import FAZA20Stack

# Optional: Import other FAZA layers if available
# from senti_os.core.faza21 import FAZA21Stack

# Create FAZA 20 stack
ux_layer = FAZA20Stack(
    # Optional: Pass other FAZA layer references
    # faza21_persistence=persistence_layer,
    status_collection_frequency=5,  # seconds
    heartbeat_interval=10           # seconds
)

# Initialize the stack
success = ux_layer.initialize()

if success:
    print("✓ FAZA 20 initialized successfully")
else:
    print("✗ FAZA 20 initialization failed")
    # Check logs for details
```

**What's Normal:**
- Initialization takes 1-3 seconds
- No error messages
- Console output shows component initialization

**What Indicates an Error:**
- `success = False` returned
- Error messages in console
- Exceptions raised
- Initialization time >10 seconds

#### Step 2: Start Services

```python
# Start background services (heartbeat monitor)
success = ux_layer.start()

if success:
    print("✓ FAZA 20 services started")
    print("  • Heartbeat monitoring: ACTIVE")
    print("  • Status collection: READY")
else:
    print("✗ FAZA 20 services failed to start")
```

**What's Normal:**
- Start completes in <1 second
- Heartbeat thread starts in background
- No errors or warnings

**What Indicates an Error:**
- `success = False` returned
- Thread start failures
- Port conflicts (if applicable)

#### Step 3: Check Initial Status

```python
# Get system status
status = ux_layer.get_status()

print(f"Initialized: {status['initialized']}")
print(f"Started: {status['started']}")
print(f"Components: {status['components']}")
print(f"Modules Registered: {status['modules_registered']}")
```

**Expected Output:**
```
Initialized: True
Started: True
Components: {'status_collector': {...}, 'heartbeat_monitor': {...}, ...}
Modules Registered: {'faza16': False, 'faza17': False, ...}
```

#### Step 4: Run Initial Diagnostics

```python
# Run quick diagnostics
report = ux_layer.run_diagnostics(quick=True)

print(f"Overall Status: {report.overall_status.value}")
print(f"Tests Run: {report.tests_run}")
print(f"Tests Passed: {report.tests_passed}")
print(f"Tests Failed: {report.tests_failed}")
print(f"Duration: {report.duration_seconds:.2f}s")

# Check for issues
if report.overall_status.value in ['error', 'critical']:
    print("\n⚠ Issues detected:")
    for result in report.results:
        if not result.passed:
            print(f"  - {result.test_name}: {result.message}")
```

**Expected Output (Minimal Setup):**
```
Overall Status: warning
Tests Run: 8
Tests Passed: 4
Tests Failed: 4
Duration: 0.45s

⚠ Issues detected:
  - module_registered_faza16_llm_control: Module not registered
  - module_registered_faza17_orchestration: Module not registered
  ...
```

**This is NORMAL** if you haven't registered other FAZA modules yet.

#### Step 5: Access UI API

```python
# Create UI API instance
from senti_os.core.faza20.ui_api import UIAPI

api = UIAPI(ux_layer)

# Get system status via API
response = api.get_status()

if response["success"]:
    print(f"System Health: {response['status']['overall_health']}")
    print(f"System Score: {response['status']['overall_score']}")
else:
    print(f"Error: {response['error']}")
```

**Expected Output:**
```
System Health: healthy
System Score: 0.85
```

---

## Onboarding Wizard Flow

### Complete Onboarding State Machine

```
                    ┌─────────────┐
          START ────►│   WELCOME   │
                    └──────┬──────┘
                           │
                   User clicks "Get Started"
                           │
                    ┌──────▼───────────────┐
                    │  GENERATE_MASTER_KEY │
                    │                      │
                    │  Options:            │
                    │  • No passphrase     │
                    │  • With passphrase   │
                    └──────┬───────────────┘
                           │
                    Success / Failure
                           │
                ┌──────────┴──────────┐
                │                     │
            SUCCESS                FAILURE
                │                     │
         ┌──────▼──────────┐         │
         │ LINK_FIRST_     │         │
         │ DEVICE          │         └──► Show Error
         │                 │              Allow Retry
         │ Input:          │
         │ • Device name   │
         └──────┬──────────┘
                │
         Success / Failure
                │
         ┌──────┴──────┐
         │             │
     SUCCESS        FAILURE
         │             │
  ┌──────▼─────────────┴──┐         │
  │ TEST_LLM_            ◄─┘         │
  │ CONNECTIVITY         │           └──► Show Error
  │ (Optional)           │                Allow Retry
  │                      │
  │ Can be skipped ──────┼──► SKIP
  └──────┬───────────────┘
         │
  Success / Skip
         │
  ┌──────▼──────────┐
  │ RUN_DIAGNOSTICS │
  │                 │
  │ Automatic       │
  └──────┬──────────┘
         │
    All tests OK
         │
  ┌──────▼──────┐
  │  COMPLETE   │
  │             │
  │ ✓ Ready!    │
  └─────────────┘
```

### Implementing Onboarding

#### Basic Onboarding Flow

```python
from senti_os.core.faza20.onboarding_assistant import OnboardingStep

# Get onboarding assistant from stack
assistant = ux_layer.onboarding_assistant

# Start onboarding
state = assistant.start_onboarding()

print(f"Current Step: {state.current_step.value}")
print(f"Progress: {len(state.steps_completed)}/{state.metadata['total_steps']}")

# Get step info
step_info = assistant.get_current_step_info()
print(f"\nStep: {step_info['title']}")
print(f"Description: {step_info['description']}")
print(f"Action: {step_info['action']}")
print(f"Estimated Time: {step_info['estimated_time']}")
```

#### Step 1: Welcome

```python
# Complete welcome step
result = assistant.complete_step(OnboardingStep.WELCOME)

if result.completed:
    print(f"✓ {result.message}")
else:
    print(f"✗ {result.message}")
```

**Expected Output:**
```
✓ Welcome! Let's get started with your setup.
```

#### Step 2: Generate Master Key

```python
# Option A: No passphrase (random key)
result = assistant.complete_step(
    OnboardingStep.GENERATE_MASTER_KEY
)

# Option B: With passphrase (user-provided)
result = assistant.complete_step(
    OnboardingStep.GENERATE_MASTER_KEY,
    passphrase="my-secure-passphrase-2025"
)

if result.completed:
    print(f"✓ {result.message}")
    has_passphrase = result.details.get('has_passphrase', False)
    print(f"  Passphrase: {'Yes' if has_passphrase else 'No (random key)'}")
else:
    print(f"✗ {result.message}")
```

**Expected Output (Success):**
```
✓ Master key generated successfully
  Passphrase: Yes
```

**Expected Output (Failure):**
```
✗ Error generating master key: FAZA 21 persistence layer not available
```

**Recovery:**
- Ensure FAZA 21 is initialized and passed to FAZA20Stack
- Retry the step after fixing dependencies

#### Step 3: Link First Device

```python
# Link device with name
result = assistant.complete_step(
    OnboardingStep.LINK_FIRST_DEVICE,
    device_name="Primary Desktop"
)

if result.completed:
    print(f"✓ {result.message}")
    device_id = result.details.get('device_id')
    device_name = result.details.get('device_name')
    print(f"  Device ID: {device_id}")
    print(f"  Device Name: {device_name}")
else:
    print(f"✗ {result.message}")
```

**Expected Output (Success):**
```
✓ Device 'Primary Desktop' linked successfully
  Device ID: dev_20251202_100523_abc123
  Device Name: Primary Desktop
```

#### Step 4: Test LLM Connectivity (Optional)

```python
# Option A: Complete the step
result = assistant.complete_step(
    OnboardingStep.TEST_LLM_CONNECTIVITY
)

# Option B: Skip the step
success = assistant.skip_step(
    OnboardingStep.TEST_LLM_CONNECTIVITY
)

if success:
    print("✓ Step skipped")
```

#### Step 5: Run Diagnostics

```python
# This step runs automatically
result = assistant.complete_step(
    OnboardingStep.RUN_DIAGNOSTICS
)

if result.completed:
    print(f"✓ {result.message}")
    status = result.details.get('status')
    tests_passed = result.details.get('tests_passed')
    tests_failed = result.details.get('tests_failed')

    print(f"  Status: {status}")
    print(f"  Tests Passed: {tests_passed}")
    print(f"  Tests Failed: {tests_failed}")
else:
    print(f"✗ {result.message}")
```

**Expected Output (Success):**
```
✓ Diagnostics complete: ok
  Status: ok
  Tests Passed: 12
  Tests Failed: 0
```

#### Check Completion

```python
# Check if onboarding is complete
if assistant.is_onboarding_complete():
    print("\n🎉 Onboarding Complete!")
    print("SENTI OS is ready to use.")
else:
    state = assistant.get_state()
    remaining = state.metadata['total_steps'] - len(state.steps_completed)
    print(f"\n{remaining} steps remaining")
```

---

## Terminal Comfort Dashboard

### Real-Time Status Display

Here's a sample terminal UI you can implement:

```
╔══════════════════════════════════════════════════════════════════╗
║                    SENTI OS — System Status                      ║
║                      FAZA 20 UX Layer                            ║
╚══════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────┐
│  OVERALL HEALTH: ● HEALTHY                    Score: 0.92 / 1.00 │
│  Uptime: 00:15:42                            Last Check: 2s ago  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  MODULE STATUS                                                   │
├──────────────────────────────────────────────────────────────────┤
│  FAZA 16 — LLM Control         ● HEALTHY     Score: 0.95        │
│  FAZA 17 — Orchestration       ● HEALTHY     Score: 0.90        │
│  FAZA 18 — Auth Flow           ● DEGRADED    Score: 0.75  ⚠     │
│  FAZA 19 — UIL & Multi-Device  ● HEALTHY     Score: 0.98        │
│  FAZA 21 — Persistence         ● HEALTHY     Score: 1.00        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  HEARTBEAT MONITOR                                               │
├──────────────────────────────────────────────────────────────────┤
│  Total Beats: 245                Success Rate: 99.2%            │
│  Missed: 2                       Last Beat: 1s ago              │
│                                                                  │
│  Module Response Times (ms):                                    │
│    FAZA 16: 15ms   FAZA 17: 22ms   FAZA 19: 8ms   FAZA 21: 12ms│
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  ACTIVE ALERTS (2)                                               │
├──────────────────────────────────────────────────────────────────┤
│  ⚠  WARNING  │ FAZA 18: Authentication flow delayed             │
│              │ 3 minutes ago                                     │
│              │ [Dismiss]                                         │
│  ──────────────────────────────────────────────────────────────  │
│  ℹ  INFO     │ System diagnostics completed successfully        │
│              │ 15 minutes ago                                    │
│              │ [Dismiss]                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  RECENT ACTIVITY                                                 │
├──────────────────────────────────────────────────────────────────┤
│  [llm_control] Selected Claude-3 for complex reasoning           │
│  [orchestration] Step 1: Analyzing input with Model A            │
│  [event_bus] Device linked: Primary Desktop                      │
│  [system] FAZA 20 services started: heartbeat monitoring active  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  DIAGNOSTICS                                                     │
├──────────────────────────────────────────────────────────────────┤
│  Last Run: 15 minutes ago                                        │
│  Status: ● OK                                                    │
│  Tests: 24 passed, 0 failed                                      │
│  Duration: 1.2s                                                  │
│                                                                  │
│  [Run Diagnostics]  [View Full Report]                          │
└──────────────────────────────────────────────────────────────────┘

 [Q] Quit  [D] Diagnostics  [A] Alerts  [H] Help  [R] Refresh
```

### Implementation Code

```python
import time
from datetime import datetime

def display_dashboard(ux_layer):
    """Display terminal dashboard."""

    # Clear screen
    print("\033[2J\033[H")

    # Header
    print("╔" + "═"*66 + "╗")
    print("║" + "SENTI OS — System Status".center(66) + "║")
    print("║" + "FAZA 20 UX Layer".center(66) + "║")
    print("╚" + "═"*66 + "╝")
    print()

    # Get current status
    status_response = ux_layer.ui_api.get_status()
    if not status_response["success"]:
        print("Error fetching status")
        return

    status = status_response["status"]

    # Overall Health
    health = status["overall_health"]
    score = status["overall_score"]
    health_icon = "●" if health == "healthy" else "⚠" if health == "degraded" else "✗"
    health_color = "\033[92m" if health == "healthy" else "\033[93m" if health == "degraded" else "\033[91m"

    print("┌" + "─"*66 + "┐")
    print(f"│  OVERALL HEALTH: {health_color}{health_icon}\033[0m {health.upper():<20} Score: {score:.2f} / 1.00 │")
    print(f"│  Uptime: {format_uptime(status['uptime_seconds']):<20} Last Check: 2s ago  │")
    print("└" + "─"*66 + "┘")
    print()

    # Module Status
    print("┌" + "─"*66 + "┐")
    print("│  MODULE STATUS" + " "*52 + "│")
    print("├" + "─"*66 + "┤")

    for module in status["modules"]:
        name = f"FAZA {module['faza']} — {module['name']}"
        health = module["health"]
        score = module["score"]
        icon = "●" if health == "healthy" else "⚠" if health == "degraded" else "✗"
        warning = "⚠" if health == "degraded" else " "

        print(f"│  {name:<28} {icon} {health.upper():<8} Score: {score:.2f}  {warning}     │")

    print("└" + "─"*66 + "┘")
    print()

    # Heartbeat Monitor
    hb_response = ux_layer.ui_api.get_heartbeat()
    if hb_response["success"]:
        hb_stats = hb_response["overall"]

        print("┌" + "─"*66 + "┐")
        print("│  HEARTBEAT MONITOR" + " "*48 + "│")
        print("├" + "─"*66 + "┤")
        print(f"│  Total Beats: {hb_stats['total_beats']:<15} Success Rate: {hb_stats['success_rate']*100:.1f}%            │")
        print(f"│  Missed: {hb_stats['total_missed']:<20} Last Beat: 1s ago              │")
        print("└" + "─"*66 + "┘")
        print()

    # Alerts
    alerts_response = ux_layer.ui_api.get_alerts(dismissed=False, limit=5)
    if alerts_response["success"]:
        alerts = alerts_response["alerts"]

        print("┌" + "─"*66 + "┐")
        print(f"│  ACTIVE ALERTS ({len(alerts)})" + " "*50 + "│")
        print("├" + "─"*66 + "┤")

        if alerts:
            for alert in alerts[:2]:
                level_icon = "⚠" if alert["level"] == "warning" else "ℹ" if alert["level"] == "info" else "✗"
                print(f"│  {level_icon}  {alert['level'].upper():<8} │ {alert['title']:<43} │")
                print(f"│              │ {time_ago(alert['timestamp'])}                                    │")
                print(f"│              │ [Dismiss]                                         │")
                if len(alerts) > 1:
                    print("│  " + "─"*62 + "  │")
        else:
            print("│  No active alerts                                                │")

        print("└" + "─"*66 + "┘")
        print()

    # Controls
    print("\n [Q] Quit  [D] Diagnostics  [A] Alerts  [H] Help  [R] Refresh")


def format_uptime(seconds):
    """Format uptime as HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def time_ago(iso_timestamp):
    """Format timestamp as relative time."""
    from datetime import datetime
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    now = datetime.utcnow()
    delta = now - dt

    if delta.seconds < 60:
        return "just now"
    elif delta.seconds < 3600:
        return f"{delta.seconds // 60} minutes ago"
    elif delta.seconds < 86400:
        return f"{delta.seconds // 3600} hours ago"
    else:
        return f"{delta.days} days ago"


# Usage
if __name__ == "__main__":
    # Initialize FAZA 20
    ux_layer = FAZA20Stack()
    ux_layer.initialize()
    ux_layer.start()

    # Display dashboard (refresh every 5 seconds)
    try:
        while True:
            display_dashboard(ux_layer)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        ux_layer.stop()
```

---

## Common Integration Patterns

### Pattern 1: Standalone FAZA 20

Use FAZA 20 independently for UX monitoring:

```python
from senti_os.core.faza20 import FAZA20Stack

# Initialize with no other FAZA layers
ux = FAZA20Stack()
ux.initialize()
ux.start()

# Use for basic monitoring
status = ux.status_collector.collect_status()
print(f"System Health: {status.overall_health.value}")

# Cleanup
ux.stop()
```

### Pattern 2: Full Stack Integration

Integrate all FAZA layers:

```python
from senti_os.core.faza16 import FAZA16Stack
from senti_os.core.faza17 import FAZA17Stack
from senti_os.core.faza19 import FAZA19Stack
from senti_os.core.faza21 import FAZA21Stack
from senti_os.core.faza20 import FAZA20Stack

# Initialize persistence first
persistence = FAZA21Stack()
persistence.initialize()

# Initialize other layers
llm_control = FAZA16Stack()
llm_control.initialize()

orchestration = FAZA17Stack()
orchestration.initialize()

uil = FAZA19Stack()
uil.initialize()

# Initialize UX layer with all dependencies
ux = FAZA20Stack(
    faza16_llm_control=llm_control,
    faza17_orchestration=orchestration,
    faza19_uil=uil,
    faza21_persistence=persistence
)
ux.initialize()
ux.start()

# Now you have full observability
diagnostics = ux.run_diagnostics(quick=False)
print(f"Full Diagnostics: {diagnostics.overall_status.value}")
```

### Pattern 3: Web API Wrapper (FastAPI)

Wrap UIAPI with FastAPI:

```python
from fastapi import FastAPI
from senti_os.core.faza20 import FAZA20Stack

app = FastAPI()

# Initialize FAZA 20
ux_layer = FAZA20Stack()
ux_layer.initialize()
ux_layer.start()

@app.get("/api/status")
def get_status():
    return ux_layer.ui_api.get_status()

@app.get("/api/diagnostics")
def get_diagnostics():
    return ux_layer.ui_api.get_diagnostics()

@app.post("/api/diagnostics/run")
def run_diagnostics(quick: bool = True):
    return ux_layer.ui_api.trigger_diagnostics(quick=quick)

@app.get("/api/alerts")
def get_alerts(level: str = None, limit: int = 50):
    return ux_layer.ui_api.get_alerts(level=level, limit=limit)

@app.post("/api/alerts/{alert_id}/dismiss")
def dismiss_alert(alert_id: str):
    return ux_layer.ui_api.dismiss_alert(alert_id)

# Run with: uvicorn main:app --reload
```

### Pattern 4: Scheduled Diagnostics

Run diagnostics on a schedule:

```python
import schedule
import time

def run_scheduled_diagnostics():
    """Run diagnostics every hour."""
    report = ux_layer.run_diagnostics(quick=False)

    if report.overall_status.value in ['error', 'critical']:
        # Send alert (email, Slack, etc.)
        print(f"ALERT: Diagnostics failed with {report.overall_status.value}")

        # Add to UX state
        ux_layer.ux_state_manager.add_alert(
            level=AlertLevel.ERROR,
            title="Scheduled Diagnostics Failed",
            message=f"{report.tests_failed} tests failed"
        )

# Schedule diagnostics
schedule.every().hour.do(run_scheduled_diagnostics)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Error Handling & Recovery

### Common Errors and Solutions

#### Error 1: Initialization Failure

**Symptom:**
```python
success = ux_layer.initialize()
# success = False
```

**Cause:**
- Missing dependencies
- Module registration failure
- Component initialization error

**Solution:**
```python
# Check status for details
status = ux_layer.get_status()
print(f"Initialized: {status['initialized']}")
print(f"Modules: {status['modules_registered']}")

# Check alerts
alerts = ux_layer.ux_state_manager.get_alerts(
    level=AlertLevel.ERROR,
    dismissed=False
)
for alert in alerts:
    print(f"Error: {alert.message}")
```

#### Error 2: Heartbeat Stopped

**Symptom:**
```
HeartbeatStatus.STOPPED for module
```

**Cause:**
- Module crashed or hung
- Network/communication failure
- Resource exhaustion

**Solution:**
```python
# Get heartbeat status
hb_status = ux_layer.heartbeat_monitor.get_heartbeat_status("faza16_llm_control")

if hb_status == HeartbeatStatus.STOPPED:
    # Get recent heartbeat history
    history = ux_layer.heartbeat_monitor.get_heartbeat_history("faza16_llm_control", limit=10)

    # Analyze failure pattern
    for record in history:
        print(f"{record.timestamp}: {record.status.value} ({record.response_time_ms}ms)")

    # Run diagnostics
    report = ux_layer.run_diagnostics(quick=False)
    # Check diagnostic results for root cause
```

#### Error 3: Diagnostics Failures

**Symptom:**
```
DiagnosticLevel.ERROR or DiagnosticLevel.CRITICAL
```

**Cause:**
- Module communication failure
- Persistence layer issues
- Key integrity problems

**Solution:**
```python
report = ux_layer.run_diagnostics(quick=False)

# Examine failed tests
failed_tests = [r for r in report.results if not r.passed]

for test in failed_tests:
    print(f"\n Test: {test.test_name}")
    print(f" Category: {test.category}")
    print(f" Level: {test.level.value}")
    print(f" Message: {test.message}")
    print(f" Details: {test.details}")

    # Take action based on category
    if test.category == "persistence":
        # Check FAZA 21
        if faza21:
            status = faza21.get_status()
            print(f" FAZA 21 Status: {status}")

    elif test.category == "communication":
        # Check module connectivity
        module_name = test.details.get('module')
        # Attempt reconnection or restart
```

#### Error 4: Onboarding Stuck

**Symptom:**
- Onboarding won't advance
- Step completion fails repeatedly

**Cause:**
- Missing module dependencies
- Invalid parameters
- State corruption

**Solution:**
```python
# Check current state
state = assistant.get_state()
print(f"Current Step: {state.current_step.value}")
print(f"Completed: {[s.value for s in state.steps_completed]}")

# Check last step result
current_step = state.current_step
result = assistant.get_step_result(current_step)

if result and not result.completed:
    print(f"Last Error: {result.message}")
    print(f"Details: {result.details}")

# Option 1: Retry current step
result = assistant.complete_step(current_step)

# Option 2: Reset onboarding
# WARNING: This erases all progress
ux_layer.ux_state_manager.update_state("onboarding", {})
assistant.start_onboarding()
```

---

## Monitoring & Observability

### Key Metrics to Track

#### 1. System Health Score

```python
def track_health_score():
    """Monitor health score trend."""
    scores = []

    for _ in range(60):  # 60 samples
        status = ux_layer.status_collector.collect_status()
        scores.append(status.overall_score)
        time.sleep(5)

    # Analyze trend
    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)

    print(f"Average Health: {avg_score:.2f}")
    print(f"Min: {min_score:.2f}, Max: {max_score:.2f}")

    # Alert if degrading
    if avg_score < 0.7:
        ux_layer.ux_state_manager.add_alert(
            level=AlertLevel.WARNING,
            title="System Health Degraded",
            message=f"Average health score: {avg_score:.2f}"
        )
```

#### 2. Heartbeat Success Rate

```python
def track_heartbeat_reliability():
    """Monitor heartbeat reliability."""
    stats = ux_layer.heartbeat_monitor.get_statistics()

    success_rate = stats['success_rate']
    total_beats = stats['total_beats']
    total_missed = stats['total_missed']

    # Alert if success rate drops
    if success_rate < 0.95:
        print(f"⚠ Heartbeat reliability degraded: {success_rate*100:.1f}%")
        print(f"   Missed: {total_missed}/{total_beats}")
```

#### 3. Alert Volume

```python
def track_alert_volume():
    """Monitor alert generation rate."""
    summary = ux_layer.ux_state_manager.get_alert_summary()

    print("Alert Summary:")
    print(f"  Total Active: {summary['total']}")
    print(f"  Info: {summary['info']}")
    print(f"  Warning: {summary['warning']}")
    print(f"  Error: {summary['error']}")
    print(f"  Critical: {summary['critical']}")

    # Alert on high error/critical count
    if summary['error'] + summary['critical'] > 5:
        print("⚠ High error/critical alert count!")
```

---

## Production Deployment

### Deployment Checklist

```
□ FAZA 21 persistence layer initialized with secure passphrase
□ FAZA 20 initialized with all required FAZA layers
□ Heartbeat monitoring started
□ Initial diagnostics run successfully (status: OK or WARNING)
□ Onboarding completed (if first deployment)
□ Logging configured (see below)
□ Monitoring dashboard deployed
□ Alert notification system configured
□ Backup and recovery procedures documented
□ Security audit completed
```

### Logging Configuration

```python
import logging

# Configure logging for FAZA 20
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/senti_os/faza20.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('faza20')

# Log key events
logger.info("FAZA 20 initializing...")
ux_layer.initialize()
logger.info("FAZA 20 initialized successfully")

ux_layer.start()
logger.info("FAZA 20 services started")

# Log diagnostics
report = ux_layer.run_diagnostics()
logger.info(f"Diagnostics: {report.overall_status.value}, {report.tests_passed}/{report.tests_run} passed")
```

### Health Check Endpoint

```python
@app.get("/health")
def health_check():
    """Health check endpoint for load balancers."""
    status = ux_layer.status_collector.collect_status()

    if status.overall_health.value == "healthy":
        return {"status": "healthy"}, 200
    elif status.overall_health.value == "degraded":
        return {"status": "degraded", "score": status.overall_score}, 200
    else:
        return {"status": "unhealthy"}, 503
```

---

## Troubleshooting Guide

### Issue: High CPU Usage

**Symptoms:**
- CPU usage >50% continuously
- Slow response times

**Diagnosis:**
```python
# Check heartbeat interval
stats = ux_layer.heartbeat_monitor.get_statistics()
print(f"Heartbeat interval: {stats['interval_seconds']}s")

# Check status collection frequency
info = ux_layer.status_collector.get_collection_info()
print(f"Collection frequency: {info['collection_frequency_seconds']}s")
```

**Solution:**
```python
# Increase intervals
ux_layer = FAZA20Stack(
    status_collection_frequency=10,  # was 5
    heartbeat_interval=20             # was 10
)
```

### Issue: Memory Leak

**Symptoms:**
- Memory usage grows over time
- Eventually leads to OOM

**Diagnosis:**
```python
# Check buffer sizes
explainability_stats = ux_layer.explainability_bridge.get_statistics()
print(f"Explainability entries: {explainability_stats['total_entries']}")

alert_summary = ux_layer.ux_state_manager.get_alert_summary()
print(f"Total alerts: {alert_summary['total']}")
```

**Solution:**
```python
# Clear old entries periodically
ux_layer.explainability_bridge.clear_entries()
ux_layer.ux_state_manager.clear_dismissed_alerts()
```

### Issue: Diagnostics Always Fail

**Symptoms:**
- Diagnostics return ERROR or CRITICAL
- Tests fail consistently

**Diagnosis:**
```python
report = ux_layer.run_diagnostics(quick=False)

# Group by category
by_category = {}
for result in report.results:
    category = result.category
    if category not in by_category:
        by_category[category] = []
    by_category[category].append(result)

# Print failures by category
for category, results in by_category.items():
    failed = [r for r in results if not r.passed]
    if failed:
        print(f"\n{category.upper()} Failures:")
        for r in failed:
            print(f"  - {r.test_name}: {r.message}")
```

**Solution:**
- If `registration` category fails: Register missing modules
- If `communication` category fails: Check module `get_status()` methods
- If `persistence` category fails: Verify FAZA 21 initialization
- If `uil` category fails: Verify FAZA 19 initialization

---

## Best Practices

### 1. Initialize in Correct Order

**Correct:**
```python
# 1. Persistence first
faza21 = FAZA21Stack()
faza21.initialize(passphrase="...")

# 2. Other FAZA layers
faza16 = FAZA16Stack()
faza16.initialize()

# 3. UX layer last
faza20 = FAZA20Stack(faza16_llm_control=faza16, faza21_persistence=faza21)
faza20.initialize()
faza20.start()
```

**Incorrect:**
```python
# ✗ Don't initialize UX before dependencies
faza20 = FAZA20Stack()
faza20.initialize()  # Missing dependencies!

faza21 = FAZA21Stack()
faza21.initialize()
```

### 2. Always Call start() After initialize()

```python
# ✓ Correct
ux_layer.initialize()
ux_layer.start()  # Starts heartbeat monitoring

# ✗ Incorrect (missing start)
ux_layer.initialize()
# Heartbeat monitoring won't start!
```

### 3. Handle Graceful Shutdown

```python
import signal
import sys

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print('\nShutting down FAZA 20...')
    ux_layer.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Now Ctrl+C will call stop() before exiting
```

### 4. Don't Block the Main Thread

```python
# ✗ Don't do this
while True:
    status = ux_layer.status_collector.collect_status()
    # This blocks heartbeat monitoring!

# ✓ Do this instead
import threading

def status_loop():
    while True:
        status = ux_layer.status_collector.collect_status()
        time.sleep(5)

thread = threading.Thread(target=status_loop, daemon=True)
thread.start()
```

### 5. Persist UX State Regularly

```python
# Persist important state changes
ux_layer.ux_state_manager.update_state("custom_category", {
    "last_action": "user_login",
    "timestamp": datetime.utcnow().isoformat()
})

# State is automatically encrypted and persisted to FAZA 21
```

---

## FAQ

**Q: Can I use FAZA 20 without other FAZA layers?**

A: Yes! FAZA 20 works standalone. You'll see warnings for missing modules in diagnostics, but core functionality (status collection, heartbeats, alerts) works independently.

**Q: How do I persist onboarding state across restarts?**

A: Onboarding state is automatically persisted via UXStateManager → FAZA 21. Just call `assistant.start_onboarding()` again, and it will resume from the last completed step.

**Q: What's the difference between quick and full diagnostics?**

A: Quick diagnostics (<1s) run only registration and communication tests. Full diagnostics (~2s) add persistence, UIL, LLM, and orchestration tests.

**Q: How do I customize heartbeat intervals?**

A:
```python
ux_layer = FAZA20Stack(
    heartbeat_interval=30,  # 30 seconds instead of default 10
    timeout_seconds=10       # 10 second timeout
)
```

**Q: Can I skip onboarding steps?**

A: Only `TEST_LLM_CONNECTIVITY` is skippable. All other steps are critical.

**Q: How do I export diagnostic results?**

A:
```python
import json

report = ux_layer.run_diagnostics()

# Convert to JSON
report_dict = {
    "timestamp": report.timestamp.isoformat(),
    "overall_status": report.overall_status.value,
    "tests_run": report.tests_run,
    "tests_passed": report.tests_passed,
    "results": [
        {
            "test": r.test_name,
            "passed": r.passed,
            "message": r.message
        }
        for r in report.results
    ]
}

with open('diagnostics.json', 'w') as f:
    json.dump(report_dict, f, indent=2)
```

**Q: How do I clear all UX state?**

A:
```python
# WARNING: This erases everything
ux_layer.ux_state_manager.reset_state()

# This clears:
# - Onboarding progress
# - All alerts
# - User preferences
# - Diagnostic results
```

**Q: Is FAZA 20 thread-safe?**

A: Yes. All components use threading locks for concurrent access. Heartbeat monitoring runs in a separate daemon thread.

**Q: How do I add custom alerts?**

A:
```python
from senti_os.core.faza20.ux_state_manager import AlertLevel

alert_id = ux_layer.ux_state_manager.add_alert(
    level=AlertLevel.INFO,
    title="Custom Event",
    message="Something interesting happened",
    metadata={"custom_key": "custom_value"}
)
```

---

## Summary

FAZA 20 provides a **complete, production-ready User Experience Layer** for SENTI OS with:

✓ **5-minute setup** from initialization to first diagnostics
✓ **Zero-configuration defaults** that work out of the box
✓ **Graceful degradation** when modules are unavailable
✓ **Comprehensive diagnostics** for troubleshooting
✓ **First-run onboarding** for guided setup
✓ **Real-time monitoring** via heartbeat and status collection
✓ **Privacy-first design** with encrypted persistence

**Next Steps:**
1. Follow the [First-Run Playbook](#first-run-playbook) to get started
2. Implement the [Terminal Comfort Dashboard](#terminal-comfort-dashboard) for visual monitoring
3. Set up [Production Deployment](#production-deployment) when ready
4. Refer to [Troubleshooting Guide](#troubleshooting-guide) if issues arise

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-02
**Feedback:** Report issues to SENTI OS Core Team
**License:** Proprietary
