#!/usr/bin/env bash

# -----------------------------------------------------------
# SENTI SYSTEM — WEEKLY FULL ZIP BACKUP
# -----------------------------------------------------------

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"

mkdir -p "$BACKUP_DIR"

# Disk check
FREE_MB=$(df -Pm / | awk 'NR==2 {print $4}')
if [ "$FREE_MB" -lt 10000 ]; then
    echo "⚠ Premalo prostora (<10GB). Full backup preskočen."
    exit 0
fi

TIMESTAMP=$(date +"%Y-%m-%d")
BACKUP_NAME="full_backup_$TIMESTAMP.zip"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo ""
echo "-------------------------------------------"
echo "   SENTI SYSTEM — FULL WEEKLY ZIP BACKUP"
echo "-------------------------------------------"
echo "Shranjujem v: $BACKUP_PATH"
echo ""

cd "$(dirname "$PROJECT_ROOT")"

# ZIP (optimized)
zip -r "$BACKUP_PATH" "$(basename "$PROJECT_ROOT")" \
    -x "*/venv/*" \
       "*/.git/*" \
       "*/__pycache__/*" \
       "*/logs/*" \
       "*/backups/*" \
       "*.env" \
       "*.log" \
       "*.tmp" \
       "*.pyc"

echo "✓ ZIP created"

# ROTACIJA — obdrži zadnje 4 ZIP-e
KEEP=4
COUNT=$(ls -1 "$BACKUP_DIR"/*.zip 2>/dev/null | wc -l)

if [ "$COUNT" -gt "$KEEP" ]; then
    echo "Brisanje starih ZIP backupov..."
    ls -1t "$BACKUP_DIR"/*.zip | tail -n +$((KEEP+1)) | while read -r OLD; do
        rm "$OLD"
        echo "🗑 Izbrisano: $OLD"
    done
fi

echo ""
echo "-------------------------------------------"
echo "   WEEKLY FULL BACKUP OK"
echo "-------------------------------------------"
echo ""
