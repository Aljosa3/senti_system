"""
FAZA 14 - Senti OS Anomaly Detection Engine
Anomaly detection capabilities for Senti OS

Provides statistical, pattern, and rule-based anomaly detection
with integration to FAZA 5, 6, 8, 12, and 13.

Components:
- AnomalyEngine: Low-level detection mechanism
- AnomalyManager: High-level orchestrator
- AnomalyRules: Validation and security
- AnomalyService: OS-level service for FAZA 6
- Events: AnomalyEvent, HighSeverityEvent, etc.

Example usage:
    from senti_core_module.senti_anomaly import AnomalyManager

    manager = AnomalyManager(memory_manager, prediction_manager, event_bus)
    result = manager.analyze_system()

    for component, anomaly in result.items():
        print(f"{component}: {anomaly.severity} - {anomaly.reason}")
"""

from .anomaly_engine import AnomalyEngine, AnomalyResult
from .anomaly_manager import AnomalyManager
from .anomaly_rules import AnomalyRules
from .anomaly_service import AnomalyService
from .anomaly_events import (
    AnomalyEvent,
    HighSeverityEvent,
    AnomalyStatsEvent,
    AnomalyResolvedEvent,
    AnomalyPatternEvent,
    AnomalyValidationEvent,
    ANOMALY_DETECTED,
    HIGH_SEVERITY_ANOMALY,
    ANOMALY_STATS_UPDATE,
    ANOMALY_RESOLVED,
    ANOMALY_PATTERN_DETECTED,
    ANOMALY_VALIDATION
)

__all__ = [
    # Core components
    "AnomalyEngine",
    "AnomalyResult",
    "AnomalyManager",
    "AnomalyRules",
    "AnomalyService",

    # Events
    "AnomalyEvent",
    "HighSeverityEvent",
    "AnomalyStatsEvent",
    "AnomalyResolvedEvent",
    "AnomalyPatternEvent",
    "AnomalyValidationEvent",

    # Event type constants
    "ANOMALY_DETECTED",
    "HIGH_SEVERITY_ANOMALY",
    "ANOMALY_STATS_UPDATE",
    "ANOMALY_RESOLVED",
    "ANOMALY_PATTERN_DETECTED",
    "ANOMALY_VALIDATION"
]

__version__ = "1.0.0"
__faza__ = "FAZA 14"
