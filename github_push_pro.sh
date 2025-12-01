#!/usr/bin/env bash

# ============================================================
# SENTI SYSTEM — GitHub PRO Auto Push (Protected Branch OK)
# Branch → Commit → Push → Pull Request → Auto Merge
# ============================================================

set -e

PROJECT_DIR="$HOME/senti_system"
cd "$PROJECT_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BRANCH="auto-sync-$TIMESTAMP"

echo "────────────────────────────────────────────"
echo "Senti GitHub PRO"
echo "Creating branch: $BRANCH"
echo "────────────────────────────────────────────"

# 1) Create new branch
git checkout -b "$BRANCH"

# 2) Stage & commit
git add -A
git commit -m "Auto sync ($TIMESTAMP)"

# 3) Push branch
git push -u origin "$BRANCH"

# 4) Create Pull Request (requires GitHub CLI)
gh pr create \
  --title "Auto-sync $TIMESTAMP" \
  --body "Automated sync from Senti System." \
  --base master \
  --head "$BRANCH"

# 5) Auto-merge PR & delete branch
gh pr merge "$BRANCH" --squash --delete-branch

# 6) Return to master
git checkout master

echo "✔ DONE — Auto PR merged and branch deleted."
