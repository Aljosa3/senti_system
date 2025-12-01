#!/usr/bin/env bash

# ===========================================================
#  Senti System — Boot Launcher
#  Starts Senti OS with proper PYTHONPATH
# ===========================================================

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Set PYTHONPATH to include project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Change to project directory
cd "$PROJECT_ROOT" || exit 1

echo "===================================================="
echo "  Starting Senti OS..."
echo "  Project Root: $PROJECT_ROOT"
echo "===================================================="

# Run the boot loader
python3 senti_os/boot/boot.py

echo "===================================================="
echo "  Senti OS shutdown"
echo "===================================================="
