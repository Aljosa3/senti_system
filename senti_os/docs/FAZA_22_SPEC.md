# FAZA 22 - SENTI Boot Layer - Technical Specification

**Version:** 1.0.0
**Date:** 2025-12-02
**Author:** SENTI OS Core Team
**License:** Proprietary

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Boot Flow](#boot-flow)
4. [Lifecycle State Machine](#lifecycle-state-machine)
5. [CLI Specification](#cli-specification)
6. [Health Monitoring](#health-monitoring)
7. [Event Model](#event-model)
8. [Component Specifications](#component-specifications)
9. [Regulatory Compliance](#regulatory-compliance)
10. [Security Considerations](#security-considerations)

---

## 1. Overview

### 1.1 Purpose

FAZA 22 is the Boot Layer for SENTI OS, providing unified system lifecycle management, command-line interface, health monitoring, and diagnostics. It orchestrates the initialization and coordination of all FAZA layers (16-21).

### 1.2 Key Features

- **Unified Boot Orchestration** - Manages boot sequence for all FAZA stacks
- **CLI Interface** - Complete command-line tool for system management
- **Health Monitoring** - Background sentinel process for system health
- **Log Management** - Centralized logging with rolling window (10,000 entries)
- **Visual Dashboard** - ASCII terminal rendering with real-time updates
- **Diagnostics** - Comprehensive system health checks

### 1.3 Design Principles

1. **Privacy First** - No passwords, no biometrics, GDPR/ZVOP compliant
2. **Fail-Safe** - Graceful degradation and safe shutdown
3. **Observable** - Complete visibility into system state
4. **Modular** - Each component independently testable
5. **Deterministic** - Predictable boot order and behavior

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      FAZA 22 - Boot Layer                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ CLI          │  │ Boot         │  │ Sentinel     │    │
│  │ Entrypoint   │─>│ Manager      │<─│ Process      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                 │                   │            │
│         v                 v                   v            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ CLI          │  │ Service      │  │ Logs         │    │
│  │ Commands     │  │ Registry     │  │ Manager      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                 │                   │            │
│         └─────────────────┴───────────────────┘            │
│                           │                                │
│                    ┌──────────────┐                        │
│                    │ CLI          │                        │
│                    │ Renderer     │                        │
│                    └──────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          v
    ┌─────────────────────────────────────────────┐
    │         FAZA Stacks (16-21)                 │
    │  FAZA 21 → FAZA 19 → FAZA 20 →             │
    │  FAZA 17 → FAZA 16 → FAZA 18               │
    └─────────────────────────────────────────────┘
```

### 2.2 Layer Architecture

```
┌─────────────────────────────────────────────┐
│  User Interface Layer                       │
│  - CLI Entrypoint (senti command)          │
│  - CLI Renderer (visual output)            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Command Layer                              │
│  - CLI Commands (start/stop/status/etc)    │
│  - Command routing and execution           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Orchestration Layer                        │
│  - Boot Manager (lifecycle orchestration)  │
│  - Service Registry (stack management)     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Monitoring Layer                           │
│  - Sentinel Process (health monitoring)    │
│  - Logs Manager (log aggregation)          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  FAZA Stacks Layer                          │
│  - FAZA 16, 17, 18, 19, 20, 21            │
└─────────────────────────────────────────────┘
```

### 2.3 Data Flow

```
User Command → CLI Entrypoint → CLI Commands → Boot Manager
                                                      ↓
                                        ┌─────────────┴─────────────┐
                                        v                           v
                               Service Registry              Logs Manager
                                        │                           │
                                        v                           v
                               FAZA Stacks Load             Event Logging
                                        │
                                        v
                               Stack Initialization
                                        │
                                        v
                               Sentinel Monitoring
```

---

## 3. Boot Flow

### 3.1 Boot Sequence

```
┌──────────────────────────────────────────────────────────┐
│ PHASE 1: PRE-BOOT                                        │
├──────────────────────────────────────────────────────────┤
│ 1. Initialize Boot Manager                              │
│ 2. Load Service Registry                                │
│ 3. Initialize Logs Manager                              │
│ 4. Validate configuration                               │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 2: STACK LOADING                                   │
├──────────────────────────────────────────────────────────┤
│ 1. Load FAZA 21 (Persistence Layer)                     │
│ 2. Load FAZA 19 (UIL & Multi-Device)                    │
│ 3. Load FAZA 20 (UX Layer)                              │
│ 4. Load FAZA 17 (Multi-Model Orchestration)             │
│ 5. Load FAZA 16 (LLM Control Layer)                     │
│ 6. Load FAZA 18 (Auth Flow Handler)                     │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 3: INITIALIZATION                                  │
├──────────────────────────────────────────────────────────┤
│ 1. Initialize FAZA 21 (create storage, load keys)       │
│ 2. Initialize FAZA 19 (setup event bus, devices)        │
│ 3. Initialize FAZA 20 (register modules, collectors)    │
│ 4. Initialize FAZA 17 (setup orchestration manager)     │
│ 5. Initialize FAZA 16 (load LLM manager)                │
│ 6. Initialize FAZA 18 (auth utilities loaded)           │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 4: SERVICE START                                   │
├──────────────────────────────────────────────────────────┤
│ 1. Start FAZA 19 services (WebSocket, event bus)        │
│ 2. Start FAZA 20 services (heartbeat, status)           │
│ 3. Emit boot events                                     │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 5: MONITORING                                      │
├──────────────────────────────────────────────────────────┤
│ 1. Start Sentinel Process                               │
│ 2. Begin health monitoring                              │
│ 3. System enters RUNNING state                          │
└──────────────────────────────────────────────────────────┘
```

### 3.2 Boot Order Rationale

| Order | FAZA | Reason |
|-------|------|--------|
| 1 | FAZA 21 | Foundation - all others may need persistence |
| 2 | FAZA 19 | Communication - event bus needed for coordination |
| 3 | FAZA 20 | Observability - monitor subsequent stack initialization |
| 4 | FAZA 17 | Orchestration - coordinates complex operations |
| 5 | FAZA 16 | LLM Control - depends on orchestration |
| 6 | FAZA 18 | Auth Flow - utility layer, minimal dependencies |

### 3.3 Error Handling During Boot

```
Stack Load Error → Log error → Mark stack as ERROR → Continue with next stack
                                                              ↓
                                                    All stacks loaded
                                                              ↓
                                          ┌─────────────────────────────────┐
                                          │ Any critical stack failed?      │
                                          └─────────────────────────────────┘
                                                  Yes ↓         ↓ No
                                          ┌─────────────┐   ┌────────────┐
                                          │ Boot FAILED │   │ Boot OK    │
                                          │ State=ERROR │   │ State=     │
                                          │             │   │ RUNNING    │
                                          └─────────────┘   └────────────┘
```

---

## 4. Lifecycle State Machine

### 4.1 Boot State Machine

```
                    ┌─────────────────┐
                    │ UNINITIALIZED   │ (Initial state)
                    └────────┬────────┘
                             │ start()
                             v
                    ┌─────────────────┐
              ┌────>│ INITIALIZING    │
              │     └────────┬────────┘
              │              │
              │              v
              │     ┌─────────────────┐
              │     │ INITIALIZED     │
              │     └────────┬────────┘
              │              │ start_services()
              │              v
              │     ┌─────────────────┐
              │     │ STARTING        │
              │     └────────┬────────┘
              │              │
    error     │              v
    ┌─────────┴────┐ ┌─────────────────┐
    │ ERROR        │ │ RUNNING         │<──┐
    └──────────────┘ └────────┬────────┘   │
                              │             │
                              │ restart()   │
                              │             │
                              v             │
                     ┌─────────────────┐    │
                     │ STOPPING        │    │
                     └────────┬────────┘    │
                              │             │
                              v             │
                     ┌─────────────────┐    │
                     │ STOPPED         │────┘
                     └─────────────────┘
```

### 4.2 Stack State Machine

```
┌──────────────┐
│ NOT_LOADED   │ (Initial)
└──────┬───────┘
       │ load_stack()
       v
┌──────────────┐
│ LOADED       │
└──────┬───────┘
       │ initialize()
       v
┌──────────────┐
│ INITIALIZING │
└──────┬───────┘
       │
       v
┌──────────────┐     start()      ┌──────────────┐
│ INITIALIZED  │─────────────────>│ STARTING     │
└──────────────┘                   └──────┬───────┘
       │                                  │
       │                                  v
       │                           ┌──────────────┐
       │                           │ RUNNING      │
       │                           └──────┬───────┘
       │                                  │ stop()
       │                                  v
       │                           ┌──────────────┐
       │                           │ STOPPING     │
       │                           └──────┬───────┘
       │                                  │
       v                                  v
┌──────────────┐                   ┌──────────────┐
│ ERROR        │                   │ STOPPED      │
└──────────────┘                   └──────────────┘
```

### 4.3 Sentinel State Machine

```
┌──────────────┐
│ STOPPED      │ (Initial)
└──────┬───────┘
       │ start()
       v
┌──────────────┐
│ STARTING     │
└──────┬───────┘
       │
       v
┌──────────────┐      error       ┌──────────────┐
│ RUNNING      │─────────────────>│ ERROR        │
└──────┬───────┘                   └──────────────┘
       │
       │ stop()
       v
┌──────────────┐
│ STOPPING     │
└──────┬───────┘
       │
       v
┌──────────────┐
│ STOPPED      │
└──────────────┘
```

---

## 5. CLI Specification

### 5.1 Command Reference

#### 5.1.1 `senti start`

**Description:** Start SENTI OS

**Usage:**
```bash
senti start
```

**Behavior:**
1. Check if already running (exit with error if true)
2. Initialize Boot Manager
3. Load all enabled FAZA stacks
4. Initialize stacks in boot order
5. Start services
6. Start Sentinel (if enabled)
7. Output success/failure message

**Exit Codes:**
- `0` - Success
- `1` - Already running or startup failed

**Example Output:**
```
SENTI OS started successfully (boot time: 2.34s)
```

#### 5.1.2 `senti stop`

**Description:** Stop SENTI OS

**Usage:**
```bash
senti stop
```

**Behavior:**
1. Check if running (exit with error if not)
2. Stop Sentinel (if running)
3. Stop stacks in reverse boot order
4. Shutdown persistence layer
5. Output success message

**Exit Codes:**
- `0` - Success
- `1` - Not running or shutdown failed

**Example Output:**
```
SENTI OS stopped successfully
```

#### 5.1.3 `senti restart`

**Description:** Restart SENTI OS

**Usage:**
```bash
senti restart
```

**Behavior:**
1. Execute stop sequence
2. Execute start sequence
3. Output success message

**Exit Codes:**
- `0` - Success
- `1` - Restart failed

#### 5.1.4 `senti status`

**Description:** Show system status

**Usage:**
```bash
senti status [--detailed] [--json]
```

**Options:**
- `--detailed` - Show detailed stack information
- `--json` - Output status as JSON

**Output (Simple):**
```
SENTI OS Status: RUNNING
Uptime: 123 seconds
Enabled Stacks: 6/6
Running Stacks: 6
Error Stacks: 0
```

**Output (Detailed):**
```
═══════════════════════════════════════════════════════════
                    SENTI OS DASHBOARD
═══════════════════════════════════════════════════════════

System State: RUNNING
Uptime: 00:02:03

FAZA STACKS
────────────────────────────────────────
  ✓ FAZA 21 - Persistence              running
  ✓ FAZA 19 - UIL                      running
  ✓ FAZA 20 - UX Layer                 running
  ✓ FAZA 17 - Orchestration            running
  ✓ FAZA 16 - LLM Control              running
  ✓ FAZA 18 - Auth Flow                running

HEALTH SUMMARY
────────────────────────────────────────
  Total Stacks: 6
  Enabled: 6
  Running: 6
  Errors: 0
```

#### 5.1.5 `senti logs`

**Description:** Show system logs

**Usage:**
```bash
senti logs [--level=LEVEL] [--limit=N]
```

**Options:**
- `--level=LEVEL` - Filter by level (debug/info/warning/error/critical)
- `--limit=N` - Show last N entries (default: 50)

**Example Output:**
```
[2025-12-02 14:30:00] INFO    Start command initiated
[2025-12-02 14:30:01] INFO    Starting SENTI OS...
[2025-12-02 14:30:03] INFO    SENTI OS started successfully
```

#### 5.1.6 `senti doctor`

**Description:** Run system diagnostics

**Usage:**
```bash
senti doctor [--quick]
```

**Options:**
- `--quick` - Run only essential checks

**Example Output:**
```
Diagnostic Results (5 checks):
  PASS: 4
  WARN: 1
  FAIL: 0

✓ System State: System is running
✓ Stack Health: All 6 stacks are healthy
✓ Persistence Layer: FAZA 21 initialized
✓ UIL Communication: FAZA 19 active (145 events)
⚠ Storage Directory: Storage directory not found: /path/to/storage
```

#### 5.1.7 `senti help`

**Description:** Show help information

**Usage:**
```bash
senti help
```

### 5.2 CLI Architecture

```
┌─────────────────────────────────────────────────┐
│ cli_entrypoint.py                               │
│ - Argument parsing (argparse)                   │
│ - Command routing                               │
│ - Error handling                                │
└────────────────────┬────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────┐
│ cli_commands.py                                 │
│ - start_command()                               │
│ - stop_command()                                │
│ - restart_command()                             │
│ - status_command()                              │
│ - logs_command()                                │
│ - doctor_command()                              │
│ - help_command()                                │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        v                         v
┌──────────────┐         ┌──────────────┐
│ boot_manager │         │ cli_renderer │
└──────────────┘         └──────────────┘
```

---

## 6. Health Monitoring

### 6.1 Sentinel Architecture

```
┌─────────────────────────────────────────────────┐
│ Sentinel Process (Background Thread)            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Monitoring Loop (every 5s)               │  │
│  │                                          │  │
│  │  1. Check each stack heartbeat          │  │
│  │  2. Detect stalls (no heartbeat > 30s)  │  │
│  │  3. Detect crashes (error status)       │  │
│  │  4. Emit events to FAZA 19              │  │
│  │  5. Trigger recovery (if enabled)       │  │
│  │  6. Safe shutdown (if critical)         │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 6.2 Health Check Results

| Status | Meaning | Action |
|--------|---------|--------|
| HEALTHY | Stack operating normally | Continue monitoring |
| DEGRADED | Stack running but suboptimal | Log warning, continue |
| STALLED | No heartbeat in timeout period | Alert, attempt recovery |
| CRASHED | Error status detected | Alert, shutdown if critical |
| UNKNOWN | Cannot determine status | Log, continue monitoring |

### 6.3 Recovery Strategy

```
┌───────────────────┐
│ Failure Detected  │
└─────────┬─────────┘
          │
          v
┌───────────────────┐      No      ┌──────────────┐
│ Auto-recovery     │─────────────>│ Log & Alert  │
│ enabled?          │               └──────────────┘
└─────────┬─────────┘
          │ Yes
          v
┌───────────────────┐
│ Attempt Recovery  │
│ - Call recovery   │
│   callback        │
│ - Restart stack   │
└─────────┬─────────┘
          │
          v
┌───────────────────┐      No      ┌──────────────┐
│ Recovery          │─────────────>│ Escalate     │
│ successful?       │               │ to critical  │
└─────────┬─────────┘               └──────────────┘
          │ Yes
          v
┌───────────────────┐
│ Resume monitoring │
└───────────────────┘
```

### 6.4 Safe Shutdown Conditions

Safe shutdown is triggered when:

1. **Critical Stack Failure** - Essential stack crashes > 3 times
2. **System Unhealthy** - >50% of stacks in unhealthy state
3. **Manual Trigger** - User explicitly requests shutdown
4. **Unrecoverable Error** - Error that cannot be recovered from

---

## 7. Event Model

### 7.1 Event Categories

```
┌─────────────────────────────────────────────────┐
│ Event Categories                                │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. boot    - Boot lifecycle events             │
│  2. system  - System-level events               │
│  3. stack   - Stack-specific events             │
│  4. health  - Health monitoring events          │
│  5. sentinel - Sentinel process events          │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 7.2 Boot Events

| Event Type | Category | Data | Emitted When |
|------------|----------|------|--------------|
| `boot_started` | boot | {message} | Boot sequence begins |
| `boot_completed` | boot | {message, boot_time} | Boot sequence completes |
| `boot_failed` | boot | {message, error} | Boot sequence fails |
| `stack_loaded` | boot | {stack_name, status} | Stack class loaded |
| `stack_initialized` | boot | {stack_name} | Stack initialized |
| `stack_started` | boot | {stack_name} | Stack services started |
| `stack_stopped` | boot | {stack_name} | Stack services stopped |
| `stack_error` | boot | {stack_name, error} | Stack encounters error |

### 7.3 Sentinel Events

| Event Type | Category | Data | Emitted When |
|------------|----------|------|--------------|
| `sentinel_started` | sentinel | {message} | Sentinel begins monitoring |
| `sentinel_stopped` | sentinel | {message} | Sentinel stops |
| `stack_stalled` | health | {stack_name} | Stack heartbeat timeout |
| `stack_crashed` | health | {stack_name, error} | Stack crashes |
| `stack_degraded` | health | {stack_name} | Stack in degraded state |
| `safe_shutdown_triggered` | system | {reason} | Safe shutdown initiated |

### 7.4 Event Flow

```
Boot Manager → FAZA 19 Event Bus → Subscribers
                      │
                      ├─> FAZA 20 (UX Layer)
                      ├─> Logs Manager
                      └─> External Listeners
```

---

## 8. Component Specifications

### 8.1 BootManager

**File:** `boot_manager.py`

**Responsibilities:**
- Orchestrate boot sequence
- Manage stack lifecycle
- Emit boot events
- Track system state

**Key Methods:**
- `start()` - Start system
- `stop()` - Stop system
- `restart()` - Restart system
- `get_status()` - Get system status
- `is_healthy()` - Check system health

**Configuration:**
```python
BootManager(
    storage_dir="/path/to/storage",
    enable_persistence=True,
    enable_uil=True,
    enable_ux=True,
    enable_orchestration=True,
    enable_llm_control=True,
    enable_auth_flow=True
)
```

### 8.2 ServiceRegistry

**File:** `service_registry.py`

**Responsibilities:**
- Maintain stack metadata
- Provide factory functions
- Validate boot order
- Singleton boot manager access

**Stack Metadata:**
```python
StackMetadata(
    name="faza21",
    faza_number=21,
    display_name="FAZA 21 - Persistence Layer",
    description="...",
    stack_type=StackType.PERSISTENCE,
    has_start_method=False,
    has_stop_method=True,
    has_status_method=True,
    dependencies=[]
)
```

### 8.3 LogsManager

**File:** `logs_manager.py`

**Responsibilities:**
- Centralized log collection
- Rolling window storage (max 10,000)
- Thread-safe operations
- Log querying and filtering

**Configuration:**
```python
LogsManager(
    max_entries=10000,
    persist_to_disk=False,
    log_file="/path/to/log.json"
)
```

### 8.4 SentinelProcess

**File:** `sentinel_process.py`

**Responsibilities:**
- Background health monitoring
- Heartbeat tracking
- Auto-recovery (optional)
- Safe shutdown triggering

**Configuration:**
```python
SentinelConfig(
    check_interval_seconds=5,
    heartbeat_timeout_seconds=30,
    max_errors_before_alert=3,
    auto_recovery_enabled=False,
    safe_shutdown_on_critical=True
)
```

### 8.5 CLIRenderer

**File:** `cli_renderer.py`

**Responsibilities:**
- ASCII terminal rendering
- Animated loading indicators
- Health status visualization
- Dashboard display

**Configuration:**
```python
RenderConfig(
    use_colors=True,
    use_unicode=True,
    terminal_width=80
)
```

---

## 9. Regulatory Compliance

### 9.1 GDPR Compliance

**Article 5 - Data Processing Principles:**
- ✅ **Lawfulness, fairness, transparency** - All diagnostics are safe and transparent
- ✅ **Purpose limitation** - Only system monitoring data collected
- ✅ **Data minimization** - Minimal data collected (no personal data)
- ✅ **Accuracy** - Log data is accurate and timestamped
- ✅ **Storage limitation** - Rolling window (max 10,000 entries)
- ✅ **Integrity and confidentiality** - Logs stored securely

**Article 25 - Data Protection by Design:**
- ✅ Default to minimal logging
- ✅ No passwords or biometrics ever logged
- ✅ Privacy-first architecture

### 9.2 ZVOP Compliance (Slovenian Data Protection)

FAZA 22 complies with Zakon o varstvu osebnih podatkov (ZVOP):
- ✅ No collection of personal data without explicit consent
- ✅ Data minimization principle applied
- ✅ Secure processing of system diagnostics
- ✅ Right to deletion (clear logs functionality)

### 9.3 EU AI Act Compliance

**Article 9 - Risk Management System:**
- ✅ Comprehensive health monitoring
- ✅ Failure detection and safe shutdown
- ✅ Complete audit trail of system operations

**Article 12 - Record-Keeping:**
- ✅ All system events logged with timestamps
- ✅ Boot events, errors, and recovery attempts tracked
- ✅ Log export functionality for auditing

**Article 13 - Transparency:**
- ✅ Complete visibility into system state
- ✅ CLI status and diagnostics commands
- ✅ Real-time dashboard

### 9.4 Privacy Guarantees

**CRITICAL - What FAZA 22 NEVER Does:**
1. ❌ Store passwords
2. ❌ Collect biometric data
3. ❌ Log sensitive user information
4. ❌ Make external network calls
5. ❌ Process personal data

**What FAZA 22 DOES:**
1. ✅ Log system events (boot, shutdown, errors)
2. ✅ Monitor stack health (internal metrics only)
3. ✅ Collect diagnostics (safe for audit)
4. ✅ Track performance metrics (response times, uptimes)

---

## 10. Security Considerations

### 10.1 Threat Model

**Assets:**
- System configuration
- Boot state
- Log data
- Stack credentials (managed by FAZA 21, not 22)

**Threats:**
1. **Unauthorized system control** - Mitigated by OS-level permissions
2. **Log tampering** - Mitigated by FAZA 21 encryption (if enabled)
3. **Denial of service** - Mitigated by sentinel watchdog
4. **Information disclosure** - No sensitive data in logs

### 10.2 Security Controls

1. **Access Control**
   - CLI requires appropriate OS permissions
   - State files protected by filesystem permissions

2. **Data Protection**
   - Logs contain no sensitive data
   - Optional persistence encryption via FAZA 21

3. **Availability**
   - Sentinel monitors system health
   - Safe shutdown prevents data corruption
   - Auto-recovery (configurable)

4. **Audit Trail**
   - Complete event logging
   - Timestamps on all events
   - Export functionality for audit

### 10.3 Secure Defaults

```python
# Secure default configuration
FAZA22Stack(
    enable_sentinel=True,        # Monitoring enabled
    enable_persistence=True,     # Safe storage
    storage_dir="/secure/path"   # Protected directory
)

SentinelConfig(
    auto_recovery_enabled=False,     # Manual recovery
    safe_shutdown_on_critical=True   # Prevent data loss
)

LogsManager(
    persist_to_disk=False,  # No disk persistence by default
    max_entries=10000       # Limited memory usage
)
```

---

## Appendix A: Boot Order Dependency Graph

```
     FAZA 21 (Persistence)
          │
          └─────────┬──────────────┐
                    │              │
                    v              v
         FAZA 19 (UIL)      FAZA 16 (LLM)
                    │              │
                    └──────┬───────┤
                           │       │
                           v       v
                    FAZA 20 (UX) FAZA 17 (Orch)
                           │       │
                           └───┬───┘
                               │
                               v
                        FAZA 18 (Auth)
```

---

## Appendix B: File Structure

```
senti_os/core/faza22/
├── __init__.py              # Main FAZA22Stack class
├── boot_manager.py          # Boot orchestration
├── cli_commands.py          # CLI command implementations
├── cli_entrypoint.py        # CLI entry point
├── cli_renderer.py          # Terminal rendering
├── logs_manager.py          # Log management
├── sentinel_process.py      # Health monitoring
└── service_registry.py      # Stack registry

senti_os/tests/faza22/
└── test_faza22_comprehensive.py  # 73+ tests

senti_os/docs/
├── FAZA_22_SPEC.md          # This document
└── FAZA_22_IMPLEMENTATION_GUIDE.md
```

---

**End of Specification**

**Document Version:** 1.0.0
**Last Updated:** 2025-12-02
**Status:** Complete
