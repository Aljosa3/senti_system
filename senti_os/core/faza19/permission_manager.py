"""
FAZA 19 - Permission Manager

Per-device permission management with safe defaults and enforcement.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, List, Set, Optional
from enum import Enum


class Permission(Enum):
    """Device permissions."""
    READ_STATUS = "read_status"
    EXECUTE_TASK = "execute_task"
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    MANAGE_DEVICES = "manage_devices"
    VIEW_LOGS = "view_logs"
    ADMIN = "admin"


class PermissionManager:
    """Manages per-device permissions with safe defaults."""

    DEFAULT_PERMISSIONS = {Permission.READ_STATUS}

    def __init__(self):
        """Initialize permission manager."""
        self._device_permissions: Dict[str, Set[Permission]] = {}

    def grant_permission(self, device_id: str, permission: Permission) -> bool:
        """Grant permission to device."""
        if device_id not in self._device_permissions:
            self._device_permissions[device_id] = self.DEFAULT_PERMISSIONS.copy()
        self._device_permissions[device_id].add(permission)
        return True

    def revoke_permission(self, device_id: str, permission: Permission) -> bool:
        """Revoke permission from device."""
        if device_id in self._device_permissions:
            self._device_permissions[device_id].discard(permission)
            return True
        return False

    def has_permission(self, device_id: str, permission: Permission) -> bool:
        """Check if device has permission."""
        if device_id not in self._device_permissions:
            return permission in self.DEFAULT_PERMISSIONS

        # Admin has all permissions
        if Permission.ADMIN in self._device_permissions[device_id]:
            return True

        return permission in self._device_permissions[device_id]

    def get_permissions(self, device_id: str) -> Set[Permission]:
        """Get all permissions for device."""
        if device_id not in self._device_permissions:
            return self.DEFAULT_PERMISSIONS.copy()
        return self._device_permissions[device_id].copy()

    def set_permissions(self, device_id: str, permissions: Set[Permission]) -> bool:
        """Set permissions for device."""
        self._device_permissions[device_id] = permissions
        return True

    def reset_to_default(self, device_id: str) -> bool:
        """Reset device permissions to default."""
        self._device_permissions[device_id] = self.DEFAULT_PERMISSIONS.copy()
        return True

    def is_admin(self, device_id: str) -> bool:
        """Check if device has admin permission."""
        return self.has_permission(device_id, Permission.ADMIN)


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "permission_manager",
        "faza": "19",
        "version": "1.0.0",
        "description": "Per-device permission management"
    }
