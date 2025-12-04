# FAZA 28 - Agent Execution Loop (AEL)

## Overview

FAZA 28 is the Agent Execution Loop for Senti OS, providing an agent-based execution system with intelligent scheduling, event-driven coordination, and shared state management.

**Key Capabilities:**
- Agent lifecycle management (start, tick, error, shutdown)
- Event-driven inter-agent communication
- Intelligent agent scheduling (priority, round-robin, load-aware)
- Thread-safe shared state management
- Main execution loop orchestration
- Integration with FAZA 25, 26, 27.5, and 24

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│            FAZA 28 - Agent Execution Loop                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌─────────────────────────┐     │
│  │ AgentManager │         │    AELController        │     │
│  │  (Registry)  │◄────────│   (Main Loop)           │     │
│  └──────┬───────┘         └──────────┬──────────────┘     │
│         │                             │                     │
│         │  ┌──────────────┐           │                     │
│         └─►│  AgentBase   │           │                     │
│            │   (Base)     │           │                     │
│            └──────────────┘           │                     │
│                                       │                     │
│         ┌──────────────┐              │                     │
│         │  EventBus    │◄─────────────┤                     │
│         │  (Pub/Sub)   │              │                     │
│         └──────────────┘              │                     │
│                                       │                     │
│         ┌──────────────┐              │                     │
│         │  Scheduler   │◄─────────────┤                     │
│         │  (Selection) │              │                     │
│         └──────────────┘              │                     │
│                                       │                     │
│         ┌──────────────┐              │                     │
│         │StateContext  │◄─────────────┘                     │
│         │   (State)    │                                    │
│         └──────────────┘                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. AgentBase
**File:** `agent_base.py`

Base class for all agents. Defines lifecycle hooks:
- `on_start(context)` - Called when agent starts
- `on_tick(context)` - Main agent logic (called each loop iteration)
- `on_event(event, context)` - Event handler
- `on_error(error, context)` - Error handler
- `on_shutdown(context)` - Cleanup handler

#### 2. AgentManager
**File:** `agent_manager.py`

Central registry and lifecycle manager:
- Agent registration and discovery
- Priority-based sorting
- Start/shutdown coordination
- Agent statistics tracking

#### 3. EventBus
**File:** `event_bus.py`

Publish/subscribe event system:
- Event subscription management
- Event publishing and routing
- Event history tracking
- Inter-agent communication

#### 4. Scheduler
**File:** `scheduler.py`

Agent selection and scheduling:
- Priority-based scheduling (higher priority = more frequent)
- Round-robin scheduling (fair distribution)
- Load-aware scheduling (considers execution time)
- Agent throttling

#### 5. StateContext
**File:** `state_context.py`

Thread-safe shared state:
- Key-value state storage
- State change history
- JSON export/import
- File persistence

#### 6. AELController
**File:** `ael_loop.py`

Main execution loop orchestrator:
- Loop lifecycle management
- Agent tick coordination
- Event processing
- Error handling and recovery
- System statistics

## Usage

### Basic Example

```python
from senti_os.core.faza28 import (
    AgentBase,
    get_agent_manager,
    get_ael_controller
)

# Define custom agent
class MonitoringAgent(AgentBase):
    name = "monitoring_agent"
    priority = 8
    enabled = True

    async def on_start(self, context):
        await super().on_start(context)
        print(f"{self.name} started")

    async def on_tick(self, context):
        await super().on_tick(context)

        # Agent logic
        cpu_usage = get_cpu_usage()  # Your monitoring logic
        context.set("cpu_usage", cpu_usage)

        if cpu_usage > 80:
            context.set("alert_high_cpu", True)
            print(f"High CPU usage detected: {cpu_usage}%")

    async def on_shutdown(self, context):
        await super().on_shutdown(context)
        print(f"{self.name} shutdown")

# Register agent
manager = get_agent_manager()
manager.register(MonitoringAgent())

# Start AEL
controller = get_ael_controller(tick_rate=1.0, strategy="priority")
await controller.start()
```

### Event-Driven Agent

```python
from senti_os.core.faza28 import AgentBase, get_event_bus

class ReactiveAgent(AgentBase):
    name = "reactive_agent"
    priority = 7

    async def on_start(self, context):
        await super().on_start(context)

        # Subscribe to events
        event_bus = get_event_bus()
        event_bus.subscribe("alert_high_cpu", self.name, self.handle_cpu_alert)

    def handle_cpu_alert(self, event):
        print(f"Received CPU alert from {event.source}")
        # Take action...

    async def on_tick(self, context):
        await super().on_tick(context)

        # Check state
        if context.get("alert_high_cpu"):
            # Respond to alert
            print("Responding to high CPU alert")
```

