"""
FAZA 13 - Senti OS Prediction Engine
Predictive capabilities for Senti OS

Provides state forecasting, failure prediction, and action recommendations
based on memory (FAZA 12), AI layer (FAZA 5), and security policies (FAZA 8).

Components:
- PredictionEngine: Low-level prediction mechanism
- PredictionManager: High-level orchestrator
- PredictionRules: Validation and security
- PredictionService: OS-level service for FAZA 6
- Events: PredictionEvent, HighRiskPredictionEvent, etc.

Example usage:
    from senti_core_module.senti_prediction import PredictionManager

    manager = PredictionManager(memory_manager, event_bus)
    result = manager.predict_failures()
    print(f"Prediction: {result.prediction}")
    print(f"Risk Score: {result.risk_score}")
"""

from .prediction_engine import PredictionEngine, PredictionResult
from .prediction_manager import PredictionManager
from .prediction_rules import PredictionRules
from .prediction_service import PredictionService
from .prediction_events import (
    PredictionEvent,
    PredictionTriggerEvent,
    HighRiskPredictionEvent,
    PredictionValidationEvent,
    PredictionStatsEvent,
    PREDICTION_GENERATED,
    PREDICTION_TRIGGER,
    HIGH_RISK_PREDICTION,
    PREDICTION_VALIDATION,
    PREDICTION_STATS
)

__all__ = [
    # Core components
    "PredictionEngine",
    "PredictionResult",
    "PredictionManager",
    "PredictionRules",
    "PredictionService",

    # Events
    "PredictionEvent",
    "PredictionTriggerEvent",
    "HighRiskPredictionEvent",
    "PredictionValidationEvent",
    "PredictionStatsEvent",

    # Event type constants
    "PREDICTION_GENERATED",
    "PREDICTION_TRIGGER",
    "HIGH_RISK_PREDICTION",
    "PREDICTION_VALIDATION",
    "PREDICTION_STATS"
]

__version__ = "1.0.0"
__faza__ = "FAZA 13"
