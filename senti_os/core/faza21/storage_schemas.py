"""
FAZA 21 - Storage Schemas

Defines data schemas for all persistent storage files.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, Any, List
from datetime import datetime


class StorageSchemas:
    """
    Defines schemas for all persistent storage files.

    Each schema specifies the structure of JSON data that will be
    encrypted and stored.
    """

    @staticmethod
    def devices_schema() -> Dict[str, Any]:
        """
        Schema for devices.json

        Stores device identities from FAZA 19.
        """
        return {
            "schema_version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "devices": []  # List of device identity objects
        }

    @staticmethod
    def permissions_schema() -> Dict[str, Any]:
        """
        Schema for permissions.json

        Stores per-device permissions from FAZA 19.
        """
        return {
            "schema_version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "permissions": {}  # Dict: device_id -> list of permissions
        }

    @staticmethod
    def sessions_schema() -> Dict[str, Any]:
        """
        Schema for sessions.json

        Stores active sessions from FAZA 19.
        NO PASSWORDS - only session tokens.
        """
        return {
            "schema_version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "sessions": []  # List of session objects
        }

    @staticmethod
    def settings_schema() -> Dict[str, Any]:
        """
        Schema for settings.json

        Stores SENTI OS settings and preferences.
        """
        return {
            "schema_version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "settings": {
                "system": {},
                "ui": {},
                "security": {},
                "privacy": {}
            }
        }

    @staticmethod
    def orch_history_schema() -> Dict[str, Any]:
        """
        Schema for orch_history.json

        Stores orchestration history from FAZA 17.
        """
        return {
            "schema_version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "workflows": [],
            "executions": []
        }

    @staticmethod
    def oauth_tokens_schema() -> Dict[str, Any]:
        """
        Schema for oauth_tokens.json

        Stores OAuth tokens (NOT passwords).
        """
        return {
            "schema_version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "tokens": []  # List of OAuth token objects
        }

    @staticmethod
    def platform_sessions_schema() -> Dict[str, Any]:
        """
        Schema for platform_sessions.json

        Stores platform session tokens from FAZA 18.
        NO PASSWORDS - only session tokens.
        """
        return {
            "schema_version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "platform_sessions": []  # List of platform session objects
        }

    @staticmethod
    def get_all_schemas() -> Dict[str, callable]:
        """
        Get all schema generators.

        Returns:
            Dict mapping filename to schema generator function.
        """
        return {
            "devices.json": StorageSchemas.devices_schema,
            "permissions.json": StorageSchemas.permissions_schema,
            "sessions.json": StorageSchemas.sessions_schema,
            "settings.json": StorageSchemas.settings_schema,
            "orch_history.json": StorageSchemas.orch_history_schema,
            "oauth_tokens.json": StorageSchemas.oauth_tokens_schema,
            "platform_sessions.json": StorageSchemas.platform_sessions_schema
        }

    @staticmethod
    def validate_schema(filename: str, data: Dict[str, Any]) -> bool:
        """
        Validate data against schema.

        Args:
            filename: Schema filename.
            data: Data to validate.

        Returns:
            True if valid.
        """
        if "schema_version" not in data:
            return False
        if "last_updated" not in data:
            return False

        # Filename-specific validation
        if filename == "devices.json":
            return "devices" in data and isinstance(data["devices"], list)
        elif filename == "permissions.json":
            return "permissions" in data and isinstance(data["permissions"], dict)
        elif filename == "sessions.json":
            return "sessions" in data and isinstance(data["sessions"], list)
        elif filename == "settings.json":
            return "settings" in data and isinstance(data["settings"], dict)
        elif filename == "orch_history.json":
            return "workflows" in data and "executions" in data
        elif filename == "oauth_tokens.json":
            return "tokens" in data and isinstance(data["tokens"], list)
        elif filename == "platform_sessions.json":
            return "platform_sessions" in data and isinstance(data["platform_sessions"], list)

        return False


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "storage_schemas",
        "faza": "21",
        "version": "1.0.0",
        "description": "Data schemas for persistent storage",
        "stores_passwords": "false",
        "stores_biometrics": "false"
    }
