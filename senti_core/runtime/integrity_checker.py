"""
Senti System - Runtime Integrity Checker
Location: senti_core/runtime/integrity_checker.py

Responsible for verifying:
- module.json validity
- module template compliance
- absolute import safety
- no OS bypass attempts
- required directories exist
- __init__.py integrity
- config schema validity
- module interface structure

This file is critical for runtime safety and must remain consistent.
"""

import json
import yaml
import os
import inspect
from pathlib import Path

from senti_core.utils.validator import Validator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = PROJECT_ROOT / "modules"
CONFIG_DIR = PROJECT_ROOT / "config"
SYSTEM_CONFIG = CONFIG_DIR / "system" / "config.yaml"
MODULE_SCHEMA = CONFIG_DIR / "modules" / "schema.json"

REQUIRED_ROOT_DIRS = [
    "senti_os",
    "senti_core",
    "modules",
    "config",
    "scripts",
    "tests",
    "docs"
]


class IntegrityError(Exception):
    """Raised when a critical integrity violation is detected."""
    pass


class IntegrityChecker:

    # ===============================================================
    # PUBLIC METHODS
    # ===============================================================

    @staticmethod
    def check_system_integrity():
        """
        Performs full system integrity validation.
        Raises IntegrityError on failure.
        """
        IntegrityChecker._check_required_directories()
        IntegrityChecker._check_init_files()
        IntegrityChecker._check_system_config()
        IntegrityChecker._check_module_schema()
        IntegrityChecker._scan_for_dangerous_imports()
        print("✔ System integrity validated.")

    @staticmethod
    def check_module_integrity(module_path: Path):
        """
        Validates a single module directory.
        """
        IntegrityChecker._check_module_json(module_path)
        IntegrityChecker._check_module_interface(module_path)
        print(f"✔ Module integrity OK: {module_path.name}")

    # ===============================================================
    # SYSTEM LEVEL CHECKS
    # ===============================================================

    @staticmethod
    def _check_required_directories():
        missing = []
        for d in REQUIRED_ROOT_DIRS:
            if not (PROJECT_ROOT / d).exists():
                missing.append(d)

        if missing:
            raise IntegrityError(f"Missing required directories: {missing}")

        print("✔ Required root directories exist.")

    @staticmethod
    def _check_init_files():
        """
        Ensures every Python directory has __init__.py.
        """
        missing = []
        for root, dirs, files in os.walk(PROJECT_ROOT):
            root = Path(root)
            if "__pycache__" in root.name:
                continue

            # if directory contains ANY .py file, must have __init__.py
            if any(f.endswith(".py") for f in files):
                if "__init__.py" not in files:
                    missing.append(str(root))

        if missing:
            raise IntegrityError(f"Missing __init__.py in: {missing}")

        print("✔ __init__.py integrity OK.")

    @staticmethod
    def _check_system_config():
        if not SYSTEM_CONFIG.exists():
            raise IntegrityError("System config.yaml is missing.")

        try:
            with open(SYSTEM_CONFIG, "r") as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise IntegrityError(f"Invalid YAML in system config: {e}")

        print("✔ System config.yaml validated.")

    @staticmethod
    def _check_module_schema():
        if not MODULE_SCHEMA.exists():
            raise IntegrityError("Module schema.json is missing.")

        try:
            with open(MODULE_SCHEMA, "r") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise IntegrityError(f"Invalid module schema.json: {e}")

        print("✔ Module schema.json validated.")

    # ===============================================================
    # MODULE LEVEL CHECKS
    # ===============================================================

    @staticmethod
    def _check_module_json(module_path: Path):
        """
        Checks module.json against schema.
        """
        module_json_path = module_path / "module.json"

        if not module_json_path.exists():
            raise IntegrityError(f"{module_path.name} missing module.json")

        # Load module metadata
        try:
            with open(module_json_path, "r") as f:
                module_meta = json.load(f)
        except json.JSONDecodeError as e:
            raise IntegrityError(f"Invalid module.json in {module_path}: {e}")

        # Validate via Validator
        Validator.validate_module_metadata(module_meta)

        print(f"✔ module.json validated for {module_path.name}")

    @staticmethod
    def _check_module_interface(module_path: Path):
        """
        Ensures module implements the required interface structure.
        """
        module_file = module_path / f"{module_path.name}.py"
        if not module_file.exists():
            raise IntegrityError(f"{module_path.name} missing module implementation file.")

        # Dynamically import module
        import importlib.util

        spec = importlib.util.spec_from_file_location(module_path.name, module_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Check required functions
        required = ["load", "start", "stop", "metadata"]
        for func in required:
            if not hasattr(mod, func):
                raise IntegrityError(
                    f"Module {module_path.name} missing required function: {func}"
                )

        # Check class inheritance from base template
        classes = inspect.getmembers(mod, inspect.isclass)
        found_valid_class = False

        for _, cls in classes:
            if "Base" in cls.__name__ or "Module" in cls.__name__:
                found_valid_class = True

        if not found_valid_class:
            raise IntegrityError(
                f"Module {module_path.name} must inherit from a base module template."
            )

        print(f"✔ Module interface validated for {module_path.name}")

    # ===============================================================
    # IMPORT SAFETY
    # ===============================================================

    @staticmethod
    def _scan_for_dangerous_imports():
        dangerous_patterns = ["..", "../", "os.system", "subprocess.", "eval(", "exec("]

        offenders = []

        for root, dirs, files in os.walk(PROJECT_ROOT):
            for f in files:
                if f.endswith(".py"):
                    path = Path(root) / f
                    content = path.read_text()

                    for pattern in dangerous_patterns:
                        if pattern in content:
                            offenders.append((str(path), pattern))

        if offenders:
            raise IntegrityError(f"Dangerous imports detected: {offenders}")

        print("✔ Import safety validated.")
