"""
FAZA 19 - Unified Interaction Layer (UIL) & Multi-Device Communication Protocol

This module provides the complete UIL stack for multi-device communication
with zero-trust architecture and GDPR/ZVOP/EU AI Act compliance.

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict

# Device Management
from senti_os.core.faza19.device_identity_manager import (
    DeviceIdentityManager,
    DeviceIdentity,
    DeviceType,
    DeviceStatus
)

from senti_os.core.faza19.device_linking_service import (
    DeviceLinkingService,
    LinkingRequest,
    LinkingStatus
)

# Session & Permissions
from senti_os.core.faza19.session_controller import (
    SessionController,
    DeviceSession,
    SessionStatus
)

from senti_os.core.faza19.permission_manager import (
    PermissionManager,
    Permission
)

# UIL Core
from senti_os.core.faza19.uil_event_bus import (
    UILEventBus,
    UILEvent,
    EventCategory
)

from senti_os.core.faza19.uil_protocol import (
    UILProtocol,
    UILMessage,
    MessageType
)

from senti_os.core.faza19.uil_websocket_server import (
    UILWebSocketServer,
    SimulatedWebSocketConnection
)

# Bridges & APIs
from senti_os.core.faza19.bridge_mobile_controller import MobileBridgeController
from senti_os.core.faza19.local_ui_api import LocalUIAPI
from senti_os.core.faza19.isolation_adapter import (
    IsolationAdapter,
    IsolationMode
)
from senti_os.core.faza19.notification_dispatcher import (
    NotificationDispatcher,
    NotificationPriority
)


# Module exports
__all__ = [
    # Device Management
    "DeviceIdentityManager",
    "DeviceIdentity",
    "DeviceType",
    "DeviceStatus",
    "DeviceLinkingService",
    "LinkingRequest",
    "LinkingStatus",

    # Session & Permissions
    "SessionController",
    "DeviceSession",
    "SessionStatus",
    "PermissionManager",
    "Permission",

    # UIL Core
    "UILEventBus",
    "UILEvent",
    "EventCategory",
    "UILProtocol",
    "UILMessage",
    "MessageType",
    "UILWebSocketServer",
    "SimulatedWebSocketConnection",

    # Bridges & APIs
    "MobileBridgeController",
    "LocalUIAPI",
    "IsolationAdapter",
    "IsolationMode",
    "NotificationDispatcher",
    "NotificationPriority",

    # Main Class
    "FAZA19Stack",

    # Module info
    "get_info"
]


class FAZA19Stack:
    """
    Complete FAZA 19 UIL stack initialization.

    This class provides a single entry point to initialize and manage
    the entire Unified Interaction Layer with all components.
    """

    def __init__(self):
        """Initialize complete FAZA 19 stack."""
        # Device Management
        self.device_identity_manager = DeviceIdentityManager()
        self.device_linking_service = DeviceLinkingService()

        # Session & Permissions
        self.session_controller = SessionController()
        self.permission_manager = PermissionManager()

        # UIL Core
        self.event_bus = UILEventBus()
        self.protocol = UILProtocol()
        self.websocket_server = UILWebSocketServer()

        # Bridges & APIs
        self.mobile_bridge = MobileBridgeController(
            self.permission_manager,
            self.session_controller
        )
        self.local_ui_api = LocalUIAPI(
            self.event_bus,
            self.permission_manager
        )
        self.isolation_adapter = IsolationAdapter()
        self.notification_dispatcher = NotificationDispatcher()

    def start(self):
        """Start all UIL services."""
        self.websocket_server.start()

    def stop(self):
        """Stop all UIL services."""
        self.websocket_server.stop()

    def get_stack_status(self) -> Dict:
        """Get status of all stack components."""
        return {
            "device_manager": {
                "total_devices": len(self.device_identity_manager._devices),
                "active_devices": len(self.device_identity_manager.get_active_devices())
            },
            "session_controller": {
                "total_sessions": len(self.session_controller._sessions)
            },
            "websocket_server": {
                "active_connections": len(self.websocket_server.get_active_connections())
            },
            "event_bus": {
                "event_count": len(self.event_bus._event_history)
            }
        }


def get_info() -> Dict[str, str]:
    """
    Get FAZA 19 module information.

    Returns:
        Dictionary with comprehensive module metadata.
    """
    return {
        "module": "faza19",
        "name": "Unified Interaction Layer (UIL) & Multi-Device Communication Protocol",
        "version": "1.0.0",
        "faza": "19",
        "description": (
            "Multi-device communication protocol with zero-trust architecture"
        ),

        # Privacy Guarantees
        "privacy_compliant": "true",
        "gdpr_compliant": "true",
        "zvop_compliant": "true",
        "eu_ai_act_compliant": "true",

        # Critical Privacy Rules
        "processes_biometrics": "false",
        "stores_biometrics": "false",
        "authentication_method": "cryptographic_keys_only",

        # Capabilities
        "supports_multi_device": "true",
        "supports_device_linking": "true",
        "supports_session_management": "true",
        "supports_permission_management": "true",
        "supports_event_bus": "true",
        "supports_websocket": "true",
        "supports_isolation_mode": "true",

        # Components
        "components": {
            "device_identity_manager": "Multi-device identity management",
            "device_linking_service": "Secure device pairing with QR code",
            "session_controller": "Multi-device session management",
            "permission_manager": "Per-device permission enforcement",
            "uil_event_bus": "Publish/subscribe event bus",
            "uil_protocol": "JSON message protocol",
            "uil_websocket_server": "Simulated WebSocket server",
            "bridge_mobile_controller": "Mobile command validation",
            "local_ui_api": "Local-only UI interface",
            "isolation_adapter": "On-premises isolation mode",
            "notification_dispatcher": "Real-time notification distribution"
        },

        # Architecture
        "architecture": "zero_trust",
        "approach": "cryptographic_verification",
        "communication": "bidirectional_streaming",

        # Contact
        "author": "SENTI OS Core Team",
        "license": "Proprietary"
    }


# Version info
__version__ = "1.0.0"
__author__ = "SENTI OS Core Team"
__license__ = "Proprietary"
