"""
FAZA 20 - UI API

Pure Python API (no HTTP server) providing programmatic access to SENTI OS
UX layer for external UI applications.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class UIAPI:
    """
    Pure Python API for SENTI OS UX layer.

    Provides programmatic interface for UI applications:
    - Status queries
    - Module health
    - Heartbeat monitoring
    - Diagnostics execution
    - Onboarding control
    - UX state access
    - Explainability data

    Designed to be wrapped with FastAPI/REST later.
    NO HTTP server - pure Python only.
    """

    def __init__(self, faza20_stack):
        """
        Initialize UI API.

        Args:
            faza20_stack: FAZA20Stack instance.
        """
        self.stack = faza20_stack

    def get_status(self) -> Dict[str, Any]:
        """
        Get complete SENTI OS status.

        Returns:
            Dictionary with overall system status.
        """
        try:
            status_snapshot = self.stack.status_collector.collect_status()

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "status": {
                    "overall_health": status_snapshot.overall_health.value,
                    "overall_score": status_snapshot.overall_score,
                    "uptime_seconds": status_snapshot.total_uptime_seconds,
                    "active_warnings": status_snapshot.active_warnings,
                    "active_errors": status_snapshot.active_errors,
                    "modules": [
                        {
                            "name": m.module_name,
                            "faza": m.faza_number,
                            "health": m.health.value,
                            "score": m.health_score,
                            "errors": m.error_count,
                            "warnings": m.warning_count
                        }
                        for m in status_snapshot.modules
                    ]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_module_status(self, module_name: str) -> Dict[str, Any]:
        """
        Get status for specific module.

        Args:
            module_name: Module identifier (e.g., "faza16_llm_control").

        Returns:
            Dictionary with module status.
        """
        try:
            module_status = self.stack.status_collector.get_module_status(module_name)

            if not module_status:
                return {
                    "success": False,
                    "error": f"Module {module_name} not found",
                    "timestamp": datetime.utcnow().isoformat()
                }

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "module": {
                    "name": module_status.module_name,
                    "faza": module_status.faza_number,
                    "health": module_status.health.value,
                    "score": module_status.health_score,
                    "errors": module_status.error_count,
                    "warnings": module_status.warning_count,
                    "last_updated": module_status.last_updated.isoformat(),
                    "metadata": module_status.metadata
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_heartbeat(self, module_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get heartbeat status.

        Args:
            module_name: Optional module to get heartbeat for.
                        If None, returns overall heartbeat status.

        Returns:
            Dictionary with heartbeat information.
        """
        try:
            if module_name:
                # Get specific module heartbeat
                latest = self.stack.heartbeat_monitor.get_latest_heartbeat(module_name)
                stats = self.stack.heartbeat_monitor.get_module_statistics(module_name)

                if not latest:
                    return {
                        "success": False,
                        "error": f"No heartbeat data for {module_name}",
                        "timestamp": datetime.utcnow().isoformat()
                    }

                return {
                    "success": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "module": module_name,
                    "heartbeat": {
                        "status": latest.status.value,
                        "sequence": latest.sequence_number,
                        "response_time_ms": latest.response_time_ms,
                        "last_beat": latest.timestamp.isoformat()
                    },
                    "statistics": stats
                }
            else:
                # Get overall heartbeat statistics
                stats = self.stack.heartbeat_monitor.get_statistics()

                return {
                    "success": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "overall": stats
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get last diagnostics results.

        Returns:
            Dictionary with diagnostics report.
        """
        try:
            report = self.stack.diagnostics_engine.get_last_report()

            if not report:
                return {
                    "success": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "diagnostics": None,
                    "message": "No diagnostics run yet"
                }

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "diagnostics": {
                    "overall_status": report.overall_status.value,
                    "tests_run": report.tests_run,
                    "tests_passed": report.tests_passed,
                    "tests_failed": report.tests_failed,
                    "warnings": report.warnings,
                    "errors": report.errors,
                    "duration_seconds": report.duration_seconds,
                    "timestamp": report.timestamp.isoformat(),
                    "results": [
                        {
                            "test": r.test_name,
                            "category": r.category,
                            "level": r.level.value,
                            "passed": r.passed,
                            "message": r.message
                        }
                        for r in report.results
                    ]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def trigger_diagnostics(self, quick: bool = False) -> Dict[str, Any]:
        """
        Run system diagnostics.

        Args:
            quick: If True, run only essential tests.

        Returns:
            Dictionary with diagnostics results.
        """
        try:
            report = self.stack.diagnostics_engine.run_diagnostics(quick=quick)

            # Update UX state
            if self.stack.ux_state_manager:
                self.stack.ux_state_manager.update_diagnostics_result(report)

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "diagnostics": {
                    "overall_status": report.overall_status.value,
                    "tests_run": report.tests_run,
                    "tests_passed": report.tests_passed,
                    "tests_failed": report.tests_failed,
                    "warnings": report.warnings,
                    "errors": report.errors,
                    "duration_seconds": report.duration_seconds,
                    "results": [
                        {
                            "test": r.test_name,
                            "category": r.category,
                            "level": r.level.value,
                            "passed": r.passed,
                            "message": r.message
                        }
                        for r in report.results
                    ]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def trigger_onboarding_step(
        self,
        step: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete an onboarding step.

        Args:
            step: Step name (e.g., "welcome", "generate_master_key").
            **kwargs: Step-specific parameters.

        Returns:
            Dictionary with step result.
        """
        try:
            from senti_os.core.faza20.onboarding_assistant import OnboardingStep

            # Convert string to enum
            step_enum = OnboardingStep(step)

            result = self.stack.onboarding_assistant.complete_step(
                step_enum,
                **kwargs
            )

            return {
                "success": result.completed,
                "timestamp": datetime.utcnow().isoformat(),
                "step": step,
                "message": result.message,
                "details": result.details
            }
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid step: {step}",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_ux_state(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get UX state.

        Args:
            category: Optional category filter.

        Returns:
            Dictionary with UX state.
        """
        try:
            state = self.stack.ux_state_manager.get_state(category)

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "category": category,
                "state": state
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_alerts(
        self,
        level: Optional[str] = None,
        dismissed: Optional[bool] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get UX alerts.

        Args:
            level: Optional alert level filter ("info", "warning", "error", "critical").
            dismissed: Optional dismissed status filter.
            limit: Maximum alerts to return.

        Returns:
            Dictionary with alerts.
        """
        try:
            from senti_os.core.faza20.ux_state_manager import AlertLevel

            # Convert level string to enum if provided
            level_enum = None
            if level:
                level_enum = AlertLevel(level)

            alerts = self.stack.ux_state_manager.get_alerts(
                level=level_enum,
                dismissed=dismissed,
                limit=limit
            )

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "count": len(alerts),
                "alerts": [
                    {
                        "id": a.alert_id,
                        "level": a.level.value,
                        "title": a.title,
                        "message": a.message,
                        "timestamp": a.timestamp.isoformat(),
                        "dismissed": a.dismissed,
                        "metadata": a.metadata
                    }
                    for a in alerts
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def dismiss_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Dismiss an alert.

        Args:
            alert_id: Alert ID to dismiss.

        Returns:
            Dictionary with result.
        """
        try:
            success = self.stack.ux_state_manager.dismiss_alert(alert_id)

            return {
                "success": success,
                "timestamp": datetime.utcnow().isoformat(),
                "alert_id": alert_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_explainability(
        self,
        source: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get explainability data.

        Args:
            source: Optional source filter.
            level: Optional detail level filter.
            limit: Maximum entries to return.

        Returns:
            Dictionary with explainability entries.
        """
        try:
            from senti_os.core.faza20.explainability_bridge import (
                ExplainabilitySource,
                ExplainabilityLevel
            )

            # Convert filters
            source_enum = ExplainabilitySource(source) if source else None
            level_enum = ExplainabilityLevel(level) if level else None

            entries = self.stack.explainability_bridge.get_entries(
                source=source_enum,
                level=level_enum,
                limit=limit
            )

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "count": len(entries),
                "entries": [
                    {
                        "id": e.entry_id,
                        "source": e.source.value,
                        "level": e.level.value,
                        "title": e.title,
                        "description": e.description,
                        "timestamp": e.timestamp.isoformat(),
                        "metadata": e.metadata
                    }
                    for e in entries
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_onboarding_state(self) -> Dict[str, Any]:
        """
        Get current onboarding state.

        Returns:
            Dictionary with onboarding progress.
        """
        try:
            state = self.stack.onboarding_assistant.get_state()
            current_step_info = self.stack.onboarding_assistant.get_current_step_info()

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "onboarding": {
                    "is_complete": state.is_complete,
                    "current_step": state.current_step.value,
                    "steps_completed": [s.value for s in state.steps_completed],
                    "started_at": state.started_at.isoformat() if state.started_at else None,
                    "completed_at": state.completed_at.isoformat() if state.completed_at else None,
                    "current_step_info": current_step_info,
                    "progress": len(state.steps_completed) / state.metadata["total_steps"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "ui_api",
        "faza": "20",
        "version": "1.0.0",
        "description": "Pure Python API for UX layer (no HTTP server)"
    }
