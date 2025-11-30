#!/usr/bin/env bash

# =============================================================
# Senti System — Automatic GitHub Push Script
# Safe, user-friendly, internet-aware git sync
# =============================================================

PROJECT_DIR="$HOME/senti_system"
LOGFILE="$PROJECT_DIR/logs/github_push.log"

mkdir -p "$PROJECT_DIR/logs"

cd "$PROJECT_DIR" || exit 1

echo "[$(date)] Starting GitHub sync..." | tee -a "$LOGFILE"

# 1. Check internet (repeat until available)
until ping -c1 github.com &>/dev/null; do
    echo "[$(date)] No internet. Retrying in 20 seconds..." | tee -a "$LOGFILE"
    sleep 20
done

# 2. Add & commit changes
git add -A

if git diff --cached --quiet; then
    echo "[$(date)] No changes to commit." | tee -a "$LOGFILE"
else
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')"
    echo "[$(date)] Commit created." | tee -a "$LOGFILE"
fi

# 3. Push (safe push)
if git push origin main; then
    echo "[$(date)] GitHub push successful." | tee -a "$LOGFILE"
    exit 0
else
    echo "[$(date)] Push failed — will retry in 60 seconds." | tee -a "$LOGFILE"
    sleep 60
    git push origin main && echo "[$(date)] Retry successful!" | tee -a "$LOGFILE"
fi
