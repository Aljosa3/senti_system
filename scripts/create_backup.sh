#!/usr/bin/env bash

# -----------------------------------------------------------
# SENTI SYSTEM — AUTOMATIC BACKUP SCRIPT (NO EMAIL VERSION)
# -----------------------------------------------------------

set -e

# Resolve script directory safely
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR="$PROJECT_ROOT/backups"
NEXTCLOUD_DIR="$HOME/Nextcloud/Senti_Backups"

# Ensure directories exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$NEXTCLOUD_DIR"

# Timestamp + backup filename
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
REASON="${1:-manual}"
BACKUP_NAME="${TIMESTAMP}_senti_backup__${REASON}.zip"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo "-------------------------------------------"
echo "   SENTI SYSTEM — Backup Started"
echo "-------------------------------------------"
echo "Project root:     $PROJECT_ROOT"
echo "Backup name:      $BACKUP_NAME"
echo ""

# Go to parent of project root
cd "$(dirname "$PROJECT_ROOT")"

# ZIP — exclude unnecessary/sensitive files
zip -r "$BACKUP_PATH" "$(basename "$PROJECT_ROOT")" \
    -x "*/__pycache__/*" \
       "*/.git/*" \
       "*.env" \
       "*API*" \
       "*KEY*" \
       "*.pem" \
       "*.log" \
       "*cache*" \
       "*.tmp"

# Create SHA256 checksum
HASH_FILE="${BACKUP_PATH}.sha256"
shasum -a 256 "$BACKUP_PATH" > "$HASH_FILE"

# Copy to Nextcloud
cp "$BACKUP_PATH" "$NEXTCLOUD_DIR"
cp "$HASH_FILE" "$NEXTCLOUD_DIR"

# -----------------------------------------------------------
# AUTO-CLEAN — KEEP ONLY LAST 30 BACKUPS
# -----------------------------------------------------------
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.zip 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -gt 30 ]; then
    echo "Cleaning old backups (keeping last 30)..."
    ls -1t "$BACKUP_DIR"/*.zip | tail -n +31 | while read -r OLD_BACKUP; do
        echo "Deleting: $OLD_BACKUP"
        rm "$OLD_BACKUP"
        rm "${OLD_BACKUP}.sha256" 2>/dev/null
    done
fi

echo ""
echo "-------------------------------------------"
echo "   Backup Completed Successfully!"
echo "-------------------------------------------"
echo "Saved to:   $BACKUP_PATH"
echo "Uploaded to: $NEXTCLOUD_DIR"
echo "SHA256: ${BACKUP_NAME}.sha256"
echo ""
