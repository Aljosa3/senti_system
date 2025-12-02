"""
FAZA 19 - Isolation Adapter

Mode for on-premises clients with relay-only communication.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class IsolationMode:
    """Isolation mode enumeration."""
    DIRECT = "direct"  # Direct communication
    RELAY = "relay"  # Relay-only
    ISOLATED = "isolated"  # Fully isolated


class IsolationAdapter:
    """
    Isolation adapter for on-premises deployments.

    Ensures OS is never exposed to internet, only relay communication.
    """

    def __init__(self, mode: str = IsolationMode.RELAY):
        """Initialize isolation adapter."""
        self.mode = mode
        self._relay_queue: List[Dict] = []
        self._allowed_endpoints: List[str] = []

    def set_mode(self, mode: str):
        """Set isolation mode."""
        self.mode = mode

    def is_endpoint_allowed(self, endpoint: str) -> bool:
        """Check if endpoint is allowed."""
        if self.mode == IsolationMode.ISOLATED:
            return False  # No external endpoints in isolated mode

        if self.mode == IsolationMode.RELAY:
            # Only relay endpoints allowed
            return "relay" in endpoint.lower()

        return True  # Direct mode allows all

    def queue_relay_message(self, message: Dict[str, Any]):
        """Queue message for relay."""
        self._relay_queue.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        })

    def get_relay_queue(self) -> List[Dict]:
        """Get relay queue."""
        return self._relay_queue.copy()

    def clear_relay_queue(self):
        """Clear relay queue."""
        self._relay_queue.clear()

    def add_allowed_endpoint(self, endpoint: str):
        """Add allowed endpoint."""
        if endpoint not in self._allowed_endpoints:
            self._allowed_endpoints.append(endpoint)

    def remove_allowed_endpoint(self, endpoint: str):
        """Remove allowed endpoint."""
        if endpoint in self._allowed_endpoints:
            self._allowed_endpoints.remove(endpoint)


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "isolation_adapter",
        "faza": "19",
        "version": "1.0.0",
        "description": "On-premises isolation mode support"
    }
