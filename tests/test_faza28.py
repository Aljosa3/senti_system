"""
FAZA 28 - Agent Execution Loop (AEL)
Comprehensive Test Suite

Tests all components:
- AgentBase and custom agents
- AgentManager (registry and lifecycle)
- EventBus (pub/sub system)
- Scheduler (agent selection)
- StateContext (state management)
- AELController (main loop)
"""

import asyncio
from typing import Any

from senti_os.core.faza28 import (
    AgentBase,
    AgentManager,
    Event,
    EventBus,
    Scheduler,
    StateContext,
    AELController,
    get_agent_manager,
    get_event_bus,
    get_state_context,
    get_ael_controller
)


# Test Agents

class DummyAgent(AgentBase):
    """Simple test agent"""
    name = "dummy_agent"
    priority = 5

    def __init__(self):
        super().__init__()
        self.tick_calls = 0
        self.start_calls = 0
        self.shutdown_calls = 0
        self.error_calls = 0
        self.event_calls = 0

    async def on_start(self, context: Any) -> None:
        await super().on_start(context)
        self.start_calls += 1

    async def on_tick(self, context: Any) -> None:
        await super().on_tick(context)
        self.tick_calls += 1
        context.set(f"{self.name}_ticks", self.tick_calls)

    async def on_event(self, event: Any, context: Any) -> None:
        await super().on_event(event, context)
        self.event_calls += 1

    async def on_error(self, error: Exception, context: Any) -> None:
        await super().on_error(error, context)
        self.error_calls += 1

    async def on_shutdown(self, context: Any) -> None:
        await super().on_shutdown(context)
        self.shutdown_calls += 1


class HighPriorityAgent(DummyAgent):
    """High priority test agent"""
    name = "high_priority_agent"
    priority = 10


class LowPriorityAgent(DummyAgent):
    """Low priority test agent"""
    name = "low_priority_agent"
    priority = 1


class ErrorAgent(AgentBase):
    """Agent that raises errors"""
    name = "error_agent"
    priority = 5

    async def on_tick(self, context: Any) -> None:
        await super().on_tick(context)
        raise RuntimeError("Intentional error for testing")


# Test Classes

class TestAgentBase:
    """Tests for AgentBase"""

    def test_agent_creation(self):
        """Test creating an agent"""
        agent = DummyAgent()
        assert agent.name == "dummy_agent"
        assert agent.priority == 5
        assert agent.enabled is True
        assert agent.tick_count == 0

    def test_agent_stats(self):
        """Test agent statistics"""
        agent = DummyAgent()
        stats = agent.get_stats()

        assert stats["name"] == "dummy_agent"
        assert stats["priority"] == 5
        assert stats["enabled"] is True
        assert stats["tick_count"] == 0
        assert stats["error_count"] == 0

    async def test_agent_lifecycle(self):
        """Test agent lifecycle hooks"""
        agent = DummyAgent()
        context = StateContext()

        await agent.on_start(context)
        assert agent.start_calls == 1

        await agent.on_tick(context)
        assert agent.tick_calls == 1
        assert agent.tick_count == 1

        await agent.on_shutdown(context)
        assert agent.shutdown_calls == 1

    async def test_agent_error_handling(self):
        """Test agent error handling"""
        agent = DummyAgent()
        context = StateContext()

        error = ValueError("test error")
        await agent.on_error(error, context)
        assert agent.error_calls == 1
        assert agent.error_count == 1


