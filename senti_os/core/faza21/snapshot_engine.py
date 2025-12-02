"""
FAZA 21 - Snapshot Engine

Daily snapshots, manual snapshots, and rollback functionality.

Author: SENTI OS Core Team
License: Proprietary
"""

import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Snapshot:
    """Represents a storage snapshot."""
    snapshot_id: str
    created_at: datetime
    snapshot_type: str  # "manual" or "automatic"
    file_count: int
    total_size: int


class SnapshotEngine:
    """
    Manages storage snapshots for backup and rollback.

    Provides daily automatic snapshots and manual snapshots.
    """

    def __init__(self, storage_backend):
        """
        Initialize snapshot engine.

        Args:
            storage_backend: StorageBackendFS instance.
        """
        self.storage_backend = storage_backend
        self.snapshots_dir = Path(storage_backend.storage_dir) / ".snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self._snapshots: List[Snapshot] = []
        self._load_snapshot_index()

    def create_snapshot(self, snapshot_type: str = "manual") -> Optional[str]:
        """
        Create a new snapshot.

        Args:
            snapshot_type: "manual" or "automatic".

        Returns:
            Snapshot ID if successful, None otherwise.
        """
        try:
            snapshot_id = self._generate_snapshot_id()
            snapshot_path = self.snapshots_dir / snapshot_id

            # Copy all files to snapshot directory
            snapshot_path.mkdir(parents=True, exist_ok=True)

            file_count = 0
            total_size = 0

            for filename in self.storage_backend.list_files():
                src = self.storage_backend.storage_dir / filename
                dst = snapshot_path / filename

                if src.exists():
                    shutil.copy2(src, dst)
                    file_count += 1
                    total_size += src.stat().st_size

            # Create snapshot record
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                created_at=datetime.utcnow(),
                snapshot_type=snapshot_type,
                file_count=file_count,
                total_size=total_size
            )

            self._snapshots.append(snapshot)
            self._save_snapshot_index()

            return snapshot_id
        except Exception:
            return None

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore from a snapshot.

        Args:
            snapshot_id: Snapshot to restore from.

        Returns:
            True if restored successfully.
        """
        try:
            snapshot_path = self.snapshots_dir / snapshot_id

            if not snapshot_path.exists():
                return False

            # Backup current state before restoring
            backup_id = self.create_snapshot("pre_restore_backup")

            # Clear current storage
            for filename in self.storage_backend.list_files():
                self.storage_backend.delete(filename)

            # Restore files from snapshot
            for src_file in snapshot_path.iterdir():
                if src_file.is_file():
                    dst = self.storage_backend.storage_dir / src_file.name
                    shutil.copy2(src_file, dst)

            return True
        except Exception:
            return False

    def list_snapshots(self) -> List[Snapshot]:
        """List all available snapshots."""
        return sorted(self._snapshots, key=lambda s: s.created_at, reverse=True)

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot."""
        try:
            snapshot_path = self.snapshots_dir / snapshot_id

            if snapshot_path.exists():
                shutil.rmtree(snapshot_path)

            self._snapshots = [s for s in self._snapshots if s.snapshot_id != snapshot_id]
            self._save_snapshot_index()

            return True
        except Exception:
            return False

    def cleanup_old_snapshots(self, keep_count: int = 10) -> int:
        """
        Clean up old snapshots, keeping most recent.

        Args:
            keep_count: Number of snapshots to keep.

        Returns:
            Number of snapshots deleted.
        """
        snapshots = self.list_snapshots()

        if len(snapshots) <= keep_count:
            return 0

        to_delete = snapshots[keep_count:]
        count = 0

        for snapshot in to_delete:
            if self.delete_snapshot(snapshot.snapshot_id):
                count += 1

        return count

    def get_snapshot_info(self, snapshot_id: str) -> Optional[Snapshot]:
        """Get snapshot information."""
        for snapshot in self._snapshots:
            if snapshot.snapshot_id == snapshot_id:
                return snapshot
        return None

    def _generate_snapshot_id(self) -> str:
        """Generate unique snapshot ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        return f"snapshot_{timestamp}"

    def _save_snapshot_index(self):
        """Save snapshot index."""
        try:
            index_path = self.snapshots_dir / "index.json"
            import json

            data = {
                "snapshots": [
                    {
                        "snapshot_id": s.snapshot_id,
                        "created_at": s.created_at.isoformat(),
                        "snapshot_type": s.snapshot_type,
                        "file_count": s.file_count,
                        "total_size": s.total_size
                    }
                    for s in self._snapshots
                ]
            }

            with open(index_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load_snapshot_index(self):
        """Load snapshot index."""
        try:
            index_path = self.snapshots_dir / "index.json"
            if not index_path.exists():
                return

            import json
            with open(index_path, 'r') as f:
                data = json.load(f)

            for snapshot_data in data.get("snapshots", []):
                snapshot = Snapshot(
                    snapshot_id=snapshot_data["snapshot_id"],
                    created_at=datetime.fromisoformat(snapshot_data["created_at"]),
                    snapshot_type=snapshot_data["snapshot_type"],
                    file_count=snapshot_data["file_count"],
                    total_size=snapshot_data["total_size"]
                )
                self._snapshots.append(snapshot)
        except Exception:
            pass


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "snapshot_engine",
        "faza": "21",
        "version": "1.0.0",
        "description": "Snapshot and rollback functionality"
    }
