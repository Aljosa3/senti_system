"""
FAZA 29 – Enterprise Governance Engine
Feedback Loop

Advanced feedback control system for system stability.
Features:
- Integral correction
- Threshold gates
- Reinforcement signals from FAZA 28.5 policies
- Smoothing factor computation
- Damping coefficient calculation
- Corrective signal generation

Maintains system stability under load and stress conditions.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class FeedbackConfig:
    """
    Feedback loop configuration.

    Attributes:
        kp: Proportional gain
        ki: Integral gain
        kd: Derivative gain
        setpoint: Target setpoint (0-1)
        integral_limit: Integral windup limit
        deadband: Deadband threshold
        smoothing_window: Smoothing window size
    """
    kp: float = 0.5          # Proportional gain
    ki: float = 0.1          # Integral gain
    kd: float = 0.2          # Derivative gain
    setpoint: float = 0.5    # Target stability point
    integral_limit: float = 10.0
    deadband: float = 0.02   # 2% deadband
    smoothing_window: int = 10


@dataclass
class FeedbackState:
    """
    Feedback loop state.

    Attributes:
        error: Current error
        integral: Integral accumulator
        derivative: Derivative term
        output: Control output
        timestamp: State timestamp
    """
    error: float = 0.0
    integral: float = 0.0
    derivative: float = 0.0
    output: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class FeedbackLoop:
    """
    Advanced feedback control system for system stability.

    Implements PID-like control with threshold gates, reinforcement
    signals, and damping for robust system stabilization.
    """

    def __init__(self, config: Optional[FeedbackConfig] = None):
        """
        Initialize feedback loop.

        Args:
            config: Feedback configuration
        """
        self.config = config or FeedbackConfig()

        # State
        self.state = FeedbackState()
        self.previous_error = 0.0

        # History for smoothing
        self.error_history: deque = deque(maxlen=self.config.smoothing_window)
        self.output_history: deque = deque(maxlen=self.config.smoothing_window)

        # Reinforcement signals
        self.reinforcement_signals: Dict[str, float] = {}

        # Threshold gates
        self.gates = {
            "low_stability": 0.3,
            "medium_stability": 0.6,
            "high_stability": 0.8
        }

        # Statistics
        self.stats = {
            "corrections": 0,
            "integral_saturations": 0,
            "deadband_skips": 0,
            "reinforcements_applied": 0
        }

    def update(
        self,
        measurement: float,
        dt: float = 1.0,
        reinforcement: Optional[Dict[str, float]] = None
    ) -> Tuple[float, float, float]:
        """
        Update feedback loop.

        Args:
            measurement: Current system measurement (0-1)
            dt: Time delta since last update (seconds)
            reinforcement: Optional reinforcement signals from FAZA 28.5

        Returns:
            Tuple of (corrective_signal, smoothing_factor, damping_coefficient)
        """
        # Apply reinforcement signals
        if reinforcement:
            self.reinforcement_signals.update(reinforcement)
            self.stats["reinforcements_applied"] += 1

        # Calculate error
        error = self.config.setpoint - measurement

        # Apply deadband
        if abs(error) < self.config.deadband:
            self.stats["deadband_skips"] += 1
            return self.state.output, 1.0, 1.0

        # Store error history
        self.error_history.append(error)

        # Proportional term
        p_term = self.config.kp * error

        # Integral term with anti-windup
        self.state.integral += error * dt
        self.state.integral = max(-self.config.integral_limit,
                                   min(self.config.integral_limit, self.state.integral))
        if abs(self.state.integral) >= self.config.integral_limit:
            self.stats["integral_saturations"] += 1

        i_term = self.config.ki * self.state.integral

        # Derivative term
        if dt > 0:
            self.state.derivative = (error - self.previous_error) / dt
        d_term = self.config.kd * self.state.derivative

        # PID output
        pid_output = p_term + i_term + d_term

        # Apply reinforcement
        reinforcement_factor = self._calculate_reinforcement_factor()
        corrective_signal = pid_output * reinforcement_factor

        # Apply threshold gates
        corrective_signal = self._apply_threshold_gates(corrective_signal, measurement)

        # Update state
        self.state.error = error
        self.state.output = corrective_signal
        self.state.timestamp = datetime.now()
        self.previous_error = error

        # Store output history
        self.output_history.append(corrective_signal)

        # Calculate smoothing factor and damping coefficient
        smoothing_factor = self._calculate_smoothing_factor()
        damping_coefficient = self._calculate_damping_coefficient(measurement)

        # Update statistics
        self.stats["corrections"] += 1

        logger.debug(f"Feedback: error={error:.3f}, output={corrective_signal:.3f}, "
                    f"smooth={smoothing_factor:.3f}, damp={damping_coefficient:.3f}")

        return corrective_signal, smoothing_factor, damping_coefficient

    def _calculate_reinforcement_factor(self) -> float:
        """
        Calculate reinforcement factor from FAZA 28.5 signals.

        Returns:
            Reinforcement factor (0.5 - 2.0)
        """
        if not self.reinforcement_signals:
            return 1.0

        # Aggregate reinforcement signals
        positive_signals = sum(v for v in self.reinforcement_signals.values() if v > 0)
        negative_signals = sum(v for v in self.reinforcement_signals.values() if v < 0)

        # Calculate net reinforcement
        net_reinforcement = positive_signals + negative_signals

        # Map to factor range (0.5 - 2.0)
        factor = 1.0 + (net_reinforcement * 0.5)
        return max(0.5, min(2.0, factor))

    def _apply_threshold_gates(self, signal: float, measurement: float) -> float:
        """
        Apply threshold gates to corrective signal.

        Args:
            signal: Raw corrective signal
            measurement: Current measurement

        Returns:
            Gated signal
        """
        # Low stability gate - reduce aggressive corrections
        if measurement < self.gates["low_stability"]:
            signal *= 0.5
            logger.debug("Low stability gate applied")

        # Medium stability gate - normal operation
        elif measurement < self.gates["medium_stability"]:
            pass  # No modification

        # High stability gate - allow aggressive corrections
        elif measurement >= self.gates["high_stability"]:
            signal *= 1.5
            logger.debug("High stability gate applied")

        return signal

    def _calculate_smoothing_factor(self) -> float:
        """
        Calculate smoothing factor based on error history.

        Returns:
            Smoothing factor (0.0 - 1.0)
        """
        if len(self.error_history) < 2:
            return 0.5

        # Calculate error variance
        errors = list(self.error_history)
        mean_error = sum(errors) / len(errors)
        variance = sum((e - mean_error) ** 2 for e in errors) / len(errors)

        # Map variance to smoothing factor
        # High variance = more smoothing needed
        smoothing = 1.0 - min(variance * 10, 1.0)

        return max(0.0, min(1.0, smoothing))

    def _calculate_damping_coefficient(self, measurement: float) -> float:
        """
        Calculate damping coefficient based on system state.

        Args:
            measurement: Current measurement

        Returns:
            Damping coefficient (0.0 - 1.0)
        """
        # Base damping on distance from setpoint
        distance = abs(self.config.setpoint - measurement)

        # Closer to setpoint = more damping
        damping = 1.0 - (distance * 2.0)

        # Apply derivative influence (oscillation damping)
        if abs(self.state.derivative) > 0.1:
            damping *= 0.7  # Increase damping during oscillations

        return max(0.0, min(1.0, damping))

    def add_reinforcement_signal(self, signal_name: str, value: float) -> None:
        """
        Add reinforcement signal from FAZA 28.5.

        Args:
            signal_name: Signal identifier
            value: Signal value (-1.0 to 1.0)
        """
        self.reinforcement_signals[signal_name] = max(-1.0, min(1.0, value))
        logger.debug(f"Reinforcement signal added: {signal_name}={value:.3f}")

    def clear_reinforcement_signals(self) -> None:
        """Clear all reinforcement signals"""
        self.reinforcement_signals.clear()

    def set_setpoint(self, setpoint: float) -> None:
        """
        Set target setpoint.

        Args:
            setpoint: New setpoint (0-1)
        """
        self.config.setpoint = max(0.0, min(1.0, setpoint))
        logger.info(f"Setpoint updated to {self.config.setpoint:.3f}")

    def reset(self) -> None:
        """Reset feedback loop state"""
        self.state = FeedbackState()
        self.previous_error = 0.0
        self.error_history.clear()
        self.output_history.clear()
        self.reinforcement_signals.clear()
        logger.info("Feedback loop reset")

    def get_stability_score(self) -> float:
        """
        Calculate stability score based on error history.

        Returns:
            Stability score (0-1, 1 = stable)
        """
        if len(self.error_history) < 2:
            return 0.5

        # Calculate error magnitude
        errors = list(self.error_history)
        mean_abs_error = sum(abs(e) for e in errors) / len(errors)

        # Map to stability score (lower error = higher stability)
        stability = 1.0 - min(mean_abs_error * 2, 1.0)

        return max(0.0, min(1.0, stability))

    def is_stable(self, threshold: float = 0.7) -> bool:
        """
        Check if system is stable.

        Args:
            threshold: Stability threshold

        Returns:
            True if stable, False otherwise
        """
        return self.get_stability_score() >= threshold

    def get_statistics(self) -> Dict[str, Any]:
        """Get feedback loop statistics"""
        return {
            "corrections": self.stats["corrections"],
            "integral_saturations": self.stats["integral_saturations"],
            "deadband_skips": self.stats["deadband_skips"],
            "reinforcements_applied": self.stats["reinforcements_applied"],
            "current_error": round(self.state.error, 4),
            "current_integral": round(self.state.integral, 4),
            "current_output": round(self.state.output, 4),
            "stability_score": round(self.get_stability_score(), 3),
            "is_stable": self.is_stable()
        }

    def get_status(self) -> Dict[str, Any]:
        """Get feedback loop status"""
        return {
            "setpoint": self.config.setpoint,
            "error": round(self.state.error, 4),
            "integral": round(self.state.integral, 4),
            "derivative": round(self.state.derivative, 4),
            "output": round(self.state.output, 4),
            "stability_score": round(self.get_stability_score(), 3),
            "reinforcement_count": len(self.reinforcement_signals),
            "is_stable": self.is_stable()
        }


def create_feedback_loop(config: Optional[FeedbackConfig] = None) -> FeedbackLoop:
    """
    Factory function to create FeedbackLoop instance.

    Args:
        config: Optional feedback configuration

    Returns:
        FeedbackLoop instance
    """
    return FeedbackLoop(config)
