#!/bin/bash

# HARD FAILSAFE DISABLE SCRIPT FOR ANTI-DISCLOSURE
# OWNER-ONLY. SAFE TO RUN ANYTIME.

ANTI_DIR="/senti/core/security/anti_disclosure"
BACKUP_DIR="/senti/backups/anti_disclosure_disabled_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/senti/logs/security.log"

echo "---- Senti OS Anti-Disclosure Disable Script ----"

# 1) Check if directory exists
if [ ! -d "$ANTI_DIR" ]; then
    echo "[INFO] Anti-Disclosure directory not found. System is already in open mode."
    echo "$(date)  | INFO | Anti-Disclosure already removed." >> "$LOG_FILE"
    exit 0
fi

# 2) Create backup
echo "[INFO] Creating backup at: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$ANTI_DIR" "$BACKUP_DIR"

# 3) Delete anti-disclosure modules
echo "[INFO] Removing Anti-Disclosure modules..."
rm -rf "$ANTI_DIR"

# 4) Log the action
echo "$(date)  | OWNER ACTION | Anti-Disclosure modules disabled and removed." >> "$LOG_FILE"

# 5) Confirmation
echo "[SUCCESS] Anti-Disclosure successfully disabled."
echo "[SUCCESS] System is now in OPEN MODE."
echo "----------------------------------------------"