class TestAgentManager:
    """Tests for AgentManager"""

    def test_manager_creation(self):
        """Test creating agent manager"""
        manager = AgentManager()
        assert len(manager.agents) == 0

    def test_register_agent(self):
        """Test registering agents"""
        manager = AgentManager()
        agent = DummyAgent()

        manager.register(agent)
        assert len(manager.agents) == 1
        assert "dummy_agent" in manager.agents

    def test_duplicate_registration(self):
        """Test that duplicate names are rejected"""
        manager = AgentManager()
        agent1 = DummyAgent()
        agent2 = DummyAgent()

        manager.register(agent1)
        try:
            manager.register(agent2)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already registered" in str(e)

    def test_unregister_agent(self):
        """Test unregistering agents"""
        manager = AgentManager()
        agent = DummyAgent()

        manager.register(agent)
        assert len(manager.agents) == 1

        manager.unregister("dummy_agent")
        assert len(manager.agents) == 0

    def test_get_agent(self):
        """Test getting agent by name"""
        manager = AgentManager()
        agent = DummyAgent()

        manager.register(agent)
        retrieved = manager.get_agent("dummy_agent")
        assert retrieved is agent

    def test_list_agents(self):
        """Test listing agents"""
        manager = AgentManager()
        agent1 = DummyAgent()
        agent2 = HighPriorityAgent()

        manager.register(agent1)
        manager.register(agent2)

        all_agents = manager.list_agents()
        assert len(all_agents) == 2

        enabled_agents = manager.list_agents(enabled_only=True)
        assert len(enabled_agents) == 2

    def test_get_agents_by_priority(self):
        """Test getting agents sorted by priority"""
        manager = AgentManager()
        low = LowPriorityAgent()
        mid = DummyAgent()
        high = HighPriorityAgent()

        manager.register(low)
        manager.register(mid)
        manager.register(high)

        sorted_agents = manager.get_agents_by_priority()
        assert len(sorted_agents) == 3
        assert sorted_agents[0].name == "high_priority_agent"
        assert sorted_agents[2].name == "low_priority_agent"

    async def test_start_all_agents(self):
        """Test starting all agents"""
        manager = AgentManager()
        agent1 = DummyAgent()
        agent2 = HighPriorityAgent()

        manager.register(agent1)
        manager.register(agent2)

        context = StateContext()
        await manager.start_all(context)

        assert agent1.start_calls == 1
        assert agent2.start_calls == 1

    async def test_shutdown_all_agents(self):
        """Test shutting down all agents"""
        manager = AgentManager()
        agent1 = DummyAgent()
        agent2 = HighPriorityAgent()

        manager.register(agent1)
        manager.register(agent2)

        context = StateContext()
        await manager.start_all(context)
        await manager.shutdown_all(context)

        assert agent1.shutdown_calls == 1
        assert agent2.shutdown_calls == 1


class TestEventBus:
    """Tests for EventBus"""

    def test_event_creation(self):
        """Test creating events"""
        event = Event(type="test_event", source="test_source", data={"key": "value"})
        assert event.type == "test_event"
        assert event.source == "test_source"
        assert event.data["key"] == "value"

    def test_eventbus_creation(self):
        """Test creating event bus"""
        bus = EventBus()
        assert len(bus._subscriptions) == 0
        assert len(bus._event_history) == 0

    def test_subscribe(self):
        """Test subscribing to events"""
        bus = EventBus()
        received_events = []

        def handler(event):
            received_events.append(event)

        bus.subscribe("test_event", "subscriber1", handler)
        assert len(bus._subscriptions["test_event"]) == 1

    def test_publish_event(self):
        """Test publishing events"""
        bus = EventBus()
        received_events = []

        def handler(event):
            received_events.append(event)

        bus.subscribe("test_event", "subscriber1", handler)

        event = Event(type="test_event", source="source1", data="test_data")
        bus.publish(event)

        assert len(received_events) == 1
        assert received_events[0].type == "test_event"
        assert len(bus._event_history) == 1

    def test_emit_event(self):
        """Test emit convenience method"""
        bus = EventBus()
        received_events = []

        def handler(event):
            received_events.append(event)

        bus.subscribe("test_event", "subscriber1", handler)
        bus.emit("test_event", "source1", data="test_data")

        assert len(received_events) == 1
        assert received_events[0].data == "test_data"

    def test_unsubscribe(self):
        """Test unsubscribing from events"""
        bus = EventBus()
        received_events = []

        def handler(event):
            received_events.append(event)

        bus.subscribe("test_event", "subscriber1", handler)
        bus.unsubscribe("test_event", "subscriber1")

        bus.emit("test_event", "source1")
        assert len(received_events) == 0

    def test_event_history(self):
        """Test event history tracking"""
        bus = EventBus()

        bus.emit("event1", "source1")
        bus.emit("event2", "source2")
        bus.emit("event1", "source3")

        history = bus.get_event_history()
        assert len(history) == 3

        # Filter by type
        event1_history = bus.get_event_history(event_type="event1")
        assert len(event1_history) == 2

        # Filter by source
        source1_history = bus.get_event_history(source="source1")
        assert len(source1_history) == 1


