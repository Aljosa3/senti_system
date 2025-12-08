#!/usr/bin/env bash

# -----------------------------------------------------------
# SENTI SYSTEM — RESTORE TOOL (SNAPSHOTS + ZIP BACKUPS)
# -----------------------------------------------------------

set -e

PROJECT_DIR="$HOME/senti_system"
SNAPSHOT_DIR="$HOME/senti_system_snapshots/daily"
ZIP_DIR="$PROJECT_DIR/backups"

BACKUP_BEFORE_RESTORE="$HOME/senti_system_restore_backup"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

usage() {
    echo ""
    echo "Senti Restore Tool - Options:"
    echo "-------------------------------------------"
    echo "  --list                     Prikaže vse snapshot-e in ZIP-e"
    echo "  --from-snapshot <DATE>     Obnovi sistem iz snapshot-a"
    echo "  --from-zip <FILE>          Obnovi sistem iz ZIP datoteke"
    echo ""
    exit 0
}

# ---------------------------------------------
# LIST BACKUPS
# ---------------------------------------------
if [[ "$1" == "--list" ]]; then
    echo ""
    echo "📁 Razpoložljivi SNAPSHOTI:"
    ls -1 "$SNAPSHOT_DIR" || echo "(ni snapshotov)"

    echo ""
    echo "📁 Razpoložljivi ZIP backupi:"
    ls -1 "$ZIP_DIR"/*.zip 2>/dev/null || echo "(ni ZIP backupov)"

    echo ""
    exit 0
fi

# ---------------------------------------------
# SAFE BACKUP BEFORE RESTORE
# ---------------------------------------------
create_safety_backup() {
    echo ""
    echo "🛡 Ustvarjam varnostno kopijo trenutnega sistema..."
    rm -rf "$BACKUP_BEFORE_RESTORE"
    cp -r "$PROJECT_DIR" "$BACKUP_BEFORE_RESTORE"
    echo "✓ Varnostna kopija shranjena v: $BACKUP_BEFORE_RESTORE"
}

# ---------------------------------------------
# RESTORE FROM SNAPSHOT
# ---------------------------------------------
if [[ "$1" == "--from-snapshot" ]]; then
    SNAP_DATE="$2"
    SOURCE="$SNAPSHOT_DIR/$SNAP_DATE"

    if [[ ! -d "$SOURCE" ]]; then
        echo "❌ Snapshot $SNAP_DATE ne obstaja!"
        exit 1
    fi

    create_safety_backup

    echo "♻ Obnavljam sistem iz snapshot-a: $SNAP_DATE"
    rm -rf "$PROJECT_DIR"
    cp -r "$SOURCE" "$PROJECT_DIR"

    echo ""
    echo "✓ SISTEM OBNOVLJEN IZ SNAPSHOTA"
    echo ""
    exit 0
fi

# ---------------------------------------------
# RESTORE FROM ZIP BACKUP
# ---------------------------------------------
if [[ "$1" == "--from-zip" ]]; then
    ZIP_FILE="$2"
    FULL_ZIP_PATH="$ZIP_DIR/$ZIP_FILE"

    if [[ ! -f "$FULL_ZIP_PATH" ]]; then
        echo "❌ ZIP datoteka ne obstaja: $FULL_ZIP_PATH"
        exit 1
    fi

    # Verify checksum if available
    SHA_FILE="${FULL_ZIP_PATH}.sha256"
    if [[ -f "$SHA_FILE" ]]; then
        echo "🔍 Preverjam SHA256 integriteto..."
        shasum -c "$SHA_FILE" || {
            echo "❌ Integriteta ZIP-a NI v redu!"
            exit 1
        }
        echo "✓ ZIP integriteta OK"
    else
        echo "⚠ Opozorilo: SHA256 datoteka manjka"
    fi

    create_safety_backup

    echo "♻ Obnavljam sistem iz ZIP: $ZIP_FILE"
    rm -rf "$PROJECT_DIR"
    unzip "$FULL_ZIP_PATH" -d "$HOME"

    echo ""
    echo "✓ SISTEM OBNOVLJEN IZ ZIP BACKUPA"
    echo ""
    exit 0
fi

usage
