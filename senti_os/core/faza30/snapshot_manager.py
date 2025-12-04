"""
FAZA 30 – Snapshot Manager

System state snapshot and rollback management.

Provides:
- State snapshot creation
- Snapshot restoration (rollback)
- Snapshot persistence to disk
- Snapshot history and cleanup
- Snapshot verification

Architecture:
    Snapshot - Snapshot metadata and state
    SnapshotManager - Main snapshot controller

Usage:
    from senti_os.core.faza30.snapshot_manager import SnapshotManager

    manager = SnapshotManager(snapshot_dir="~/.senti_system/snapshots/")
    snapshot_id = manager.create_snapshot(snapshot_type="pre_repair")
    manager.restore_snapshot(snapshot_id)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import os
import shutil


class SnapshotType(Enum):
    """Type of snapshot."""
    PRE_REPAIR = "pre_repair"           # Before repair attempt
    SCHEDULED = "scheduled"             # Scheduled backup
    MANUAL = "manual"                   # Manual user snapshot
    EMERGENCY = "emergency"             # Emergency snapshot
    CHECKPOINT = "checkpoint"           # System checkpoint


@dataclass
class Snapshot:
    """
    System state snapshot.

    Attributes:
        snapshot_id: Unique snapshot identifier
        snapshot_type: Type of snapshot
        timestamp: When snapshot was created
        state: Captured system state
        metadata: Additional snapshot metadata
        file_path: Path to snapshot file
        size_bytes: Snapshot size in bytes
        verified: Whether snapshot is verified
    """
    snapshot_id: str
    snapshot_type: SnapshotType
    timestamp: datetime
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    size_bytes: int = 0
    verified: bool = False


class SnapshotManager:
    """
    Snapshot manager for system state capture and restoration.

    Features:
    - Create snapshots of system state
    - Persist snapshots to disk
    - Restore from snapshots (rollback)
    - Snapshot history management
    - Automatic cleanup of old snapshots
    - Snapshot verification

    Snapshots are stored in: ~/.senti_system/snapshots/
    """

    def __init__(
        self,
        snapshot_dir: Optional[str] = None,
        max_snapshots: int = 50,
        auto_cleanup: bool = True
    ):
        """
        Initialize snapshot manager.

        Args:
            snapshot_dir: Directory for snapshots (default: ~/.senti_system/snapshots/)
            max_snapshots: Maximum snapshots to keep
            auto_cleanup: Automatically cleanup old snapshots
        """
        if snapshot_dir is None:
            home = Path.home()
            snapshot_dir = home / ".senti_system" / "snapshots"
        else:
            snapshot_dir = Path(snapshot_dir).expanduser()

        self.snapshot_dir = snapshot_dir
        self.max_snapshots = max_snapshots
        self.auto_cleanup = auto_cleanup

        # Create snapshot directory
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        self._snapshots: Dict[str, Snapshot] = {}
        self._load_snapshots()

        self._stats = {
            "total_created": 0,
            "total_restored": 0,
            "total_deleted": 0,
            "failed_creates": 0,
            "failed_restores": 0
        }

    def create_snapshot(
        self,
        snapshot_type: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
        state_override: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new system state snapshot.

        Args:
            snapshot_type: Type of snapshot
            metadata: Optional snapshot metadata
            state_override: Optional state dict (otherwise captures current state)

        Returns:
            Snapshot ID
        """
        timestamp = datetime.now()
        snapshot_id = f"snap_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond}"

        try:
            # Capture state
            if state_override is not None:
                state = state_override
            else:
                state = self._capture_state()

            # Create snapshot
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                snapshot_type=SnapshotType(snapshot_type) if isinstance(snapshot_type, str) else snapshot_type,
                timestamp=timestamp,
                state=state,
                metadata=metadata or {}
            )

            # Persist to disk
            file_path = self._persist_snapshot(snapshot)
            snapshot.file_path = str(file_path)
            snapshot.size_bytes = file_path.stat().st_size

            # Verify snapshot
            snapshot.verified = self._verify_snapshot(snapshot)

            # Store in memory
            self._snapshots[snapshot_id] = snapshot

            # Auto cleanup if enabled
            if self.auto_cleanup:
                self._cleanup_old_snapshots()

            self._stats["total_created"] += 1

            return snapshot_id

        except Exception as e:
            self._stats["failed_creates"] += 1
            raise RuntimeError(f"Failed to create snapshot: {e}")

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore system from snapshot.

        Args:
            snapshot_id: ID of snapshot to restore

        Returns:
            True if restore successful, False otherwise
        """
        if snapshot_id not in self._snapshots:
            # Try loading from disk
            self._load_snapshot(snapshot_id)

        if snapshot_id not in self._snapshots:
            self._stats["failed_restores"] += 1
            return False

        try:
            snapshot = self._snapshots[snapshot_id]

            # Verify snapshot before restore
            if not snapshot.verified:
                if not self._verify_snapshot(snapshot):
                    self._stats["failed_restores"] += 1
                    return False

            # Restore state
            self._restore_state(snapshot.state)

            self._stats["total_restored"] += 1
            return True

        except Exception as e:
            self._stats["failed_restores"] += 1
            return False

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """
        Delete a snapshot.

        Args:
            snapshot_id: Snapshot to delete

        Returns:
            True if deleted, False otherwise
        """
        if snapshot_id not in self._snapshots:
            return False

        try:
            snapshot = self._snapshots[snapshot_id]

            # Delete file
            if snapshot.file_path:
                file_path = Path(snapshot.file_path)
                if file_path.exists():
                    file_path.unlink()

            # Remove from memory
            del self._snapshots[snapshot_id]

            self._stats["total_deleted"] += 1
            return True

        except Exception:
            return False

    def list_snapshots(self, snapshot_type: Optional[str] = None) -> List[Snapshot]:
        """
        List all snapshots.

        Args:
            snapshot_type: Optional filter by type

        Returns:
            List of snapshots
        """
        snapshots = list(self._snapshots.values())

        if snapshot_type:
            snapshots = [s for s in snapshots if s.snapshot_type.value == snapshot_type]

        # Sort by timestamp (newest first)
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)

        return snapshots

    def get_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Get snapshot by ID."""
        return self._snapshots.get(snapshot_id)

    def get_latest_snapshot(self, snapshot_type: Optional[str] = None) -> Optional[Snapshot]:
        """Get most recent snapshot."""
        snapshots = self.list_snapshots(snapshot_type)
        return snapshots[0] if snapshots else None

    def _capture_state(self) -> Dict[str, Any]:
        """
        Capture current system state.

        In a real implementation, this would capture:
        - Task graph state
        - Agent states
        - Orchestrator state
        - Configuration
        - Runtime parameters
        """
        state = {
            "timestamp": datetime.now().isoformat(),
            "task_graph": self._capture_task_graph_state(),
            "agents": self._capture_agent_state(),
            "orchestrator": self._capture_orchestrator_state(),
            "governance": self._capture_governance_state(),
            "config": self._capture_config_state()
        }

        return state

    def _capture_task_graph_state(self) -> Dict[str, Any]:
        """Capture task graph state."""
        # Placeholder - in real implementation would capture actual graph
        return {
            "nodes": [],
            "edges": [],
            "metadata": {}
        }

    def _capture_agent_state(self) -> Dict[str, Any]:
        """Capture agent execution state."""
        # Placeholder - in real implementation would capture agent states
        return {
            "active_agents": [],
            "agent_metadata": {}
        }

    def _capture_orchestrator_state(self) -> Dict[str, Any]:
        """Capture orchestrator state."""
        # Placeholder - in real implementation would capture orchestrator state
        return {
            "queue_state": [],
            "scheduler_state": {}
        }

    def _capture_governance_state(self) -> Dict[str, Any]:
        """Capture governance state."""
        # Placeholder - in real implementation would capture governance state
        return {
            "policies": {},
            "overrides": []
        }

    def _capture_config_state(self) -> Dict[str, Any]:
        """Capture configuration state."""
        # Placeholder - in real implementation would capture config
        return {
            "settings": {}
        }

    def _restore_state(self, state: Dict[str, Any]) -> None:
        """
        Restore system state from snapshot.

        In a real implementation, this would restore:
        - Task graph
        - Agent states
        - Orchestrator state
        - Configuration
        """
        # Placeholder - in real implementation would restore state
        pass

    def _persist_snapshot(self, snapshot: Snapshot) -> Path:
        """Persist snapshot to disk."""
        file_path = self.snapshot_dir / f"{snapshot.snapshot_id}.json"

        snapshot_data = {
            "snapshot_id": snapshot.snapshot_id,
            "snapshot_type": snapshot.snapshot_type.value,
            "timestamp": snapshot.timestamp.isoformat(),
            "state": snapshot.state,
            "metadata": snapshot.metadata
        }

        with open(file_path, 'w') as f:
            json.dump(snapshot_data, f, indent=2)

        return file_path

    def _load_snapshots(self) -> None:
        """Load all snapshots from disk."""
        if not self.snapshot_dir.exists():
            return

        for file_path in self.snapshot_dir.glob("snap_*.json"):
            try:
                snapshot_id = file_path.stem
                self._load_snapshot(snapshot_id)
            except Exception:
                # Skip corrupted snapshots
                continue

    def _load_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Load a single snapshot from disk."""
        file_path = self.snapshot_dir / f"{snapshot_id}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            snapshot = Snapshot(
                snapshot_id=data["snapshot_id"],
                snapshot_type=SnapshotType(data["snapshot_type"]),
                timestamp=datetime.fromisoformat(data["timestamp"]),
                state=data["state"],
                metadata=data.get("metadata", {}),
                file_path=str(file_path),
                size_bytes=file_path.stat().st_size,
                verified=True
            )

            self._snapshots[snapshot_id] = snapshot
            return snapshot

        except Exception:
            return None

    def _verify_snapshot(self, snapshot: Snapshot) -> bool:
        """Verify snapshot integrity."""
        # Basic verification - check if file exists and is readable
        if snapshot.file_path:
            file_path = Path(snapshot.file_path)
            if not file_path.exists():
                return False

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return "snapshot_id" in data and "state" in data
            except Exception:
                return False

        return True

    def _cleanup_old_snapshots(self) -> None:
        """Remove old snapshots to stay within max_snapshots limit."""
        snapshots = self.list_snapshots()

        if len(snapshots) > self.max_snapshots:
            # Keep newest snapshots, delete oldest
            to_delete = snapshots[self.max_snapshots:]

            for snapshot in to_delete:
                self.delete_snapshot(snapshot.snapshot_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get snapshot manager statistics."""
        total_size = sum(s.size_bytes for s in self._snapshots.values())

        return {
            **self._stats,
            "current_snapshots": len(self._snapshots),
            "total_size_bytes": total_size,
            "snapshot_dir": str(self.snapshot_dir)
        }

    def cleanup_all(self) -> int:
        """
        Delete all snapshots.

        Returns:
            Number of snapshots deleted
        """
        count = 0
        snapshot_ids = list(self._snapshots.keys())

        for snapshot_id in snapshot_ids:
            if self.delete_snapshot(snapshot_id):
                count += 1

        return count


def create_snapshot_manager(
    snapshot_dir: Optional[str] = None,
    max_snapshots: int = 50,
    auto_cleanup: bool = True
) -> SnapshotManager:
    """
    Factory function to create SnapshotManager.

    Args:
        snapshot_dir: Directory for snapshots
        max_snapshots: Maximum snapshots to keep
        auto_cleanup: Enable automatic cleanup

    Returns:
        Initialized SnapshotManager instance
    """
    return SnapshotManager(
        snapshot_dir=snapshot_dir,
        max_snapshots=max_snapshots,
        auto_cleanup=auto_cleanup
    )
