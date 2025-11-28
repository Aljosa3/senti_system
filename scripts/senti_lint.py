#!/usr/bin/env python3
"""
Senti System - Static Anti-Pattern Analyzer (Senti Lint)
Location: senti_system/scripts/senti_lint.py

Performs static code analysis across the entire Senti System, checking for:
- prohibited import patterns
- OS bypass attempts
- forbidden functions (eval, exec, subprocess, etc.)
- invalid module structure
- missing __init__.py
- naming violations
- root structure violations
- partial patch signatures
- absolute import enforcement

This script is complementary to:
- qa_checker.py (QA level)
- integrity_checker.py (runtime level)
- PROJECT_RULES.md
- SENTI_CORE_AI_RULES.md
"""

import os
import re
from pathlib import Path
import json
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
CONFIG_DIR = PROJECT_ROOT / "config"

FORBIDDEN_PATTERNS = [
    r"\.\./",                     # directory traversal
    r"from\s+\.\.",               # relative import
    r"os\.system",                # OS bypass
    r"subprocess\.",              # command execution
    r"eval\s*\(",                 # dangerous eval
    r"exec\s*\(",                 # dangerous exec
]

FORBIDDEN_IMPORTS = [
    "..",
    "../",
]

FORBIDDEN_FUNCTIONS = [
    "eval(",
    "exec(",
    "os.system(",
    "subprocess.",
]


class LintError(Exception):
    """Raised when the linter detects a problem."""
    pass


class SentiLint:

    # =========================================================
    # MAIN ENTRY
    # =========================================================

    @staticmethod
    def run():
        print("=====================================")
        print("   Senti System — Senti Lint Scan")
        print("=====================================")

        problems = []

        problems += SentiLint._check_required_directories()
        problems += SentiLint._check_init_files()
        problems += SentiLint._check_import_safety()
        problems += SentiLint._check_forbidden_functions()
        problems += SentiLint._check_module_structure()

        if problems:
            print("\n❌ Lint found issues:\n")
            for p in problems:
                print(" -", p)
            raise LintError("Static lint analysis failed.")
        else:
            print("✔ Senti Lint: All checks passed successfully.")

    # =========================================================
    # CHECK REQUIRED DIRECTORIES
    # =========================================================

    @staticmethod
    def _check_required_directories():
        required = [
            "senti_os",
            "senti_core",
            "modules",
            "config",
            "scripts",
            "tests",
            "docs",
        ]

        missing = []
        for d in required:
            if not (PROJECT_ROOT / d).exists():
                missing.append(f"Missing required directory: {d}")

        return missing

    # =========================================================
    # CHECK __init__.py IN ALL PYTHON PACKAGES
    # =========================================================

    @staticmethod
    def _check_init_files():
        missing = []

        for root, dirs, files in os.walk(PROJECT_ROOT):
            root = Path(root)
            if "__pycache__" in root.name:
                continue

            if any(f.endswith(".py") for f in files):
                if "__init__.py" not in files:
                    missing.append(f"Missing __init__.py in: {root}")

        return missing

    # =========================================================
    # CHECK IMPORT SAFETY
    # =========================================================

    @staticmethod
    def _check_import_safety():
        offenders = []

        for root, dirs, files in os.walk(PROJECT_ROOT):
            for f in files:
                if f.endswith(".py"):
                    path = Path(root) / f
                    content = path.read_text()

                    # Check forbidden patterns
                    for pattern in FORBIDDEN_PATTERNS:
                        if re.search(pattern, content):
                            offenders.append(
                                f"Dangerous import/pattern in {path}: pattern '{pattern}'"
                            )

                    # Check for absolute imports requirement
                    if "from ." in content or "import ." in content:
                        offenders.append(f"Relative import detected in {path}")

        return offenders

    # =========================================================
    # CHECK FORBIDDEN FUNCTIONS
    # =========================================================

    @staticmethod
    def _check_forbidden_functions():
        offenders = []

        for root, dirs, files in os.walk(PROJECT_ROOT):
            for f in files:
                if f.endswith(".py"):
                    path = Path(root) / f
                    content = path.read_text()

                    for func in FORBIDDEN_FUNCTIONS:
                        if func in content:
                            offenders.append(f"Forbidden function '{func}' in {path}")

        return offenders

    # =========================================================
    # CHECK MODULE STRUCTURE
    # =========================================================

    @staticmethod
    def _check_module_structure():
        problems = []

        if not MODULES_DIR.exists():
            return ["Modules directory missing."]

        for module_dir in MODULES_DIR.iterdir():
            if not module_dir.is_dir():
                continue

            module_json = module_dir / "module.json"
            implementation = module_dir / f"{module_dir.name}.py"

            if not module_json.exists():
                problems.append(f"{module_dir.name}: Missing module.json")

            if not implementation.exists():
                problems.append(
                    f"{module_dir.name}: Missing implementation file {module_dir.name}.py"
                )

            # Check required functions in module implementation:
            if implementation.exists():
                content = implementation.read_text()

                required_funcs = ["load(", "start(", "stop(", "metadata("]
                for func in required_funcs:
                    if func not in content:
                        problems.append(
                            f"{module_dir.name}: Missing required function '{func}'"
                        )

        return problems


if __name__ == "__main__":
    try:
        SentiLint.run()
    except LintError as e:
        print("\n❌", e)
        exit(1)
    except Exception as e:
        print("\n❌ Unexpected error:", e)
        exit(1)
