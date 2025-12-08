#!/usr/bin/env bash

# -----------------------------------------------------------
# SENTI SYSTEM — DAILY INCREMENTAL SNAPSHOT (RSYNC)
# -----------------------------------------------------------

set -e

SOURCE="$HOME/senti_system"
SNAPSHOT_ROOT="$HOME/senti_system_snapshots/daily"

# Create snapshot root if missing
mkdir -p "$SNAPSHOT_ROOT"

TODAY=$(date +"%Y-%m-%d")
TARGET="$SNAPSHOT_ROOT/$TODAY"

# Free disk check
FREE_MB=$(df -Pm / | awk 'NR==2 {print $4}')
if [ "$FREE_MB" -lt 5000 ]; then
    echo "⚠ Premalo prostora (<5GB). Snapshot preskočen."
    exit 0
fi

echo ""
echo "-------------------------------------------"
echo "  SENTI DAILY SNAPSHOT"
echo "-------------------------------------------"
echo "IZVOR:      $SOURCE"
echo "CILJ:       $TARGET"
echo ""

# RSYNC — efficient incremental snapshot
rsync -a --delete \
    --exclude "venv/" \
    --exclude ".git/" \
    --exclude "logs/" \
    --exclude "__pycache__/" \
    --exclude "backups/" \
    "$SOURCE/" "$TARGET/"

echo ""
echo "✓ Snapshot completed: $TARGET"

# ROTACIJA — obdrži zadnjih 7 snapshotov
KEEP=7
COUNT=$(ls -1 "$SNAPSHOT_ROOT" | wc -l)

if [ "$COUNT" -gt "$KEEP" ]; then
    echo "Brisanje starih snapshotov..."
    ls -1t "$SNAPSHOT_ROOT" | tail -n +$((KEEP+1)) | while read -r OLD; do
        rm -rf "$SNAPSHOT_ROOT/$OLD"
        echo "🗑 Izbrisano: $OLD"
    done
fi

echo "-------------------------------------------"
echo "  DAILY SNAPSHOT OK"
echo "-------------------------------------------"
echo ""