### Multiple Agents with Different Priorities

```python
class CriticalAgent(AgentBase):
    name = "critical_agent"
    priority = 10  # Runs every iteration

class NormalAgent(AgentBase):
    name = "normal_agent"
    priority = 5  # Runs every 3 iterations

class BackgroundAgent(AgentBase):
    name = "background_agent"
    priority = 2  # Runs every 5 iterations

# Register all agents
manager = get_agent_manager()
manager.register(CriticalAgent())
manager.register(NormalAgent())
manager.register(BackgroundAgent())
```

## Agent Definition Guide

### Agent Attributes

```python
class MyAgent(AgentBase):
    # Required: Unique agent name
    name: str = "my_agent"

    # Optional: Priority (0-10, higher = more important)
    priority: int = 5

    # Optional: Enable/disable agent
    enabled: bool = True
```

### Lifecycle Hooks

**on_start(context)**
- Called once when agent starts
- Use for initialization, resource setup
- Subscribe to events here

**on_tick(context)**
- Called each loop iteration (if scheduled)
- Main agent logic goes here
- Access/modify shared state
- Emit events to other agents

**on_event(event, context)**
- Called when agent receives subscribed event
- Handle event-driven logic

**on_error(error, context)**
- Called when exception occurs in agent
- Implement error recovery
- Log errors, update metrics

**on_shutdown(context)**
- Called on graceful shutdown
- Cleanup resources
- Save state if needed

### Using State

```python
async def on_tick(self, context):
    # Read state
    counter = context.get("counter", 0)

    # Write state
    context.set("counter", counter + 1)

    # Check existence
    if context.has("alert_active"):
        # Handle alert
        pass

    # Delete state
    context.delete("old_key")
```

### Using Events

```python
async def on_start(self, context):
    # Subscribe to events
    event_bus = get_event_bus()
    event_bus.subscribe("task_completed", self.name, self.handle_task_done)

def handle_task_done(self, event):
    print(f"Task completed: {event.data}")

async def on_tick(self, context):
    # Emit events
    event_bus = get_event_bus()
    event_bus.emit("my_event", self.name, data={"status": "ok"})
```

## Integration with Other FAZA Modules

### FAZA 25 Integration (Task Orchestration)

```python
class TaskSubmitterAgent(AgentBase):
    name = "task_submitter"
    priority = 7

    async def on_tick(self, context):
        await super().on_tick(context)

        # TODO: Import FAZA 25
        # from senti_os.core.faza25 import get_orchestrator

        # Check if work needs to be done
        if context.get("pending_work"):
            # TODO: Submit task to FAZA 25
            # orchestrator = get_orchestrator()
            # await orchestrator.submit_task(task)

            context.delete("pending_work")
```

### FAZA 26 Integration (Action Layer)

```python
class ActionExecutorAgent(AgentBase):
    name = "action_executor"
    priority = 8

    async def on_tick(self, context):
        await super().on_tick(context)

        # TODO: Import FAZA 26
        # from senti_os.core.faza26 import get_action_layer

        # Check for user commands
        command = context.get("user_command")
        if command:
            # TODO: Execute via FAZA 26
            # action_layer = get_action_layer()
            # await action_layer.execute_command(command)

            context.delete("user_command")
```

### FAZA 27.5 Integration (Execution Optimizer)

```python
class OptimizerAgent(AgentBase):
    name = "optimizer"
    priority = 6

    async def on_tick(self, context):
        await super().on_tick(context)

        # TODO: Import FAZA 27.5
        # from senti_os.core.faza27_5 import get_optimizer

        # Get task graph from state
        task_graph = context.get("task_graph")
        if task_graph:
            # TODO: Optimize graph
            # optimizer = get_optimizer()
            # optimized_graph, report = optimizer.optimize(task_graph)

            # Store optimized graph and report
            context.set("optimized_graph", "optimized_graph")
            context.set("optimization_report", "report")
```

### FAZA 24 Integration (Web Dashboard)

