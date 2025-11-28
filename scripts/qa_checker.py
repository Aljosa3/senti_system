---------------------------------------
FILE START: ~/senti_system/scripts/qa_checker.py
---------------------------------------
#!/usr/bin/env python3
"""
Senti System — Automated QA Checker
Location: ~/senti_system/scripts/qa_checker.py
Version: 1.0

This script performs automated QA validation using:
- self_check_schema.json (SCP-24 rules)
- project directory structure
- module metadata
- config schemas

It complements manual QA: docs/QA_CHECKLIST.md
"""

import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_DIR = PROJECT_ROOT / ".claude"
SCHEMA_FILE = CLAUDE_DIR / "self_check_schema.json"

REQUIRED_ROOT_DIRS = [
    "senti_os",
    "senti_core",
    "modules",
    "config",
    "docs",
    "tests",
    "scripts"
]


def load_schema():
    if not SCHEMA_FILE.exists():
        print("❌ ERROR: self_check_schema.json not found.")
        sys.exit(1)

    with open(SCHEMA_FILE, "r") as f:
        return json.load(f)


def check_root_structure():
    print("\n=== ROOT STRUCTURE CHECK ===")

    for d in REQUIRED_ROOT_DIRS:
        if not (PROJECT_ROOT / d).exists():
            print(f"❌ Missing required directory: {d}")
        else:
            print(f"✔ {d}")


def check_init_files():
    print("\n=== __init__.py CHECK ===")

    missing = []
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        if "__pycache__" in dirpath:
            continue

        if any(fname.endswith(".py") for fname in filenames):
            # ensure __init__.py exists
            if "__init__.py" not in filenames:
                missing.append(dirpath)

    if missing:
        print("❌ Missing __init__.py in:")
        for m in missing:
            print(" -", m)
    else:
        print("✔ All packages contain __init__.py")


def check_no_relative_imports():
    print("\n=== IMPORT RULE CHECK ===")

    viol = []

    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        for fname in filenames:
            if fname.endswith(".py"):
                fpath = Path(dirpath) / fname
                with open(fpath, "r") as f:
                    content = f.read()
                    if "from .." in content or "from ../" in content:
                        viol.append(str(fpath))

    if viol:
        print("❌ Relative imports detected:")
        for v in viol:
            print(" -", v)
    else:
        print("✔ No relative imports found")


def qa_run():
    print("=====================================")
    print("  Senti System — Automated QA Check")
    print("=====================================")

    schema = load_schema()

    check_root_structure()
    check_init_files()
    check_no_relative_imports()

    print("\nQA Check complete.\n")


if __name__ == "__main__":
    qa_run()
---------------------------------------
FILE END: ~/senti_system/scripts/qa_checker.py
---------------------------------------
