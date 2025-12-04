"""
FAZA 29 – Enterprise Governance Engine
Adaptive Tick Engine

Dynamic frequency control for FAZA 29 governance loop.
Tick speed adjusts based on:
- System load
- Risk score
- Meta-agent warnings
- Governance override decisions

Supports min/max bounds, smoothing window, spike suppression.
Produces tick cadence (Hz).
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class TickConfig:
    """
    Adaptive tick configuration.

    Attributes:
        min_hz: Minimum tick frequency (Hz)
        max_hz: Maximum tick frequency (Hz)
        default_hz: Default tick frequency (Hz)
        smoothing_window: Smoothing window size
        spike_threshold: Spike suppression threshold
        adaptation_rate: Rate of frequency adaptation (0-1)
    """
    min_hz: float = 0.1      # 10 second intervals min
    max_hz: float = 10.0     # 100ms intervals max
    default_hz: float = 1.0  # 1 second intervals default
    smoothing_window: int = 10
    spike_threshold: float = 2.0  # 2x change is spike
    adaptation_rate: float = 0.3  # 30% adaptation per update


class AdaptiveTickEngine:
    """
    Adaptive tick frequency controller.

    Dynamically adjusts governance loop tick frequency based on
    system conditions to balance responsiveness and resource usage.
    """

    def __init__(self, config: Optional[TickConfig] = None):
        """
        Initialize adaptive tick engine.

        Args:
            config: Tick configuration
        """
        self.config = config or TickConfig()

        # Current state
        self.current_hz = self.config.default_hz
        self.target_hz = self.config.default_hz

        # History for smoothing
        self.hz_history: deque = deque(maxlen=self.config.smoothing_window)
        self.hz_history.append(self.current_hz)

        # Adjustment factors
        self.load_factor = 1.0
        self.risk_factor = 1.0
        self.warning_factor = 1.0
        self.override_factor = 1.0

        # Statistics
        self.stats = {
            "adjustments": 0,
            "spike_suppressions": 0,
            "max_hz_hits": 0,
            "min_hz_hits": 0
        }

    def update(
        self,
        system_load: float = 0.0,
        risk_score: float = 0.0,
        warning_level: float = 0.0,
        override_active: bool = False
    ) -> float:
        """
        Update tick frequency based on current conditions.

        Args:
            system_load: System load (0-1)
            risk_score: Risk score (0-100)
            warning_level: Meta-agent warning level (0-1)
            override_active: User override active

        Returns:
            New tick frequency (Hz)
        """
        # Calculate adjustment factors
        self._update_factors(system_load, risk_score, warning_level, override_active)

        # Compute target frequency
        base_hz = self.config.default_hz

        # Apply factors (multiplicative)
        self.target_hz = (
            base_hz *
            self.load_factor *
            self.risk_factor *
            self.warning_factor *
            self.override_factor
        )

        # Clamp to bounds
        self.target_hz = max(self.config.min_hz, min(self.config.max_hz, self.target_hz))

        # Adaptive transition (smooth adjustment)
        delta = self.target_hz - self.current_hz
        self.current_hz += delta * self.config.adaptation_rate

        # Spike suppression
        if self._is_spike(self.current_hz):
            logger.warning(f"Tick spike detected, suppressing")
            self.current_hz = self._suppress_spike(self.current_hz)
            self.stats["spike_suppressions"] += 1

        # Update history
        self.hz_history.append(self.current_hz)

        # Update statistics
        self.stats["adjustments"] += 1
        if self.current_hz >= self.config.max_hz - 0.01:
            self.stats["max_hz_hits"] += 1
        if self.current_hz <= self.config.min_hz + 0.01:
            self.stats["min_hz_hits"] += 1

        logger.debug(f"Tick frequency updated: {self.current_hz:.2f} Hz (target: {self.target_hz:.2f} Hz)")

        return self.current_hz

    def _update_factors(
        self,
        system_load: float,
        risk_score: float,
        warning_level: float,
        override_active: bool
    ) -> None:
        """
        Update adjustment factors.

        Args:
            system_load: System load (0-1)
            risk_score: Risk score (0-100)
            warning_level: Warning level (0-1)
            override_active: Override active flag
        """
        # Load factor: Higher load = Lower frequency
        # Range: 0.3 (high load) to 1.0 (low load)
        self.load_factor = 1.0 - (system_load * 0.7)

        # Risk factor: Higher risk = Higher frequency
        # Range: 1.0 (low risk) to 2.5 (high risk)
        normalized_risk = risk_score / 100.0
        self.risk_factor = 1.0 + (normalized_risk * 1.5)

        # Warning factor: Warnings = Higher frequency
        # Range: 1.0 (no warnings) to 2.0 (high warnings)
        self.warning_factor = 1.0 + warning_level

        # Override factor: Override = Maximum frequency
        # Range: 1.0 (no override) to 3.0 (override active)
        self.override_factor = 3.0 if override_active else 1.0

    def _is_spike(self, new_hz: float) -> bool:
        """
        Check if frequency change is a spike.

        Args:
            new_hz: New frequency

        Returns:
            True if spike detected
        """
        if len(self.hz_history) < 2:
            return False

        avg_hz = sum(self.hz_history) / len(self.hz_history)
        ratio = abs(new_hz - avg_hz) / (avg_hz + 0.001)

        return ratio > self.config.spike_threshold

    def _suppress_spike(self, new_hz: float) -> float:
        """
        Suppress frequency spike.

        Args:
            new_hz: Spike frequency

        Returns:
            Suppressed frequency
        """
        avg_hz = sum(self.hz_history) / len(self.hz_history)
        # Limit change to spike threshold
        max_change = avg_hz * self.config.spike_threshold
        if new_hz > avg_hz:
            return min(new_hz, avg_hz + max_change)
        else:
            return max(new_hz, avg_hz - max_change)

    def get_current_hz(self) -> float:
        """Get current tick frequency"""
        return self.current_hz

    def get_tick_interval(self) -> float:
        """Get current tick interval in seconds"""
        return 1.0 / self.current_hz if self.current_hz > 0 else float('inf')

    def get_smoothed_hz(self) -> float:
        """Get smoothed tick frequency"""
        if not self.hz_history:
            return self.current_hz
        return sum(self.hz_history) / len(self.hz_history)

    def force_frequency(self, hz: float) -> None:
        """
        Force specific tick frequency.

        Args:
            hz: Desired frequency (Hz)
        """
        hz = max(self.config.min_hz, min(self.config.max_hz, hz))
        self.current_hz = hz
        self.target_hz = hz
        logger.info(f"Tick frequency forced to {hz:.2f} Hz")

    def reset(self) -> None:
        """Reset to default frequency"""
        self.current_hz = self.config.default_hz
        self.target_hz = self.config.default_hz
        self.hz_history.clear()
        self.hz_history.append(self.current_hz)
        logger.info("Tick engine reset to default frequency")

    def get_statistics(self) -> Dict[str, Any]:
        """Get tick engine statistics"""
        return {
            "current_hz": round(self.current_hz, 2),
            "target_hz": round(self.target_hz, 2),
            "smoothed_hz": round(self.get_smoothed_hz(), 2),
            "tick_interval_ms": round(self.get_tick_interval() * 1000, 2),
            "adjustments": self.stats["adjustments"],
            "spike_suppressions": self.stats["spike_suppressions"],
            "max_hz_hits": self.stats["max_hz_hits"],
            "min_hz_hits": self.stats["min_hz_hits"],
            "load_factor": round(self.load_factor, 2),
            "risk_factor": round(self.risk_factor, 2),
            "warning_factor": round(self.warning_factor, 2),
            "override_factor": round(self.override_factor, 2)
        }


def create_adaptive_tick_engine(config: Optional[TickConfig] = None) -> AdaptiveTickEngine:
    """
    Factory function to create AdaptiveTickEngine.

    Args:
        config: Optional tick configuration

    Returns:
        AdaptiveTickEngine instance
    """
    return AdaptiveTickEngine(config)