```python
class TelemetryAgent(AgentBase):
    name = "telemetry"
    priority = 5

    async def on_tick(self, context):
        await super().on_tick(context)

        # Collect system metrics
        stats = {
            "cpu_usage": context.get("cpu_usage", 0),
            "memory_usage": context.get("memory_usage", 0),
            "active_agents": len(get_agent_manager().list_agents(enabled_only=True))
        }

        # TODO: Push to FAZA 24 dashboard
        # from senti_os.core.faza24 import push_metrics
        # push_metrics("ael_telemetry", stats)
```

## API Reference

### AgentBase
```python
class AgentBase:
    name: str
    priority: int = 5
    enabled: bool = True

    async def on_start(context) -> None
    async def on_tick(context) -> None
    async def on_event(event, context) -> None
    async def on_error(error, context) -> None
    async def on_shutdown(context) -> None
    def get_stats() -> Dict[str, Any]
```

### AgentManager
```python
manager = get_agent_manager()
manager.register(agent: AgentBase)
manager.unregister(agent_name: str)
manager.get_agent(agent_name: str) -> Optional[AgentBase]
manager.list_agents(enabled_only: bool = False) -> List[AgentBase]
manager.get_agents_by_priority(enabled_only: bool = True) -> List[AgentBase]
await manager.start_all(context)
await manager.shutdown_all(context)
```

### EventBus
```python
bus = get_event_bus()
bus.subscribe(event_type: str, subscriber_name: str, callback: Callable)
bus.unsubscribe(event_type: str, subscriber_name: str)
bus.publish(event: Event)
bus.emit(event_type: str, source: str, data: Any = None)
bus.get_event_history(event_type: Optional[str] = None) -> List[Event]
```

### StateContext
```python
context = get_state_context()
context.get(key: str, default: Any = None) -> Any
context.set(key: str, value: Any)
context.delete(key: str) -> bool
context.has(key: str) -> bool
context.get_all() -> Dict[str, Any]
context.update(updates: Dict[str, Any])
context.clear()
context.get_history(key: Optional[str] = None) -> List[Dict]
```

### AELController
```python
controller = get_ael_controller(tick_rate: float = 1.0, strategy: str = "priority")
await controller.start()
await controller.stop()
controller.get_stats() -> Dict[str, Any]
```

## Testing

### Run Test Suite

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 tests/test_faza28.py
```

### Test Coverage

**39 comprehensive tests:**
- AgentBase: 4 tests
- AgentManager: 9 tests
- EventBus: 7 tests
- Scheduler: 5 tests
- StateContext: 8 tests
- AELController: 4 tests

All tests passing ✓

## Configuration

### Tick Rate
Control loop iteration speed:
```python
controller = get_ael_controller(tick_rate=1.0)  # 1 iteration per second
controller = get_ael_controller(tick_rate=0.5)  # 2 iterations per second
```

### Scheduling Strategy
Choose agent selection strategy:
```python
# Priority-based (default): Higher priority agents run more often
controller = get_ael_controller(strategy="priority")

# Round-robin: Fair scheduling across all agents
controller = get_ael_controller(strategy="round_robin")

# Load-aware: Consider execution time and load
controller = get_ael_controller(strategy="load_aware")
```

## Best Practices

1. **Agent Design**
   - Keep agents focused on single responsibility
   - Use priority wisely (10 = critical, 5 = normal, 1 = background)
   - Avoid blocking operations in on_tick()

2. **State Management**
   - Use clear, namespaced state keys (e.g., "agent_name:key")
   - Clean up state in on_shutdown()
   - Document state keys used by each agent

3. **Event Usage**
   - Use events for inter-agent communication
   - Subscribe in on_start(), unsubscribe in on_shutdown()
   - Keep event payloads lightweight

4. **Error Handling**
   - Implement robust on_error() handlers
   - Log errors with context
   - Don't let one agent crash the entire system

5. **Performance**
   - Monitor agent execution time
   - Adjust priorities based on actual load
   - Use appropriate tick rate for your use case

## Version History

- **v1.0.0** (2024-12-04): Initial implementation
  - AgentBase with lifecycle hooks
  - AgentManager with registry and lifecycle
  - EventBus with pub/sub system
  - Scheduler with 3 strategies
  - StateContext with thread-safe state
  - AELController with main loop
  - 39 comprehensive tests

## License

Part of Senti System - Proprietary

---

**FAZA 28 - Agent Execution Loop**
*Intelligent agent orchestration for autonomous system operation*