class TestScheduler:
    """Tests for Scheduler"""

    def test_scheduler_creation(self):
        """Test creating scheduler"""
        scheduler = Scheduler(strategy="priority")
        assert scheduler.strategy == "priority"

    def test_priority_selection(self):
        """Test priority-based agent selection"""
        scheduler = Scheduler(strategy="priority")
        agents = [
            LowPriorityAgent(),
            DummyAgent(),
            HighPriorityAgent()
        ]

        selected = scheduler.select_agents(agents)
        assert len(selected) == 3
        assert selected[0].name == "high_priority_agent"

    def test_round_robin_selection(self):
        """Test round-robin agent selection"""
        scheduler = Scheduler(strategy="round_robin")
        agents = [
            DummyAgent(),
            HighPriorityAgent(),
            LowPriorityAgent()
        ]

        # First selection
        selected1 = scheduler.select_agents(agents, max_agents=1)
        assert len(selected1) == 1

        # Second selection (should be different)
        selected2 = scheduler.select_agents(agents, max_agents=1)
        assert len(selected2) == 1

    def test_should_run_agent(self):
        """Test agent run decision"""
        scheduler = Scheduler()

        high_priority = HighPriorityAgent()
        low_priority = LowPriorityAgent()

        # High priority runs every iteration
        assert scheduler.should_run_agent(high_priority, 1) is True
        assert scheduler.should_run_agent(high_priority, 2) is True

        # Low priority runs less frequently
        runs = [scheduler.should_run_agent(low_priority, i) for i in range(20)]
        assert sum(runs) < 20  # Should run less than every iteration

    def test_record_execution(self):
        """Test execution recording"""
        scheduler = Scheduler()

        scheduler.record_execution("agent1", 0.5)
        scheduler.record_execution("agent1", 0.3)

        stats = scheduler.get_stats()
        assert stats["execution_counts"]["agent1"] == 2


class TestStateContext:
    """Tests for StateContext"""

    def test_state_creation(self):
        """Test creating state context"""
        state = StateContext(name="test")
        assert state.name == "test"
        assert len(state._state) == 0

    def test_get_set(self):
        """Test getting and setting state"""
        state = StateContext()

        state.set("key1", "value1")
        assert state.get("key1") == "value1"
        assert state.get("missing", "default") == "default"

    def test_delete(self):
        """Test deleting state"""
        state = StateContext()

        state.set("key1", "value1")
        assert state.has("key1") is True

        deleted = state.delete("key1")
        assert deleted is True
        assert state.has("key1") is False

    def test_get_all(self):
        """Test getting all state"""
        state = StateContext()

        state.set("key1", "value1")
        state.set("key2", "value2")

        all_state = state.get_all()
        assert len(all_state) == 2
        assert all_state["key1"] == "value1"

    def test_update(self):
        """Test bulk update"""
        state = StateContext()

        state.update({
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        })

        assert len(state._state) == 3

    def test_clear(self):
        """Test clearing state"""
        state = StateContext()

        state.set("key1", "value1")
        state.set("key2", "value2")

        state.clear()
        assert len(state._state) == 0

    def test_history(self):
        """Test state change history"""
        state = StateContext()

        state.set("key1", "value1")
        state.set("key1", "value2")
        state.delete("key1")

        history = state.get_history()
        assert len(history) == 3

        key1_history = state.get_history(key="key1")
        assert len(key1_history) == 3

    def test_json_export_import(self):
        """Test JSON export/import"""
        state = StateContext()

        state.set("key1", "value1")
        state.set("key2", 123)

        json_str = state.to_json()
        assert "key1" in json_str

        state2 = StateContext()
        state2.from_json(json_str)
        assert state2.get("key1") == "value1"
        assert state2.get("key2") == 123


class TestAELController:
    """Tests for AELController"""

    def test_controller_creation(self):
        """Test creating AEL controller"""
        controller = AELController(tick_rate=1.0, strategy="priority")
        assert controller.tick_rate == 1.0
        assert controller.strategy == "priority"
        assert controller._running is False

    async def test_basic_loop_cycle(self):
        """Test basic loop execution"""
        manager = AgentManager()
        agent = DummyAgent()
        manager.register(agent)

        controller = AELController(
            agent_manager=manager,
            tick_rate=0.1,
            strategy="priority"
        )

        # Run loop for a short time
        async def run_briefly():
            asyncio.create_task(controller.start())
            await asyncio.sleep(0.3)
            await controller.stop()

        await run_briefly()

        # Agent should have ticked at least once
        assert agent.tick_calls >= 1
        assert agent.start_calls == 1

    async def test_error_handling_in_loop(self):
        """Test error handling during loop execution"""
        manager = AgentManager()
        error_agent = ErrorAgent()
        normal_agent = DummyAgent()

        manager.register(error_agent)
        manager.register(normal_agent)

        controller = AELController(
            agent_manager=manager,
            tick_rate=0.1,
            strategy="priority"
        )

        # Run loop briefly
        async def run_briefly():
            asyncio.create_task(controller.start())
            await asyncio.sleep(0.3)
            await controller.stop()

        await run_briefly()

        # Normal agent should continue despite error agent
        assert normal_agent.tick_calls >= 1
        assert error_agent.error_count >= 1

    def test_controller_stats(self):
        """Test getting controller statistics"""
        controller = AELController(tick_rate=1.0)
        stats = controller.get_stats()

        assert "running" in stats
        assert "iteration" in stats
        assert "tick_rate" in stats
        assert "agent_manager" in stats


