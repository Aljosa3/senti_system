# FAZA 22 - Implementation Guide

**Version:** 1.0.0
**Date:** 2025-12-02
**Author:** SENTI OS Core Team
**License:** Proprietary

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [First Run](#first-run)
4. [Usage Examples](#usage-examples)
5. [Dashboard Guide](#dashboard-guide)
6. [Advanced Configuration](#advanced-configuration)
7. [Integration Guide](#integration-guide)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## 1. Getting Started

### 1.1 Prerequisites

Before using FAZA 22, ensure you have:

- **Python 3.10+** installed
- **SENTI OS** base system configured
- **FAZA layers 16-21** available (if you want to enable them)
- **Permissions** to create directories in `/home/pisarna/senti_system/data/`

### 1.2 Quick Start

The fastest way to get started with FAZA 22:

```python
from senti_os.core.faza22 import FAZA22Stack

# Create minimal stack (no FAZA dependencies)
stack = FAZA22Stack(
    enable_persistence=False,
    enable_uil=False,
    enable_ux=False,
    enable_orchestration=False,
    enable_llm_control=False,
    enable_auth_flow=False,
    enable_sentinel=False
)

# Start the system
stack.start()

# Check status
status = stack.get_status()
print(f"System running: {stack.is_running()}")

# Stop when done
stack.stop()
```

### 1.3 Full System Start

To start SENTI OS with all FAZA layers:

```python
from senti_os.core.faza22 import FAZA22Stack

# Create full stack
stack = FAZA22Stack(
    storage_dir="/home/pisarna/senti_system/data/faza21",
    enable_persistence=True,
    enable_uil=True,
    enable_ux=True,
    enable_orchestration=True,
    enable_llm_control=True,
    enable_auth_flow=True,
    enable_sentinel=True
)

# Start the system
if stack.start():
    print("✓ SENTI OS started successfully")
else:
    print("✗ Failed to start SENTI OS")
```

---

## 2. Installation

### 2.1 Installing the `senti` Command

To use the `senti` command-line tool, you have two options:

#### Option A: Direct Python Execution

Run the CLI entrypoint directly with Python:

```bash
# From the senti_system directory
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH \
    python3 -m senti_os.core.faza22.cli_entrypoint start
```

#### Option B: Create Shell Script (Recommended)

Create a shell script wrapper:

```bash
# Create the script
cat > /usr/local/bin/senti << 'EOF'
#!/bin/bash
export PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH
exec python3 -m senti_os.core.faza22.cli_entrypoint "$@"
EOF

# Make it executable
chmod +x /usr/local/bin/senti

# Test it
senti --version
```

#### Option C: Python Entry Point (Setup.py)

If you have a `setup.py`, add this entry point:

```python
setup(
    name="senti-os",
    # ... other settings ...
    entry_points={
        'console_scripts': [
            'senti=senti_os.core.faza22.cli_entrypoint:run',
        ],
    },
)
```

Then install with:

```bash
pip install -e /home/pisarna/senti_system
```

### 2.2 Verify Installation

Test that the `senti` command works:

```bash
# Should show version
senti --version

# Should show help
senti help

# Should show current status
senti status
```

---

## 3. First Run

### 3.1 Initial System Start

The first time you start SENTI OS:

```bash
# Start the system
senti start
```

**Expected Output:**
```
Starting SENTI OS...
✓ FAZA 21 - Persistence Layer loaded
✓ FAZA 19 - UIL loaded
✓ FAZA 20 - UX Layer loaded
✓ FAZA 17 - Orchestration loaded
✓ FAZA 16 - LLM Control loaded
✓ FAZA 18 - Auth Flow loaded

SENTI OS started successfully (boot time: 2.34s)
```

### 3.2 Check System Status

After starting, verify everything is running:

```bash
senti status --detailed
```

**Expected Output:**
```
═══════════════════════════════════════════════════════════
                    SENTI OS DASHBOARD
═══════════════════════════════════════════════════════════

System State: RUNNING
Uptime: 00:00:05

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

RECENT EVENTS
────────────────────────────────────────
  2025-12-02 14:30:00 boot_started: SENTI OS boot sequence initiated
  2025-12-02 14:30:01 stack_loaded: FAZA 21 Persistence Layer loaded
  2025-12-02 14:30:02 boot_completed: SENTI OS boot completed in 2.34s

────────────────────────────────────────────────────────────
```

### 3.3 Run Diagnostics

Run the built-in health checks:

```bash
senti doctor
```

**Expected Output:**
```
Diagnostic Results (5 checks):
  PASS: 5
  WARN: 0
  FAIL: 0

✓ System State: System is running
✓ Stack Health: All 6 stacks are healthy
✓ Persistence Layer: FAZA 21 initialized
✓ UIL Communication: FAZA 19 active (0 events)
✓ Storage Directory: Storage directory exists: /home/pisarna/senti_system/data/faza21
```

### 3.4 View Logs

Check system logs:

```bash
# Show last 20 log entries
senti logs --limit=20

# Show only errors
senti logs --level=error
```

---

## 4. Usage Examples

### 4.1 Basic Operations

#### Start System

```bash
senti start
```

#### Stop System

```bash
senti stop
```

#### Restart System

```bash
senti restart
```

#### Check Status

```bash
# Simple status
senti status

# Detailed status with dashboard
senti status --detailed

# JSON output (for scripting)
senti status --json
```

### 4.2 Log Management

#### View Recent Logs

```bash
# Default: last 50 entries
senti logs

# Last 100 entries
senti logs --limit=100

# Only errors
senti logs --level=error

# Only warnings
senti logs --level=warning
```

#### Example Log Output

```
[2025-12-02 14:30:00] INFO    Start command initiated
[2025-12-02 14:30:01] INFO    Starting SENTI OS...
[2025-12-02 14:30:01] INFO    Loading FAZA stacks
[2025-12-02 14:30:02] INFO    FAZA 21 Persistence Layer loaded
[2025-12-02 14:30:02] INFO    FAZA 19 UIL loaded
[2025-12-02 14:30:03] INFO    SENTI OS started successfully
```

### 4.3 Diagnostics

#### Run Full Diagnostics

```bash
senti doctor
```

#### Run Quick Diagnostics

```bash
senti doctor --quick
```

#### Example Diagnostic Output

```
Diagnostic Results (10 checks):
  PASS: 8
  WARN: 2
  FAIL: 0

✓ System State: System is running
✓ Stack Health: All 6 stacks are healthy
✓ Persistence Layer: FAZA 21 initialized
✓ UIL Communication: FAZA 19 active (145 events)
✓ Storage Directory: Storage directory exists
✓ FAZA20: Status Collection: OK
✓ FAZA20: Heartbeat Monitor: OK
⚠ FAZA20: Diagnostics Engine: Some non-critical issues detected
✓ FAZA20: UX State Manager: OK
⚠ Memory Usage: High memory usage detected (85%)
```

### 4.4 Scripting with senti

#### Check if System is Running (Bash)

```bash
#!/bin/bash

if senti status > /dev/null 2>&1; then
    echo "SENTI OS is running"
    exit 0
else
    echo "SENTI OS is not running"
    exit 1
fi
```

#### Auto-restart on Failure

```bash
#!/bin/bash

while true; do
    if ! senti status > /dev/null 2>&1; then
        echo "System down, restarting..."
        senti restart
    fi
    sleep 60
done
```

#### Parse JSON Status (Python)

```python
import subprocess
import json

result = subprocess.run(
    ["senti", "status", "--json"],
    capture_output=True,
    text=True
)

status = json.loads(result.stdout)
print(f"System state: {status['system']['state']}")
print(f"Running stacks: {status['health']['running_stacks']}")
```

### 4.5 Programmatic Usage

#### Python Integration

```python
from senti_os.core.faza22 import FAZA22Stack

# Create and configure stack
stack = FAZA22Stack(
    storage_dir="/custom/path",
    enable_sentinel=True
)

# Start
if stack.start():
    print("System started")

    # Get detailed status
    status = stack.get_status()
    print(f"Boot manager state: {status['boot_manager']['system']['state']}")
    print(f"Logs count: {status['logs']['current_entries']}")

    # Get specific components
    boot_manager = stack.get_boot_manager()
    logs_manager = stack.get_logs_manager()
    sentinel = stack.get_sentinel()

    # Check health
    if stack.is_healthy():
        print("System is healthy")

    # Stop when done
    stack.stop()
```

#### Custom Boot Configuration

```python
from senti_os.core.faza22.boot_manager import BootManager

# Create custom boot manager
manager = BootManager(
    storage_dir="/custom/storage",
    enable_persistence=True,
    enable_uil=True,
    enable_ux=False,          # Disable UX layer
    enable_orchestration=True,
    enable_llm_control=True,
    enable_auth_flow=False    # Disable auth flow
)

# Start with custom configuration
manager.start()

# Get specific stack
faza21 = manager.get_stack("faza21")
if faza21:
    faza21_status = faza21.get_status()
    print(f"Persistence initialized: {faza21_status['initialized']}")
```

#### Custom Sentinel Configuration

```python
from senti_os.core.faza22.sentinel_process import SentinelProcess, SentinelConfig
from senti_os.core.faza22 import get_logs_manager

# Create custom sentinel config
config = SentinelConfig(
    check_interval_seconds=10,      # Check every 10 seconds
    heartbeat_timeout_seconds=60,   # 60 second timeout
    max_errors_before_alert=5,
    auto_recovery_enabled=True,      # Enable auto-recovery
    safe_shutdown_on_critical=False  # Don't auto-shutdown
)

# Create sentinel
logs = get_logs_manager()
sentinel = SentinelProcess(boot_manager, logs, config)

# Register custom callbacks
def on_stall(stack_name, health_record):
    print(f"ALERT: {stack_name} is stalled!")

def on_crash(stack_name, health_record):
    print(f"CRITICAL: {stack_name} crashed: {health_record.last_error}")

sentinel.register_stall_callback(on_stall)
sentinel.register_crash_callback(on_crash)

# Start monitoring
sentinel.start()
```

---

## 5. Dashboard Guide

### 5.1 Dashboard Overview

The detailed status dashboard shows:

```
═══════════════════════════════════════════════════════════
                    SENTI OS DASHBOARD
═══════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────┐
│ SYSTEM STATE                                            │
├─────────────────────────────────────────────────────────┤
│ State:     RUNNING                                      │
│ Uptime:    00:15:23                                     │
│ Boot time: 2025-12-02 14:30:00                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ FAZA STACKS                                             │
├─────────────────────────────────────────────────────────┤
│  ✓ FAZA 21 - Persistence              running          │
│  ✓ FAZA 19 - UIL                      running          │
│  ✓ FAZA 20 - UX Layer                 running          │
│  ✓ FAZA 17 - Orchestration            running          │
│  ✓ FAZA 16 - LLM Control              running          │
│  ✓ FAZA 18 - Auth Flow                running          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ HEALTH SUMMARY                                          │
├─────────────────────────────────────────────────────────┤
│  Total Stacks:    6                                     │
│  Enabled:         6                                     │
│  Running:         6                                     │
│  Errors:          0                                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ RECENT EVENTS                                           │
├─────────────────────────────────────────────────────────┤
│  14:30:00  boot_started: Boot sequence initiated       │
│  14:30:02  stack_loaded: FAZA 21 loaded                │
│  14:30:03  boot_completed: Boot completed (2.34s)      │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Status Indicators

| Symbol | Meaning | Color |
|--------|---------|-------|
| ✓ | Healthy / OK | Green |
| ⚠ | Warning / Degraded | Yellow |
| ✗ | Failed / Error | Red |
| ℹ | Info / Unknown | Gray |

### 5.3 Reading Dashboard Data

#### System State

- **UNINITIALIZED** - System not yet started
- **INITIALIZING** - Currently starting up
- **RUNNING** - Operating normally
- **STOPPING** - Shutting down
- **STOPPED** - Not running
- **ERROR** - Fatal error occurred

#### Stack Status

Each FAZA stack shows:
- Symbol (✓/⚠/✗)
- Name and description
- Current status (loaded/initialized/running/error)
- Error message (if applicable)

#### Health Summary

- **Total Stacks** - Number of FAZA stacks registered
- **Enabled** - Number of stacks enabled in configuration
- **Running** - Number of stacks currently running
- **Errors** - Number of stacks with errors

---

## 6. Advanced Configuration

### 6.1 Custom Storage Location

```python
from senti_os.core.faza22 import FAZA22Stack

stack = FAZA22Stack(
    storage_dir="/mnt/secure-storage/senti_data",
    # ... other options
)
```

### 6.2 Selective Stack Enabling

Enable only specific FAZA layers:

```python
# Only persistence and LLM control
stack = FAZA22Stack(
    enable_persistence=True,
    enable_uil=False,
    enable_ux=False,
    enable_orchestration=False,
    enable_llm_control=True,
    enable_auth_flow=False,
    enable_sentinel=True
)
```

### 6.3 Custom Logging Configuration

```python
from senti_os.core.faza22.logs_manager import LogsManager

# Custom log manager
logs = LogsManager(
    max_entries=50000,  # Increase to 50K entries
    persist_to_disk=True,
    log_file="/var/log/senti_os/system.log"
)

# Use with CLI commands
from senti_os.core.faza22.cli_commands import CLICommands

cli = CLICommands(
    storage_dir="/custom/path",
    state_file="/custom/state.json"
)
```

### 6.4 Disable Colors in Output

For piping output to files or scripts:

```python
from senti_os.core.faza22.cli_renderer import CLIRenderer, RenderConfig

config = RenderConfig(
    use_colors=False,     # Disable colors
    use_unicode=True,     # Keep Unicode symbols
    terminal_width=80
)

renderer = CLIRenderer(config)
```

Or via environment variable:

```bash
export NO_COLOR=1
senti status --detailed
```

### 6.5 Background Service (systemd)

Create a systemd service for SENTI OS:

```ini
# /etc/systemd/system/senti.service

[Unit]
Description=SENTI OS System
After=network.target

[Service]
Type=simple
User=senti
Group=senti
WorkingDirectory=/home/pisarna/senti_system
Environment="PYTHONPATH=/home/pisarna/senti_system"
ExecStart=/usr/bin/python3 -m senti_os.core.faza22.cli_entrypoint start
ExecStop=/usr/bin/python3 -m senti_os.core.faza22.cli_entrypoint stop
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable senti.service
sudo systemctl start senti.service
sudo systemctl status senti.service
```

---

## 7. Integration Guide

### 7.1 Integrating with Existing Code

#### Import FAZA 22 in Your Application

```python
from senti_os.core.faza22 import FAZA22Stack

class MyApplication:
    def __init__(self):
        self.senti = FAZA22Stack(
            enable_persistence=True,
            enable_uil=True
            # ... configure as needed
        )

    def startup(self):
        """Start SENTI OS during app startup"""
        if not self.senti.start():
            raise RuntimeError("Failed to start SENTI OS")

    def shutdown(self):
        """Stop SENTI OS during app shutdown"""
        self.senti.stop()

    def get_system_health(self):
        """Get system health for monitoring"""
        return self.senti.is_healthy()
```

### 7.2 Event Integration

Subscribe to SENTI OS events:

```python
# Get FAZA 19 event bus
faza19 = stack.get_boot_manager().get_stack("faza19")
if faza19:
    event_bus = faza19.event_bus

    # Subscribe to boot events
    def on_boot_event(event):
        print(f"Boot event: {event.event_type} - {event.data}")

    event_bus.subscribe(
        category="boot",
        event_type="boot_completed",
        callback=on_boot_event
    )
```

### 7.3 Custom Health Checks

Add custom health checks to diagnostics:

```python
from senti_os.core.faza22.cli_commands import CLICommands

class CustomCLICommands(CLICommands):
    def doctor_command(self, quick=False):
        # Run default diagnostics
        result = super().doctor_command(quick)

        # Add custom checks
        if result.data:
            result.data["checks"].append({
                "name": "Custom Check",
                "status": "PASS",
                "message": "Custom system check passed"
            })

        return result
```

### 7.4 Log Forwarding

Forward SENTI logs to external system:

```python
from senti_os.core.faza22.logs_manager import LogsManager
import requests

class ForwardingLogsManager(LogsManager):
    def append_log(self, level, message, component=None, details=None):
        # Call parent
        super().append_log(level, message, component, details)

        # Forward to external system
        try:
            requests.post("https://logs.example.com/ingest", json={
                "level": level,
                "message": message,
                "component": component,
                "timestamp": datetime.now().isoformat()
            }, timeout=1)
        except:
            pass  # Don't fail on forward errors
```

---

## 8. Troubleshooting

### 8.1 Common Issues

#### Issue: System Won't Start

**Symptoms:**
```
Error: Failed to start SENTI OS
```

**Solutions:**

1. Check if already running:
```bash
senti status
```

2. Check logs for errors:
```bash
senti logs --level=error
```

3. Run diagnostics:
```bash
senti doctor
```

4. Check storage directory permissions:
```bash
ls -la /home/pisarna/senti_system/data/
```

5. Try with minimal configuration:
```python
stack = FAZA22Stack(
    enable_persistence=False,
    enable_uil=False,
    # ... disable all
)
```

#### Issue: Stack Fails to Load

**Symptoms:**
```
✗ FAZA 21 - Persistence Layer failed to load
Error: Module not found
```

**Solutions:**

1. Check PYTHONPATH:
```bash
echo $PYTHONPATH
# Should include: /home/pisarna/senti_system
```

2. Verify FAZA module exists:
```bash
ls -la /home/pisarna/senti_system/senti_os/core/faza21/
```

3. Try importing manually:
```python
from senti_os.core.faza21 import FAZA21Stack
```

#### Issue: High Memory Usage

**Symptoms:**
```
⚠ Memory Usage: High memory usage detected (95%)
```

**Solutions:**

1. Reduce log buffer size:
```python
logs_manager = LogsManager(max_entries=1000)  # Reduce from 10000
```

2. Disable sentinel:
```python
stack = FAZA22Stack(enable_sentinel=False)
```

3. Disable unnecessary stacks:
```python
stack = FAZA22Stack(
    enable_ux=False,
    enable_orchestration=False
)
```

#### Issue: Sentinel Detects Stalls

**Symptoms:**
```
WARNING: Stack faza20 appears stalled (no heartbeat)
```

**Solutions:**

1. Increase heartbeat timeout:
```python
config = SentinelConfig(heartbeat_timeout_seconds=60)
```

2. Check stack status:
```bash
senti status --detailed
```

3. Restart the system:
```bash
senti restart
```

### 8.2 Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from senti_os.core.faza22 import FAZA22Stack
stack = FAZA22Stack()
stack.start()
```

Or via CLI:

```bash
SENTI_DEBUG=1 senti start
```

### 8.3 Log Analysis

#### Find All Errors

```bash
senti logs --level=error | grep -i "error"
```

#### Track Boot Issues

```bash
senti logs | grep -i "boot"
```

#### Monitor Specific Stack

```python
logs_manager = get_logs_manager()
faza21_logs = logs_manager.get_component_logs("faza21")
for log in faza21_logs:
    print(log["message"])
```

### 8.4 Recovery Procedures

#### Force Stop

If normal stop doesn't work:

```python
import os
import signal

# Get PID of SENTI process
# Send SIGTERM
os.kill(pid, signal.SIGTERM)
```

#### Clean State

Remove state files to start fresh:

```bash
rm -f /home/pisarna/senti_system/data/faza22/boot_state.json
rm -f /home/pisarna/senti_system/data/faza22/senti_os.log
```

#### Reset All Data

**WARNING: This will delete all SENTI data**

```bash
rm -rf /home/pisarna/senti_system/data/faza21/*
rm -rf /home/pisarna/senti_system/data/faza22/*
```

---

## 9. Best Practices

### 9.1 Production Deployment

1. **Use systemd service** for automatic restart
2. **Enable sentinel monitoring** for health checks
3. **Configure log persistence** for audit trail
4. **Set up external monitoring** (Prometheus, Grafana)
5. **Regular backups** of FAZA 21 storage

### 9.2 Development Workflow

```python
# Development configuration
dev_stack = FAZA22Stack(
    storage_dir="/tmp/senti_dev",
    enable_sentinel=False,      # Disable for faster iteration
    enable_persistence=False    # Use in-memory only
)

# Run tests
dev_stack.start()
# ... your tests ...
dev_stack.stop()
```

### 9.3 Monitoring Recommendations

1. **Track uptime** - Monitor system uptime and restarts
2. **Log errors** - Set up alerts for error logs
3. **Health checks** - Run `senti doctor` periodically
4. **Performance metrics** - Track boot time, response times
5. **Resource usage** - Monitor memory and CPU

### 9.4 Security Best Practices

1. **File permissions** - Restrict access to storage directory:
```bash
chmod 700 /home/pisarna/senti_system/data/
```

2. **User isolation** - Run SENTI as dedicated user:
```bash
sudo useradd -r -s /bin/false senti
sudo chown -R senti:senti /home/pisarna/senti_system/data/
```

3. **No sudo** - SENTI should never require root privileges

4. **Audit logs** - Regularly review logs for suspicious activity:
```bash
senti logs --level=error > security_audit.log
```

### 9.5 Performance Optimization

1. **Disable unused stacks** - Only enable what you need
2. **Adjust log buffer** - Balance memory vs. history
3. **Sentinel interval** - Increase check interval if needed
4. **Async operations** - Use async/await for I/O operations

### 9.6 Maintenance Schedule

**Daily:**
- Check system status: `senti status`
- Review error logs: `senti logs --level=error`

**Weekly:**
- Run full diagnostics: `senti doctor`
- Review system uptime and restarts
- Check storage usage

**Monthly:**
- Review and rotate logs
- Update FAZA dependencies
- Security audit of logs

---

## Appendix A: Complete Configuration Example

```python
from senti_os.core.faza22 import FAZA22Stack
from senti_os.core.faza22.sentinel_process import SentinelConfig
from senti_os.core.faza22.logs_manager import LogsManager

# Configure logging
logs_manager = LogsManager(
    max_entries=20000,
    persist_to_disk=True,
    log_file="/var/log/senti/system.log"
)

# Configure sentinel
sentinel_config = SentinelConfig(
    check_interval_seconds=10,
    heartbeat_timeout_seconds=45,
    max_errors_before_alert=5,
    auto_recovery_enabled=True,
    safe_shutdown_on_critical=True,
    emit_events=True
)

# Create stack
stack = FAZA22Stack(
    storage_dir="/var/lib/senti/data",
    enable_sentinel=True,
    enable_persistence=True,
    enable_uil=True,
    enable_ux=True,
    enable_orchestration=True,
    enable_llm_control=True,
    enable_auth_flow=True
)

# Configure sentinel
if stack.sentinel:
    stack.sentinel.config = sentinel_config

# Start system
if stack.start():
    print("✓ SENTI OS production system started")

    # Production monitoring loop
    import time
    while True:
        if not stack.is_healthy():
            print("⚠ System unhealthy!")
            # Alert admin

        time.sleep(60)
```

---

## Appendix B: Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `PYTHONPATH` | Python module search path | - |
| `SENTI_STORAGE_DIR` | Override storage directory | `/home/pisarna/senti_system/data/faza21` |
| `SENTI_DEBUG` | Enable debug logging | `0` |
| `NO_COLOR` | Disable colored output | `0` |
| `SENTI_LOG_LEVEL` | Set log level | `info` |

---

## Appendix C: Quick Reference

### CLI Commands

```bash
senti start              # Start system
senti stop               # Stop system
senti restart            # Restart system
senti status             # Show status
senti status --detailed  # Detailed dashboard
senti status --json      # JSON output
senti logs               # Show logs
senti logs --level=error # Error logs only
senti logs --limit=100   # Last 100 entries
senti doctor             # Run diagnostics
senti doctor --quick     # Quick checks
senti help               # Show help
senti --version          # Show version
```

### Python API

```python
from senti_os.core.faza22 import FAZA22Stack

stack = FAZA22Stack()
stack.start()             # Start system
stack.stop()              # Stop system
stack.restart()           # Restart system
stack.get_status()        # Get status dict
stack.is_running()        # Check if running
stack.is_healthy()        # Check if healthy
stack.get_boot_manager()  # Get boot manager
stack.get_logs_manager()  # Get logs manager
stack.get_sentinel()      # Get sentinel
```

---

**End of Implementation Guide**

**Document Version:** 1.0.0
**Last Updated:** 2025-12-02
**Status:** Complete

For technical details, see [FAZA_22_SPEC.md](FAZA_22_SPEC.md)
