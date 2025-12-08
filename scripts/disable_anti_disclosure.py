#!/usr/bin/env python3

"""
SOFT FAILSAFE DISABLER FOR ANTI-DISCLOSURE
Can be run inside Senti OS or independently as a Python tool.
"""

import os
import shutil
import datetime

ANTI_DIR = "/senti/core/security/anti_disclosure"
BACKUP_BASE = "/senti/backups/"
LOG_FILE = "/senti/logs/security.log"

def log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp}  |  OWNER ACTION  |  {message}\n")

def disable_anti_disclosure():
    print("---- Senti OS Soft Anti-Disclosure Disable ----")

    if not os.path.isdir(ANTI_DIR):
        print("[INFO] Anti-Disclosure module not found. Already disabled.")
        log("Anti-Disclosure already disabled (soft check).")
        return

    # Create backup folder
    backup_dir = os.path.join(
        BACKUP_BASE,
        f"anti_disclosure_disabled_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(backup_dir, exist_ok=True)
    print(f"[INFO] Backup created at: {backup_dir}")

    # Copy files
    shutil.copytree(ANTI_DIR, backup_dir + "/anti_disclosure")

    # Remove the module
    print("[INFO] Removing Anti-Disclosure modules...")
    shutil.rmtree(ANTI_DIR)

    log("Anti-Disclosure removed via Python soft disable.")
    print("[SUCCESS] Anti-Disclosure disabled (soft mode). System is now OPEN.")

if __name__ == "__main__":
    disable_anti_disclosure()
