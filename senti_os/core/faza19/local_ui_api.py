"""
FAZA 19 - Local UI API

Local-only interface for pipeline events.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, Any, List, Optional


class LocalUIAPI:
    """Local-only API for UI interactions."""

    def __init__(self, event_bus, permission_manager):
        """Initialize local UI API."""
        self.event_bus = event_bus
        self.permission_manager = permission_manager

    def get_status(self, device_id: str) -> Dict[str, Any]:
        """Get system status."""
        from senti_os.core.faza19.permission_manager import Permission

        if not self.permission_manager.has_permission(device_id, Permission.READ_STATUS):
            return {"error": "Permission denied"}

        return {
            "status": "active",
            "uptime": "24h",
            "connected_devices": 3
        }

    def list_tasks(self, device_id: str) -> List[Dict[str, Any]]:
        """List tasks."""
        from senti_os.core.faza19.permission_manager import Permission

        if not self.permission_manager.has_permission(device_id, Permission.EXECUTE_TASK):
            return []

        return [
            {"task_id": "task_1", "status": "running"},
            {"task_id": "task_2", "status": "completed"}
        ]

    def execute_task(
        self,
        device_id: str,
        task_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute task."""
        from senti_os.core.faza19.permission_manager import Permission

        if not self.permission_manager.has_permission(device_id, Permission.EXECUTE_TASK):
            return {"error": "Permission denied", "success": False}

        return {
            "success": True,
            "task_id": "task_new",
            "task_name": task_name
        }


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "local_ui_api",
        "faza": "19",
        "version": "1.0.0",
        "description": "Local-only UI interface"
    }
