#!/usr/bin/env bash

# ===========================================================
#  Senti System — Full Auto GitHub Push
#  (Ena komanda, nič razmišljanja)
# ===========================================================

cd ~/senti_system || exit 1

# 1. Add all changes
git add -A

# 2. Auto commit with timestamp
COMMIT_MSG="Auto-commit $(date +"%Y-%m-%d %H:%M:%S")"
git commit -m "$COMMIT_MSG"

# 3. Push to main/master
git push

echo "--------------------------------------------"
echo "   ✔ GitHub push completed successfully!"
echo "   ✔ Commit message: $COMMIT_MSG"
echo "--------------------------------------------"
