#!/bin/bash

# ============================================
# Senti System — Restore Utility (FINAL)
# Safe restore + SHA256 verification + Sandbox
# ============================================

ROOT_DIR="$HOME/senti_system"
BACKUP_DIR="$ROOT_DIR/backups"
RESTORE_ROOT="$ROOT_DIR/RESTORED"

mkdir -p "$RESTORE_ROOT"

echo "-------------------------------------------"
echo "   SENTI SYSTEM — Restore Utility (FINAL)"
echo "-------------------------------------------"

# 1. LIST AVAILABLE BACKUPS
echo ""
echo "Available backups:"
echo "-------------------------------------------"

if ls "$BACKUP_DIR"/*.zip 1> /dev/null 2>&1; then
    ls -1 "$BACKUP_DIR"/*.zip | sed 's|.*/||'
else
    echo "❌ No backups found in $BACKUP_DIR"
    exit 1
fi

echo "-------------------------------------------"

# 2. ASK USER FOR BACKUP NAME
echo ""
read -p "Enter backup file name (exact): " BACKUP_NAME

if [ ! -f "$BACKUP_DIR/$BACKUP_NAME" ]; then
    echo "❌ Backup not found: $BACKUP_NAME"
    exit 1
fi

# 3. VERIFY SHA256 INTEGRITY
if [ ! -f "$BACKUP_DIR/$BACKUP_NAME.sha256" ]; then
    echo "❌ Missing SHA256 checksum file!"
    exit 1
fi

echo ""
echo "Verifying SHA256 integrity..."
CHECKSUM_RESULT=$(sha256sum -c "$BACKUP_DIR/$BACKUP_NAME.sha256" 2>&1)

# Accept multiple possible outputs (EN / SI)
if [[ "$CHECKSUM_RESULT" != *"OK"* ]] && \
   [[ "$CHECKSUM_RESULT" != *"V REDU"* ]] && \
   [[ "$CHECKSUM_RESULT" != *"v redu"* ]]; then
    echo "❌ SHA256 verification FAILED!"
    echo "$CHECKSUM_RESULT"
    exit 1
fi

echo "✔ SHA256 OK"

# 4. CREATE SANDBOX RESTORE DIR
RESTORE_DIR="$RESTORE_ROOT/${BACKUP_NAME%.zip}"
mkdir -p "$RESTORE_DIR"

echo ""
echo "Restoring into sandbox directory:"
echo "  $RESTORE_DIR"
echo ""

# 5. EXTRACT ZIP
unzip -q "$BACKUP_DIR/$BACKUP_NAME" -d "$RESTORE_DIR"

echo ""
echo "-------------------------------------------"
echo "   Restore Completed Successfully!"
echo "-------------------------------------------"
echo "Restored to: $RESTORE_DIR"
echo ""
echo "You may now inspect, compare, or manually merge."
echo ""