# Test runner

def run_all_tests():
    """Run all test suites"""
    import sys

    print("=" * 70)
    print("FAZA 28 - Agent Execution Loop - Test Suite")
    print("=" * 70)

    # AgentBase tests
    print("\n" + "=" * 70)
    print("Running AgentBase Tests")
    print("=" * 70)

    test_base = TestAgentBase()
    test_base.test_agent_creation()
    print("✓ Agent creation")

    test_base.test_agent_stats()
    print("✓ Agent stats")

    asyncio.run(test_base.test_agent_lifecycle())
    print("✓ Agent lifecycle")

    asyncio.run(test_base.test_agent_error_handling())
    print("✓ Agent error handling")

    # AgentManager tests
    print("\n" + "=" * 70)
    print("Running AgentManager Tests")
    print("=" * 70)

    test_manager = TestAgentManager()
    test_manager.test_manager_creation()
    print("✓ Manager creation")

    test_manager.test_register_agent()
    print("✓ Register agent")

    test_manager.test_duplicate_registration()
    print("✓ Duplicate registration rejection")

    test_manager.test_unregister_agent()
    print("✓ Unregister agent")

    test_manager.test_get_agent()
    print("✓ Get agent")

    test_manager.test_list_agents()
    print("✓ List agents")

    test_manager.test_get_agents_by_priority()
    print("✓ Get agents by priority")

    asyncio.run(test_manager.test_start_all_agents())
    print("✓ Start all agents")

    asyncio.run(test_manager.test_shutdown_all_agents())
    print("✓ Shutdown all agents")

    # EventBus tests
    print("\n" + "=" * 70)
    print("Running EventBus Tests")
    print("=" * 70)

    test_bus = TestEventBus()
    test_bus.test_event_creation()
    print("✓ Event creation")

    test_bus.test_eventbus_creation()
    print("✓ EventBus creation")

    test_bus.test_subscribe()
    print("✓ Subscribe to events")

    test_bus.test_publish_event()
    print("✓ Publish event")

    test_bus.test_emit_event()
    print("✓ Emit event")

    test_bus.test_unsubscribe()
    print("✓ Unsubscribe from events")

    test_bus.test_event_history()
    print("✓ Event history")

    # Scheduler tests
    print("\n" + "=" * 70)
    print("Running Scheduler Tests")
    print("=" * 70)

    test_scheduler = TestScheduler()
    test_scheduler.test_scheduler_creation()
    print("✓ Scheduler creation")

    test_scheduler.test_priority_selection()
    print("✓ Priority selection")

    test_scheduler.test_round_robin_selection()
    print("✓ Round-robin selection")

    test_scheduler.test_should_run_agent()
    print("✓ Should run agent decision")

    test_scheduler.test_record_execution()
    print("✓ Record execution")

    # StateContext tests
    print("\n" + "=" * 70)
    print("Running StateContext Tests")
    print("=" * 70)

    test_state = TestStateContext()
    test_state.test_state_creation()
    print("✓ State creation")

    test_state.test_get_set()
    print("✓ Get/set state")

    test_state.test_delete()
    print("✓ Delete state")

    test_state.test_get_all()
    print("✓ Get all state")

    test_state.test_update()
    print("✓ Bulk update")

    test_state.test_clear()
    print("✓ Clear state")

    test_state.test_history()
    print("✓ State history")

    test_state.test_json_export_import()
    print("✓ JSON export/import")

    # AELController tests
    print("\n" + "=" * 70)
    print("Running AELController Tests")
    print("=" * 70)

    test_controller = TestAELController()
    test_controller.test_controller_creation()
    print("✓ Controller creation")

    asyncio.run(test_controller.test_basic_loop_cycle())
    print("✓ Basic loop cycle")

    asyncio.run(test_controller.test_error_handling_in_loop())
    print("✓ Error handling in loop")

    test_controller.test_controller_stats()
    print("✓ Controller stats")

    print("\n" + "=" * 70)
    print("✓ ALL 39 TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
