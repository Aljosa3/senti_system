"""
FAZA 30 – Autorepair Engine

Continuous self-healing loop with throttling and safety mechanisms.

Provides:
- Continuous fault monitoring
- Automatic repair triggering
- Healing throttle (prevent repair storms)
- Safety mechanisms
- Configurable healing policies

Architecture:
    AutorepairConfig - Configuration for autorepair
    AutorepairEngine - Main continuous healing loop

Usage:
    from senti_os.core.faza30.autorepair_engine import AutorepairEngine

    engine = AutorepairEngine(healing_pipeline, integration_layer)
    await engine.start()
    # ... system runs with automatic healing
    await engine.stop()
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import deque


class AutorepairMode(Enum):
    """Autorepair operation mode."""
    AGGRESSIVE = "aggressive"       # Repair all faults immediately
    BALANCED = "balanced"           # Normal operation
    CONSERVATIVE = "conservative"   # Only repair critical faults
    DISABLED = "disabled"           # No automatic repairs


class ThrottleState(Enum):
    """Healing throttle state."""
    NORMAL = "normal"               # Normal operation
    THROTTLED = "throttled"         # Healing throttled
    BLOCKED = "blocked"             # Healing blocked (too many repairs)


@dataclass
class AutorepairConfig:
    """
    Configuration for autorepair engine.

    Attributes:
        mode: Operation mode
        interval_seconds: Monitoring interval
        max_repairs_per_minute: Maximum repairs per minute
        max_repairs_per_hour: Maximum repairs per hour
        cooldown_seconds: Cooldown after repair
        min_health_for_repair: Minimum health to attempt repair
        enable_snapshots: Enable pre-repair snapshots
        enable_rollback: Enable automatic rollback
    """
    mode: AutorepairMode = AutorepairMode.BALANCED
    interval_seconds: float = 5.0
    max_repairs_per_minute: int = 10
    max_repairs_per_hour: int = 50
    cooldown_seconds: float = 3.0
    min_health_for_repair: float = 20.0
    enable_snapshots: bool = True
    enable_rollback: bool = True


class AutorepairEngine:
    """
    Continuous self-healing engine with throttling.

    Features:
    - Continuous fault monitoring
    - Automatic repair execution
    - Healing throttle (prevent repair storms)
    - Cooldown periods
    - Safety mechanisms
    - Configurable policies
    - Event notifications

    Runs as async background task, continuously monitoring and healing.
    """

    def __init__(
        self,
        healing_pipeline: Any,
        integration_layer: Optional[Any] = None,
        event_hooks: Optional[Any] = None,
        config: Optional[AutorepairConfig] = None
    ):
        """
        Initialize autorepair engine.

        Args:
            healing_pipeline: HealingPipeline instance
            integration_layer: Optional IntegrationLayer
            event_hooks: Optional EventHooks
            config: Autorepair configuration
        """
        self.healing_pipeline = healing_pipeline
        self.integration_layer = integration_layer
        self.event_hooks = event_hooks
        self.config = config or AutorepairConfig()

        self._running = False
        self._task: Optional[asyncio.Task] = None

        # Throttle tracking
        self._repair_timestamps_minute: deque = deque(maxlen=self.config.max_repairs_per_minute)
        self._repair_timestamps_hour: deque = deque(maxlen=self.config.max_repairs_per_hour)
        self._last_repair_time: Optional[datetime] = None
        self._throttle_state = ThrottleState.NORMAL

        # Statistics
        self._stats = {
            "total_cycles": 0,
            "healing_cycles_triggered": 0,
            "repairs_attempted": 0,
            "repairs_successful": 0,
            "throttled_count": 0,
            "blocked_count": 0,
            "avg_cycle_duration": 0.0,
            "uptime_seconds": 0.0
        }

        self._start_time: Optional[datetime] = None

    async def start(self) -> None:
        """Start continuous autorepair loop."""
        if self._running:
            return

        self._running = True
        self._start_time = datetime.now()
        self._task = asyncio.create_task(self._autorepair_loop())

        if self.event_hooks:
            self.event_hooks.publish_event(
                "autorepair_started",
                {"mode": self.config.mode.value, "interval": self.config.interval_seconds}
            )

    async def stop(self) -> None:
        """Stop continuous autorepair loop."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self.event_hooks:
            self.event_hooks.publish_event(
                "autorepair_stopped",
                {"uptime_seconds": self._stats["uptime_seconds"]}
            )

    async def _autorepair_loop(self) -> None:
        """Main continuous autorepair loop."""
        while self._running:
            cycle_start = datetime.now()

            try:
                # Update uptime
                if self._start_time:
                    self._stats["uptime_seconds"] = (datetime.now() - self._start_time).total_seconds()

                # Increment cycle count
                self._stats["total_cycles"] += 1

                # Check if we should run healing
                should_heal = self._should_trigger_healing()

                if should_heal:
                    await self._execute_healing_cycle()

                # Wait for next interval
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                self._update_avg_cycle_duration(cycle_duration)

                sleep_time = max(0.1, self.config.interval_seconds - cycle_duration)
                await asyncio.sleep(sleep_time)

            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                if self.event_hooks:
                    self.event_hooks.publish_event(
                        "autorepair_error",
                        {"error": str(e)}
                    )
                await asyncio.sleep(self.config.interval_seconds)

    def _should_trigger_healing(self) -> bool:
        """Determine if healing should be triggered."""
        # Check if disabled
        if self.config.mode == AutorepairMode.DISABLED:
            return False

        # Check cooldown
        if self._last_repair_time:
            time_since_last = (datetime.now() - self._last_repair_time).total_seconds()
            if time_since_last < self.config.cooldown_seconds:
                return False

        # Check throttle state
        throttle_state = self._check_throttle()
        self._throttle_state = throttle_state

        if throttle_state == ThrottleState.BLOCKED:
            self._stats["blocked_count"] += 1
            return False

        if throttle_state == ThrottleState.THROTTLED:
            self._stats["throttled_count"] += 1
            # In throttled state, only heal critical faults
            return self._has_critical_faults()

        return True

    def _check_throttle(self) -> ThrottleState:
        """Check if healing is throttled."""
        now = datetime.now()

        # Clean up old timestamps
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        self._repair_timestamps_minute = deque(
            [t for t in self._repair_timestamps_minute if t > minute_ago],
            maxlen=self.config.max_repairs_per_minute
        )

        self._repair_timestamps_hour = deque(
            [t for t in self._repair_timestamps_hour if t > hour_ago],
            maxlen=self.config.max_repairs_per_hour
        )

        # Check limits
        repairs_last_minute = len(self._repair_timestamps_minute)
        repairs_last_hour = len(self._repair_timestamps_hour)

        if repairs_last_minute >= self.config.max_repairs_per_minute:
            return ThrottleState.BLOCKED

        if repairs_last_hour >= self.config.max_repairs_per_hour * 0.8:
            return ThrottleState.THROTTLED

        return ThrottleState.NORMAL

    def _has_critical_faults(self) -> bool:
        """Check if there are critical faults that need immediate attention."""
        # Get metrics from integration layer
        if not self.integration_layer:
            return False

        # Check for critical conditions
        faza29_metrics = self.integration_layer.get_faza29_metrics() if hasattr(self.integration_layer, 'get_faza29_metrics') else {}

        # Check governance risk score
        risk_score = faza29_metrics.get('risk_score', 0)
        if risk_score > 70:  # Critical risk
            return True

        # Check takeover state
        if faza29_metrics.get('takeover_active', False):
            return True

        return False

    async def _execute_healing_cycle(self) -> None:
        """Execute a healing cycle."""
        try:
            self._stats["healing_cycles_triggered"] += 1

            # Get metrics from integration layer
            metrics = self._gather_metrics()

            # Execute healing pipeline
            result = self.healing_pipeline.execute_healing_cycle(**metrics)

            # Track repair timestamp
            now = datetime.now()
            self._repair_timestamps_minute.append(now)
            self._repair_timestamps_hour.append(now)
            self._last_repair_time = now

            # Update statistics
            self._stats["repairs_attempted"] += result.faults_detected

            if result.outcome.value == "success":
                self._stats["repairs_successful"] += result.faults_repaired

            # Publish event
            if self.event_hooks:
                self.event_hooks.publish_event(
                    "healing_cycle_completed",
                    {
                        "cycle_id": result.cycle_id,
                        "outcome": result.outcome.value,
                        "faults_detected": result.faults_detected,
                        "faults_repaired": result.faults_repaired,
                        "health_improvement": result.health_improvement
                    }
                )

        except Exception as e:
            if self.event_hooks:
                self.event_hooks.publish_event(
                    "healing_cycle_failed",
                    {"error": str(e)}
                )

    def _gather_metrics(self) -> Dict[str, Any]:
        """Gather metrics from all FAZA layers."""
        metrics = {
            "faza25_metrics": None,
            "faza27_metrics": None,
            "faza28_metrics": None,
            "faza28_5_metrics": None,
            "faza29_metrics": None
        }

        if self.integration_layer:
            # Try to get metrics from each layer
            if hasattr(self.integration_layer, 'get_faza25_metrics'):
                metrics["faza25_metrics"] = self.integration_layer.get_faza25_metrics()

            if hasattr(self.integration_layer, 'get_faza27_metrics'):
                metrics["faza27_metrics"] = self.integration_layer.get_faza27_metrics()

            if hasattr(self.integration_layer, 'get_faza28_metrics'):
                metrics["faza28_metrics"] = self.integration_layer.get_faza28_metrics()

            if hasattr(self.integration_layer, 'get_faza28_5_metrics'):
                metrics["faza28_5_metrics"] = self.integration_layer.get_faza28_5_metrics()

            if hasattr(self.integration_layer, 'get_faza29_metrics'):
                metrics["faza29_metrics"] = self.integration_layer.get_faza29_metrics()

        return metrics

    def _update_avg_cycle_duration(self, duration: float) -> None:
        """Update average cycle duration."""
        total_cycles = self._stats["total_cycles"]
        if total_cycles == 0:
            return

        current_avg = self._stats["avg_cycle_duration"]
        new_avg = (current_avg * (total_cycles - 1) + duration) / total_cycles
        self._stats["avg_cycle_duration"] = new_avg

    def set_mode(self, mode: AutorepairMode) -> None:
        """
        Change autorepair mode.

        Args:
            mode: New operation mode
        """
        old_mode = self.config.mode
        self.config.mode = mode

        if self.event_hooks:
            self.event_hooks.publish_event(
                "autorepair_mode_changed",
                {"old_mode": old_mode.value, "new_mode": mode.value}
            )

    def set_interval(self, interval_seconds: float) -> None:
        """
        Change monitoring interval.

        Args:
            interval_seconds: New interval in seconds
        """
        self.config.interval_seconds = max(0.1, interval_seconds)

    def force_healing_cycle(self) -> None:
        """
        Force an immediate healing cycle (bypasses throttle and cooldown).

        Use with caution - for emergency situations only.
        """
        # Reset throttle temporarily
        self._last_repair_time = None

        if self.event_hooks:
            self.event_hooks.publish_event(
                "forced_healing_cycle",
                {"timestamp": datetime.now().isoformat()}
            )

    def get_throttle_state(self) -> ThrottleState:
        """Get current throttle state."""
        return self._throttle_state

    def get_statistics(self) -> Dict[str, Any]:
        """Get autorepair engine statistics."""
        repairs_last_minute = len(self._repair_timestamps_minute)
        repairs_last_hour = len(self._repair_timestamps_hour)

        success_rate = 0.0
        if self._stats["repairs_attempted"] > 0:
            success_rate = self._stats["repairs_successful"] / self._stats["repairs_attempted"]

        return {
            **self._stats,
            "running": self._running,
            "mode": self.config.mode.value,
            "throttle_state": self._throttle_state.value,
            "repairs_last_minute": repairs_last_minute,
            "repairs_last_hour": repairs_last_hour,
            "success_rate": success_rate,
            "last_repair_time": self._last_repair_time.isoformat() if self._last_repair_time else None
        }

    def get_config(self) -> AutorepairConfig:
        """Get current configuration."""
        return self.config

    def update_config(self, **kwargs) -> None:
        """
        Update configuration parameters.

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        if self.event_hooks:
            self.event_hooks.publish_event(
                "autorepair_config_updated",
                {"updated_params": list(kwargs.keys())}
            )

    def is_running(self) -> bool:
        """Check if autorepair engine is running."""
        return self._running

    def get_uptime(self) -> float:
        """Get uptime in seconds."""
        return self._stats["uptime_seconds"]


def create_autorepair_engine(
    healing_pipeline: Any,
    integration_layer: Optional[Any] = None,
    event_hooks: Optional[Any] = None,
    config: Optional[AutorepairConfig] = None
) -> AutorepairEngine:
    """
    Factory function to create AutorepairEngine.

    Args:
        healing_pipeline: HealingPipeline instance
        integration_layer: Optional IntegrationLayer
        event_hooks: Optional EventHooks
        config: Optional configuration

    Returns:
        Initialized AutorepairEngine instance
    """
    return AutorepairEngine(
        healing_pipeline=healing_pipeline,
        integration_layer=integration_layer,
        event_hooks=event_hooks,
        config=config
    )


# Convenience function for quick start
async def start_autorepair(
    healing_pipeline: Any,
    integration_layer: Optional[Any] = None,
    mode: str = "balanced",
    interval: float = 5.0
) -> AutorepairEngine:
    """
    Quick start autorepair with common settings.

    Args:
        healing_pipeline: HealingPipeline instance
        integration_layer: Optional IntegrationLayer
        mode: Operation mode (aggressive/balanced/conservative)
        interval: Monitoring interval in seconds

    Returns:
        Started AutorepairEngine instance
    """
    config = AutorepairConfig(
        mode=AutorepairMode(mode),
        interval_seconds=interval
    )

    engine = create_autorepair_engine(
        healing_pipeline=healing_pipeline,
        integration_layer=integration_layer,
        config=config
    )

    await engine.start()
    return engine
