#!/usr/bin/env bash
set -e

# ================================================================
# Senti System — GitHub Auto Push (PRO VERSION)
# Variant C: Protected Branch (master) → create PR → auto cleanup
# ================================================================

PROJECT_DIR="$HOME/senti_system"
LOGFILE="$PROJECT_DIR/logs/github_auto_push.log"
BRANCH_PREFIX="sync"
MAX_FILE_SIZE_MB=95
INTERNET_CHECK_HOST="github.com"

date() { command date "+%Y-%m-%d %H:%M:%S"; }

log() {
    echo "[$(date)] $1" | tee -a "$LOGFILE"
}

notify() {
    if command -v notify-send &>/dev/null; then
        notify-send "Senti System" "$1"
    fi
}

cd "$PROJECT_DIR" || { log "ERROR: Cannot access project dir"; exit 1; }

log "=== Starting GitHub AUTO PUSH (PRO) ==="

# --------------------------------------------------------
# --allow-offline (for @reboot)
# --------------------------------------------------------
ALLOW_OFFLINE=false
if [[ "$1" == "--allow-offline" ]]; then
    ALLOW_OFFLINE=true
    log "Running in OFFLINE-TOLERANT mode"
fi

# --------------------------------------------------------
# INTERNET CHECK
# --------------------------------------------------------
check_internet() {
    ping -c 1 "$INTERNET_CHECK_HOST" &>/dev/null
}

if ! check_internet; then
    if [[ "$ALLOW_OFFLINE" == true ]]; then
        log "No internet — waiting..."
        until check_internet; do
            sleep 20
            log "Retrying internet check..."
        done
        log "Internet OK."
    else
        log "ERROR: No internet — aborting."
        notify "GitHub Push FAILED (no internet)"
        exit 1
    fi
else
    log "Internet OK."
fi

# --------------------------------------------------------
# LARGE FILE DETECTION (IGNORING BACKUPS/)
# --------------------------------------------------------
log "Checking for large files..."

LARGE_FILE=$(find "$PROJECT_DIR" -type f -size +"${MAX_FILE_SIZE_MB}"M \
    ! -path "$PROJECT_DIR/backups/*" \
    | head -1)

if [[ -n "$LARGE_FILE" ]]; then
    log "ERROR: Large file detected (>${MAX_FILE_SIZE_MB}MB). Push aborted."
    echo "$LARGE_FILE" | tee -a "$LOGFILE"
    notify "Push blocked — large file detected!"
    exit 1
fi

# --------------------------------------------------------
# CLEAN TEMPORARY BRANCHES
# --------------------------------------------------------
log "Cleaning temporary branches..."

for br in $(git branch --list "$BRANCH_PREFIX-*"); do
    git branch -D "$br" &>/dev/null || true
    log "Deleted local branch: $br"
done

for br_remote in $(git branch -r | grep "$BRANCH_PREFIX-" | sed 's/origin\///'); do
    git push origin --delete "$br_remote" &>/dev/null || true
    log "Deleted remote branch: $br_remote"
done

# --------------------------------------------------------
# DETECT CHANGES
# --------------------------------------------------------
log "Checking for changes..."

if git diff --quiet && git diff --cached --quiet; then
    log "No changes to commit."
    exit 0
fi

# --------------------------------------------------------
# CREATE SYNC BRANCH (SAFE TIMESTAMP)
# --------------------------------------------------------
TIMESTAMP=$(command date "+%Y%m%d-%H%M%S")
NEWBR="${BRANCH_PREFIX}-${TIMESTAMP}"

git checkout -b "$NEWBR"
log "Created branch: $NEWBR"

# --------------------------------------------------------
# COMMIT CHANGES
# --------------------------------------------------------
git add -A
git commit -m "Auto-sync: $(date)" | tee -a "$LOGFILE"
log "Commit created."

# --------------------------------------------------------
# PUSH BRANCH
# --------------------------------------------------------
log "Pushing branch $NEWBR..."
git push -u origin "$NEWBR" | tee -a "$LOGFILE"

# --------------------------------------------------------
# CREATE PR (requires gh cli)
# --------------------------------------------------------
if command -v gh &>/dev/null; then
    log "Creating Pull Request..."

    gh pr create \
        --title "Auto-sync update: $(date)" \
        --body "Automated update from Senti System" \
        --base master \
        --head "$NEWBR" \
        --repo "Aljosa3/senti_system" \
        | tee -a "$LOGFILE"

    log "PR created."
    notify "PR created: $NEWBR → master"
else
    log "WARNING: GitHub CLI (gh) not installed. Cannot create PR automatically."
    notify "WARNING: Manual PR required!"
fi

# --------------------------------------------------------
# SWITCH BACK TO MASTER
# --------------------------------------------------------
git checkout master

log "=== GitHub Auto Push Completed ==="
notify "GitHub Auto Push completed!"

exit 0
