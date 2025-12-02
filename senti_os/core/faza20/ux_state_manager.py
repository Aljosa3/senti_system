"""
FAZA 20 - UX State Manager

Manages UX layer state including onboarding progress, last diagnostics result,
warnings/errors for UI, and persists state via FAZA 21.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import threading


class AlertLevel(Enum):
    """Alert level for warnings and errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class UXAlert:
    """UX alert for user notification."""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    dismissed: bool = False
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UXStateManager:
    """
    Manages UX layer state for SENTI OS.

    Features:
    - Onboarding progress tracking
    - Diagnostics result caching
    - Warning/error management
    - Alert queueing
    - Persistent state via FAZA 21
    """

    def __init__(self, persistence_manager=None):
        """
        Initialize UX state manager.

        Args:
            persistence_manager: FAZA 21 PersistenceManager instance.
        """
        self.persistence_manager = persistence_manager
        self._lock = threading.Lock()

        # State
        self._state: Dict[str, Any] = {
            "onboarding": {},
            "last_diagnostics": None,
            "system_status": {},
            "user_preferences": {},
            "metadata": {}
        }

        # Alerts
        self._alerts: List[UXAlert] = []
        self._alert_counter = 0

        # Load persisted state
        self._load_state()

    def update_state(self, category: str, data: Any):
        """
        Update state for a category.

        Args:
            category: State category (e.g., "onboarding", "diagnostics").
            data: State data to store.
        """
        with self._lock:
            self._state[category] = data
            self._persist_state()

    def get_state(self, category: Optional[str] = None) -> Any:
        """
        Get state for a category or entire state.

        Args:
            category: Optional category to retrieve.

        Returns:
            State data for category, or entire state if None.
        """
        with self._lock:
            if category:
                return self._state.get(category)
            return self._state.copy()

    def add_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a new UX alert.

        Args:
            level: Alert severity level.
            title: Alert title.
            message: Alert message.
            metadata: Optional additional data.

        Returns:
            Alert ID.
        """
        with self._lock:
            self._alert_counter += 1
            alert_id = f"alert_{self._alert_counter}"

            alert = UXAlert(
                alert_id=alert_id,
                level=level,
                title=title,
                message=message,
                timestamp=datetime.utcnow(),
                dismissed=False,
                metadata=metadata or {}
            )

            self._alerts.append(alert)

            # Keep only last 100 alerts
            if len(self._alerts) > 100:
                self._alerts = self._alerts[-100:]

            # Persist alerts
            self._persist_alerts()

            return alert_id

    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        dismissed: Optional[bool] = None,
        limit: int = 50
    ) -> List[UXAlert]:
        """
        Get UX alerts with optional filtering.

        Args:
            level: Filter by alert level.
            dismissed: Filter by dismissed status.
            limit: Maximum number of alerts to return.

        Returns:
            List of UXAlerts matching criteria.
        """
        with self._lock:
            filtered = self._alerts.copy()

            if level is not None:
                filtered = [a for a in filtered if a.level == level]

            if dismissed is not None:
                filtered = [a for a in filtered if a.dismissed == dismissed]

            # Return most recent first
            filtered.reverse()

            return filtered[:limit]

    def dismiss_alert(self, alert_id: str) -> bool:
        """
        Dismiss an alert.

        Args:
            alert_id: ID of alert to dismiss.

        Returns:
            True if alert found and dismissed.
        """
        with self._lock:
            for alert in self._alerts:
                if alert.alert_id == alert_id:
                    alert.dismissed = True
                    self._persist_alerts()
                    return True
            return False

    def dismiss_all_alerts(self, level: Optional[AlertLevel] = None) -> int:
        """
        Dismiss all alerts, optionally filtered by level.

        Args:
            level: Optional alert level filter.

        Returns:
            Number of alerts dismissed.
        """
        with self._lock:
            count = 0
            for alert in self._alerts:
                if alert.dismissed:
                    continue
                if level is None or alert.level == level:
                    alert.dismissed = True
                    count += 1

            if count > 0:
                self._persist_alerts()

            return count

    def clear_dismissed_alerts(self) -> int:
        """
        Remove all dismissed alerts.

        Returns:
            Number of alerts removed.
        """
        with self._lock:
            original_count = len(self._alerts)
            self._alerts = [a for a in self._alerts if not a.dismissed]
            removed_count = original_count - len(self._alerts)

            if removed_count > 0:
                self._persist_alerts()

            return removed_count

    def get_alert_summary(self) -> Dict[str, int]:
        """Get summary of active alerts by level."""
        with self._lock:
            active_alerts = [a for a in self._alerts if not a.dismissed]

            return {
                "total": len(active_alerts),
                "info": len([a for a in active_alerts if a.level == AlertLevel.INFO]),
                "warning": len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
                "error": len([a for a in active_alerts if a.level == AlertLevel.ERROR]),
                "critical": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL])
            }

    def set_user_preference(self, key: str, value: Any):
        """
        Set a user preference.

        Args:
            key: Preference key.
            value: Preference value.
        """
        with self._lock:
            if "user_preferences" not in self._state:
                self._state["user_preferences"] = {}

            self._state["user_preferences"][key] = value
            self._persist_state()

    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.

        Args:
            key: Preference key.
            default: Default value if not found.

        Returns:
            Preference value or default.
        """
        with self._lock:
            preferences = self._state.get("user_preferences", {})
            return preferences.get(key, default)

    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences."""
        with self._lock:
            return self._state.get("user_preferences", {}).copy()

    def update_diagnostics_result(self, diagnostics_report: Any):
        """
        Update last diagnostics result.

        Args:
            diagnostics_report: DiagnosticReport object.
        """
        with self._lock:
            # Convert report to dict for storage
            self._state["last_diagnostics"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": diagnostics_report.overall_status.value if hasattr(diagnostics_report.overall_status, 'value') else str(diagnostics_report.overall_status),
                "tests_run": diagnostics_report.tests_run,
                "tests_passed": diagnostics_report.tests_passed,
                "tests_failed": diagnostics_report.tests_failed,
                "warnings": diagnostics_report.warnings,
                "errors": diagnostics_report.errors
            }
            self._persist_state()

    def get_last_diagnostics(self) -> Optional[Dict[str, Any]]:
        """Get last diagnostics result."""
        with self._lock:
            return self._state.get("last_diagnostics")

    def update_system_status(self, status_snapshot: Any):
        """
        Update system status snapshot.

        Args:
            status_snapshot: SystemStatus object from StatusCollector.
        """
        with self._lock:
            # Convert status to dict for storage
            self._state["system_status"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": status_snapshot.overall_health.value if hasattr(status_snapshot.overall_health, 'value') else str(status_snapshot.overall_health),
                "overall_score": status_snapshot.overall_score,
                "active_warnings": status_snapshot.active_warnings,
                "active_errors": status_snapshot.active_errors,
                "modules_count": len(status_snapshot.modules)
            }
            self._persist_state()

    def get_system_status(self) -> Optional[Dict[str, Any]]:
        """Get last system status snapshot."""
        with self._lock:
            return self._state.get("system_status")

    def get_metadata(self) -> Dict[str, Any]:
        """Get UX state metadata."""
        with self._lock:
            return {
                "state_categories": list(self._state.keys()),
                "total_alerts": len(self._alerts),
                "active_alerts": len([a for a in self._alerts if not a.dismissed]),
                "preferences_count": len(self._state.get("user_preferences", {}))
            }

    def reset_state(self):
        """Reset UX state to defaults."""
        with self._lock:
            self._state = {
                "onboarding": {},
                "last_diagnostics": None,
                "system_status": {},
                "user_preferences": {},
                "metadata": {}
            }
            self._alerts = []
            self._alert_counter = 0
            self._persist_state()
            self._persist_alerts()

    def _load_state(self):
        """Load persisted state from FAZA 21."""
        if not self.persistence_manager:
            return

        try:
            # Load main state
            loaded_state = self.persistence_manager.load("ux_state")
            if loaded_state:
                self._state = loaded_state

            # Load alerts
            loaded_alerts = self.persistence_manager.load("ux_alerts")
            if loaded_alerts:
                # Convert dicts back to UXAlert objects
                self._alerts = []
                for alert_data in loaded_alerts.get("alerts", []):
                    alert = UXAlert(
                        alert_id=alert_data["alert_id"],
                        level=AlertLevel(alert_data["level"]),
                        title=alert_data["title"],
                        message=alert_data["message"],
                        timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                        dismissed=alert_data["dismissed"],
                        metadata=alert_data.get("metadata", {})
                    )
                    self._alerts.append(alert)

                self._alert_counter = loaded_alerts.get("counter", 0)
        except Exception:
            # Silently fail if loading fails
            pass

    def _persist_state(self):
        """Persist state to FAZA 21."""
        if not self.persistence_manager:
            return

        try:
            self.persistence_manager.save("ux_state", self._state)
        except Exception:
            # Silently fail if persistence unavailable
            pass

    def _persist_alerts(self):
        """Persist alerts to FAZA 21."""
        if not self.persistence_manager:
            return

        try:
            # Convert alerts to dicts for storage
            alerts_data = {
                "counter": self._alert_counter,
                "alerts": [
                    {
                        "alert_id": a.alert_id,
                        "level": a.level.value,
                        "title": a.title,
                        "message": a.message,
                        "timestamp": a.timestamp.isoformat(),
                        "dismissed": a.dismissed,
                        "metadata": a.metadata
                    }
                    for a in self._alerts
                ]
            }
            self.persistence_manager.save("ux_alerts", alerts_data)
        except Exception:
            # Silently fail if persistence unavailable
            pass


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "ux_state_manager",
        "faza": "20",
        "version": "1.0.0",
        "description": "UX layer state management with FAZA 21 persistence"
    }
