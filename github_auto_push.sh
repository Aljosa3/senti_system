#!/usr/bin/env bash
# ============================================================
# Senti System — Automatic GitHub Push (Stable Version)
# ============================================================

PROJECT_DIR="$HOME/senti_system"
LOGFILE="$PROJECT_DIR/logs/github_auto_push.log"
BRANCH="master"

# ------------------------------------------------------------
date() { echo $(/bin/date +"%Y-%m-%d %H:%M:%S"); }
# ------------------------------------------------------------

echo "[$(date)] === Starting GitHub Auto Push ===" | tee -a "$LOGFILE"

cd "$PROJECT_DIR" || exit 1

# ------------------------------------------------------------
# 1. WAIT FOR INTERNET
# ------------------------------------------------------------
echo "[$(date)] Checking internet connectivity..." | tee -a "$LOGFILE"

while ! ping -c1 github.com >/dev/null 2>&1; do
    echo "[$(date)] No internet — retrying in 20 sec..." | tee -a "$LOGFILE"
    sleep 20
done

echo "[$(date)] Internet OK." | tee -a "$LOGFILE"

# ------------------------------------------------------------
# 2. GIT CLEANUP (TEMP BRANCHES)
# ------------------------------------------------------------
echo "[$(date)] Cleaning temporary branches..." | tee -a "$LOGFILE"

for br in $(git branch | grep "temp-"); do
    git branch -D "$br" 2>/dev/null && \
    echo "[$(date)] Removed: $br" | tee -a "$LOGFILE"
done

# ------------------------------------------------------------
# 3. CHECK FOR CHANGES (ignore binary/big files)
# ------------------------------------------------------------
echo "[$(date)] Checking for changes..." | tee -a "$LOGFILE"

# Ignore big/binary files (>5MB)
git add -A :!*.zip :!*.png :!*.jpg :!*.jpeg :!*.mp4 :!*.mp3 :!*.pdf :!*.bin :!*.tar :!*.gz :!*.7z :!*.mov

# Check if anything is actually added
if git diff --cached --quiet; then
    echo "[$(date)] No changes to commit." | tee -a "$LOGFILE"
else
    git commit -m "Auto-sync: $(date)"
    echo "[$(date)] Commit created." | tee -a "$LOGFILE"
fi

# ------------------------------------------------------------
# 4. SAFE PUSH WITH RETRY
# ------------------------------------------------------------

PUSH_OK=false
for i in {1..10}; do
    echo "[$(date)] Attempt $i: pushing to GitHub..." | tee -a "$LOGFILE"

    if git push origin "$BRANCH"; then
        PUSH_OK=true
        echo "[$(date)] Push successful!" | tee -a "$LOGFILE"
        break
    else
        echo "[$(date)] Push FAILED. Retrying in 30 sec..." | tee -a "$LOGFILE"
        sleep 30
    fi
done

if [ "$PUSH_OK" = false ]; then
    echo "[$(date)] ❌ All push attempts FAILED!" | tee -a "$LOGFILE"
    exit 1
fi

# ------------------------------------------------------------
# 5. CLEAN OLD PULL REQUEST BRANCHES ON GITHUB (SAFE)
# ------------------------------------------------------------
echo "[$(date)] Cleaning remote temporary branches..." | tee -a "$LOGFILE"

for rbr in $(git branch -r | grep "temp-" | sed 's/origin\///'); do
    git push origin --delete "$rbr" 2>/dev/null && \
    echo "[$(date)] Remote cleaned: $rbr" | tee -a "$LOGFILE"
done

echo "[$(date)] === GitHub Auto Push Completed ===" | tee -a "$LOGFILE"
