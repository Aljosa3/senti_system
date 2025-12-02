"""
FAZA 19 - Notification Dispatcher

Real-time event distribution with push simulation, logging, and throttling.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict


class NotificationPriority:
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationDispatcher:
    """
    Dispatches notifications to devices with throttling and priority management.
    """

    def __init__(self, throttle_window_seconds: int = 60):
        """Initialize notification dispatcher."""
        self.throttle_window_seconds = throttle_window_seconds
        self._subscriptions: Dict[str, Set[str]] = defaultdict(set)  # device -> notification types
        self._notification_log: List[Dict] = []
        self._throttle_counts: Dict[str, List[datetime]] = defaultdict(list)
        self._max_per_window = 10  # Max notifications per device per window

    def subscribe(self, device_id: str, notification_types: List[str]):
        """Subscribe device to notification types."""
        for notif_type in notification_types:
            self._subscriptions[device_id].add(notif_type)

    def unsubscribe(self, device_id: str, notification_types: List[str]):
        """Unsubscribe device from notification types."""
        for notif_type in notification_types:
            self._subscriptions[device_id].discard(notif_type)

    def dispatch(
        self,
        notification_type: str,
        message: str,
        priority: str = NotificationPriority.NORMAL,
        target_devices: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Dispatch notification to subscribed devices.

        Args:
            notification_type: Type of notification.
            message: Notification message.
            priority: Priority level.
            target_devices: Optional specific devices, otherwise all subscribed.

        Returns:
            Dict mapping device_id to success boolean.
        """
        results = {}

        # Determine target devices
        if target_devices:
            devices = target_devices
        else:
            # All devices subscribed to this type
            devices = [
                dev_id for dev_id, types in self._subscriptions.items()
                if notification_type in types
            ]

        # Dispatch to each device
        for device_id in devices:
            # Check throttle
            if priority != NotificationPriority.URGENT:
                if not self._check_throttle(device_id):
                    results[device_id] = False
                    continue

            # Send notification (simulated)
            self._send_notification(device_id, notification_type, message, priority)
            results[device_id] = True

        return results

    def _check_throttle(self, device_id: str) -> bool:
        """Check if device is within throttle limits."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.throttle_window_seconds)

        # Clean old entries
        self._throttle_counts[device_id] = [
            ts for ts in self._throttle_counts[device_id]
            if ts > window_start
        ]

        # Check count
        if len(self._throttle_counts[device_id]) >= self._max_per_window:
            return False

        # Add current
        self._throttle_counts[device_id].append(now)
        return True

    def _send_notification(
        self,
        device_id: str,
        notification_type: str,
        message: str,
        priority: str
    ):
        """Send notification (simulated)."""
        self._notification_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": device_id,
            "notification_type": notification_type,
            "message": message,
            "priority": priority
        })

    def get_notification_log(
        self,
        device_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get notification log."""
        logs = self._notification_log
        if device_id:
            logs = [log for log in logs if log["device_id"] == device_id]
        return logs[-limit:]


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "notification_dispatcher",
        "faza": "19",
        "version": "1.0.0",
        "description": "Real-time notification distribution with throttling"
    }
