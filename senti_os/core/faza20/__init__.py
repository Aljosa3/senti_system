"""
FAZA 20 - User Experience Layer (UXL)

Human-centered interaction and observability layer for SENTI OS.

Provides:
- Real-time visual OS status
- System diagnostics
- Heartbeat monitoring
- Onboarding assistant
- UX state management
- Unified explainability bridge
- UI API for external interfaces

CRITICAL PRIVACY GUARANTEES:
    - NO password storage
    - NO biometric data storage
    - NO biometric processing
    - NO external network calls
    - Only internal API access

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict, Any, Optional

# Import all components
from senti_os.core.faza20.status_collector import StatusCollector, ModuleHealth
from senti_os.core.faza20.heartbeat_monitor import HeartbeatMonitor, HeartbeatStatus
from senti_os.core.faza20.diagnostics_engine import DiagnosticsEngine, DiagnosticLevel
from senti_os.core.faza20.onboarding_assistant import OnboardingAssistant, OnboardingStep
from senti_os.core.faza20.ux_state_manager import UXStateManager, AlertLevel
from senti_os.core.faza20.explainability_bridge import (
    ExplainabilityBridge,
    ExplainabilitySource,
    ExplainabilityLevel
)
from senti_os.core.faza20.ui_api import UIAPI


# Module exports
__all__ = [
    "FAZA20Stack",
    "StatusCollector",
    "ModuleHealth",
    "HeartbeatMonitor",
    "HeartbeatStatus",
    "DiagnosticsEngine",
    "DiagnosticLevel",
    "OnboardingAssistant",
    "OnboardingStep",
    "UXStateManager",
    "AlertLevel",
    "ExplainabilityBridge",
    "ExplainabilitySource",
    "ExplainabilityLevel",
    "UIAPI",
    "get_info"
]


class FAZA20Stack:
    """
    Complete FAZA 20 User Experience Layer stack.

    Provides unified interface for human-centered interaction
    and system observability.
    """

    def __init__(
        self,
        faza16_llm_control=None,
        faza17_orchestration=None,
        faza18_auth_flow=None,
        faza19_uil=None,
        faza21_persistence=None,
        status_collection_frequency: int = 5,
        heartbeat_interval: int = 10
    ):
        """
        Initialize FAZA 20 stack.

        Args:
            faza16_llm_control: Optional FAZA 16 LLM control layer.
            faza17_orchestration: Optional FAZA 17 orchestration layer.
            faza18_auth_flow: Optional FAZA 18 auth flow layer.
            faza19_uil: Optional FAZA 19 UIL layer.
            faza21_persistence: Optional FAZA 21 persistence layer.
            status_collection_frequency: Status collection interval (seconds).
            heartbeat_interval: Heartbeat interval (seconds).
        """
        # Initialize components
        self.status_collector = StatusCollector(
            collection_frequency_seconds=status_collection_frequency
        )

        self.heartbeat_monitor = HeartbeatMonitor(
            interval_seconds=heartbeat_interval
        )

        self.diagnostics_engine = DiagnosticsEngine()

        # Initialize with persistence if available
        persistence_manager = None
        if faza21_persistence and hasattr(faza21_persistence, 'persistence_manager'):
            persistence_manager = faza21_persistence.persistence_manager

        self.ux_state_manager = UXStateManager(
            persistence_manager=persistence_manager
        )

        self.onboarding_assistant = OnboardingAssistant(
            ux_state_manager=self.ux_state_manager
        )

        self.explainability_bridge = ExplainabilityBridge()

        self.ui_api = UIAPI(self)

        # Store module references
        self._faza16_llm_control = faza16_llm_control
        self._faza17_orchestration = faza17_orchestration
        self._faza18_auth_flow = faza18_auth_flow
        self._faza19_uil = faza19_uil
        self._faza21_persistence = faza21_persistence

        self._initialized = False
        self._started = False

    def initialize(self) -> bool:
        """
        Initialize FAZA 20 stack.

        Returns:
            True if initialized successfully.
        """
        try:
            # Register modules with status collector
            if self._faza16_llm_control:
                self.status_collector.register_module(
                    "faza16_llm_control",
                    self._faza16_llm_control
                )
                self.diagnostics_engine.register_module(
                    "faza16_llm_control",
                    self._faza16_llm_control
                )
                self.heartbeat_monitor.register_module(
                    "faza16_llm_control",
                    self._faza16_llm_control
                )

            if self._faza17_orchestration:
                self.status_collector.register_module(
                    "faza17_orchestration",
                    self._faza17_orchestration
                )
                self.diagnostics_engine.register_module(
                    "faza17_orchestration",
                    self._faza17_orchestration
                )
                self.heartbeat_monitor.register_module(
                    "faza17_orchestration",
                    self._faza17_orchestration
                )

            if self._faza18_auth_flow:
                self.status_collector.register_module(
                    "faza18_auth_flow",
                    self._faza18_auth_flow
                )
                self.diagnostics_engine.register_module(
                    "faza18_auth_flow",
                    self._faza18_auth_flow
                )

            if self._faza19_uil:
                self.status_collector.register_module(
                    "faza19_uil",
                    self._faza19_uil
                )
                self.diagnostics_engine.register_module(
                    "faza19_uil",
                    self._faza19_uil
                )
                self.heartbeat_monitor.register_module(
                    "faza19_uil",
                    self._faza19_uil
                )

                # Register event bus with heartbeat monitor
                if hasattr(self._faza19_uil, 'event_bus'):
                    self.heartbeat_monitor.register_event_bus(
                        self._faza19_uil.event_bus
                    )

            if self._faza21_persistence:
                self.status_collector.register_module(
                    "faza21_persistence",
                    self._faza21_persistence
                )
                self.diagnostics_engine.register_module(
                    "faza21_persistence",
                    self._faza21_persistence
                )
                self.heartbeat_monitor.register_module(
                    "faza21_persistence",
                    self._faza21_persistence
                )

            # Register modules with onboarding assistant
            self.onboarding_assistant.register_modules(
                faza16_llm_control=self._faza16_llm_control,
                faza19_uil=self._faza19_uil,
                faza21_persistence=self._faza21_persistence,
                diagnostics_engine=self.diagnostics_engine
            )

            # Register modules with explainability bridge
            self.explainability_bridge.register_modules(
                faza16_llm_control=self._faza16_llm_control,
                faza17_orchestration=self._faza17_orchestration,
                faza19_event_bus=self._faza19_uil.event_bus if self._faza19_uil and hasattr(self._faza19_uil, 'event_bus') else None
            )

            self._initialized = True

            # Log initialization
            self.explainability_bridge.explain_system_operation(
                operation="faza20_initialization",
                description="FAZA 20 User Experience Layer initialized successfully",
                level=ExplainabilityLevel.BASIC
            )

            return True
        except Exception as e:
            # Log error
            if hasattr(self, 'ux_state_manager'):
                self.ux_state_manager.add_alert(
                    level=AlertLevel.ERROR,
                    title="FAZA 20 Initialization Failed",
                    message=f"Failed to initialize UX layer: {str(e)}"
                )
            return False

    def start(self) -> bool:
        """
        Start FAZA 20 services.

        Returns:
            True if started successfully.
        """
        if not self._initialized:
            return False

        try:
            # Start heartbeat monitoring
            self.heartbeat_monitor.start()

            self._started = True

            # Log start
            self.explainability_bridge.explain_system_operation(
                operation="faza20_start",
                description="FAZA 20 services started: heartbeat monitoring active",
                level=ExplainabilityLevel.BASIC
            )

            return True
        except Exception as e:
            self.ux_state_manager.add_alert(
                level=AlertLevel.ERROR,
                title="FAZA 20 Start Failed",
                message=f"Failed to start UX layer services: {str(e)}"
            )
            return False

    def stop(self):
        """Stop FAZA 20 services."""
        if not self._started:
            return

        # Stop heartbeat monitoring
        self.heartbeat_monitor.stop()

        self._started = False

        # Log stop
        self.explainability_bridge.explain_system_operation(
            operation="faza20_stop",
            description="FAZA 20 services stopped",
            level=ExplainabilityLevel.BASIC
        )

    def get_status(self) -> Dict[str, Any]:
        """
        Get FAZA 20 stack status.

        Returns:
            Dictionary with complete stack status.
        """
        return {
            "initialized": self._initialized,
            "started": self._started,
            "components": {
                "status_collector": self.status_collector.get_collection_info(),
                "heartbeat_monitor": self.heartbeat_monitor.get_statistics(),
                "diagnostics_engine": {
                    "diagnostics_run_count": self.diagnostics_engine.get_diagnostics_count()
                },
                "ux_state_manager": self.ux_state_manager.get_metadata(),
                "explainability_bridge": self.explainability_bridge.get_statistics(),
                "onboarding_assistant": {
                    "is_complete": self.onboarding_assistant.is_onboarding_complete()
                }
            },
            "modules_registered": {
                "faza16": self._faza16_llm_control is not None,
                "faza17": self._faza17_orchestration is not None,
                "faza18": self._faza18_auth_flow is not None,
                "faza19": self._faza19_uil is not None,
                "faza21": self._faza21_persistence is not None
            }
        }

    def run_diagnostics(self, quick: bool = False) -> Any:
        """
        Run system diagnostics.

        Args:
            quick: If True, run only essential tests.

        Returns:
            DiagnosticReport with results.
        """
        return self.diagnostics_engine.run_diagnostics(quick=quick)

    def get_explainability(self, limit: int = 50) -> Any:
        """
        Get recent explainability data.

        Args:
            limit: Maximum entries to return.

        Returns:
            ExplainabilitySnapshot.
        """
        return self.explainability_bridge.get_snapshot()


def get_info() -> Dict[str, str]:
    """
    Get FAZA 20 module information.

    Returns:
        Dictionary with comprehensive module metadata.
    """
    return {
        "module": "faza20",
        "name": "User Experience Layer (UXL)",
        "version": "1.0.0",
        "faza": "20",
        "description": "Human-centered interaction and observability layer",

        # Privacy Guarantees
        "privacy_compliant": "true",
        "gdpr_compliant": "true",
        "zvop_compliant": "true",
        "eu_ai_act_compliant": "true",

        # Critical Security Rules
        "stores_passwords": "false",
        "stores_biometrics": "false",
        "processes_biometrics": "false",
        "makes_external_calls": "false",

        # What it DOES
        "collects_internal_status": "true",
        "monitors_heartbeats": "true",
        "runs_diagnostics": "true",
        "provides_onboarding": "true",
        "manages_ux_state": "true",
        "provides_explainability": "true",

        # Components
        "components": {
            "status_collector": "Collects health status from all FAZA modules",
            "heartbeat_monitor": "Periodic heartbeat monitoring with failure detection",
            "diagnostics_engine": "Comprehensive system diagnostics",
            "onboarding_assistant": "Step-by-step first-run assistant",
            "ux_state_manager": "UX state persistence via FAZA 21",
            "explainability_bridge": "Unified explainability from FAZA 16/17/19",
            "ui_api": "Pure Python API (no HTTP)"
        },

        # Architecture
        "architecture": "observability_layer",
        "approach": "human_centered_trust_transparency",

        # Integration
        "integrates_with": [
            "FAZA 16 (LLM Control Layer)",
            "FAZA 17 (Multi-Model Orchestration)",
            "FAZA 18 (Auth Flow)",
            "FAZA 19 (UIL & Multi-Device)",
            "FAZA 21 (Persistence Layer)"
        ],

        # Contact
        "author": "SENTI OS Core Team",
        "license": "Proprietary"
    }


# Version info
__version__ = "1.0.0"
__author__ = "SENTI OS Core Team"
__license__ = "Proprietary"
