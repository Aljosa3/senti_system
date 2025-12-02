"""
FAZA 19 - Mobile Bridge Controller

Validates incoming commands from mobile devices and enforces permissions.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class MobileBridgeController:
    """
    Mobile bridge controller with permission enforcement.

    Validates all commands from mobile devices before forwarding to core.
    """

    def __init__(self, permission_manager, session_controller):
        """Initialize mobile bridge controller."""
        self.permission_manager = permission_manager
        self.session_controller = session_controller
        self._command_history: List[Dict] = []

    def validate_and_execute(
        self,
        session_token: str,
        command: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate command and execute if authorized.

        Args:
            session_token: Device session token.
            command: Command to execute.
            params: Command parameters.

        Returns:
            Execution result or error.
        """
        # Validate session
        session = self.session_controller.validate_session(session_token)
        if not session:
            return {"error": "Invalid or expired session", "success": False}

        # Check permissions
        from senti_os.core.faza19.permission_manager import Permission

        required_permission = self._get_required_permission(command)
        if not self.permission_manager.has_permission(
            session.device_id,
            required_permission
        ):
            return {
                "error": f"Permission denied: {required_permission.value}",
                "success": False
            }

        # Log command
        self._log_command(session.device_id, command, params)

        # Execute command
        return self._execute_command(command, params, session.device_id)

    def _get_required_permission(self, command: str):
        """Get required permission for command."""
        from senti_os.core.faza19.permission_manager import Permission

        command_permissions = {
            "read_status": Permission.READ_STATUS,
            "execute_task": Permission.EXECUTE_TASK,
            "read_files": Permission.READ_FILES,
            "write_files": Permission.WRITE_FILES,
            "manage_devices": Permission.MANAGE_DEVICES,
            "view_logs": Permission.VIEW_LOGS
        }
        return command_permissions.get(command, Permission.ADMIN)

    def _execute_command(
        self,
        command: str,
        params: Dict[str, Any],
        device_id: str
    ) -> Dict[str, Any]:
        """Execute validated command."""
        # Simulate command execution
        return {
            "success": True,
            "command": command,
            "result": f"Command {command} executed",
            "device_id": device_id
        }

    def _log_command(self, device_id: str, command: str, params: Dict):
        """Log command execution."""
        self._command_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": device_id,
            "command": command,
            "params": params
        })

    def get_command_history(self, device_id: Optional[str] = None) -> List[Dict]:
        """Get command history."""
        if device_id:
            return [
                cmd for cmd in self._command_history
                if cmd["device_id"] == device_id
            ]
        return self._command_history


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "bridge_mobile_controller",
        "faza": "19",
        "version": "1.0.0",
        "description": "Mobile command validation and permission enforcement"
    }
