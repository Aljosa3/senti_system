"""
FAZA 38.1 — Module Storage System (Stabilized)
----------------------------------------------
Secure, sandboxed per-module storage implementation.

Fixes in FAZA 38.1:
- Replaced fragile parents[4] path traversal with stable project-root discovery
- Always uses absolute paths
- Ensures storage writes succeed regardless of working directory
- Fully compatible with tests and runtime environments
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import json
import os


def discover_senti_root(start: Path) -> Path:
    """
    Robust search for the Senti System root directory.

    We detect the project root by locating the directory that contains:
    - senti_core_module/

    This is far safer and more stable than using parents[x] indexing,
    which fails under test runners, Claude Code execution, or venv cwd changes.
    """

    for parent in start.resolve().parents:
        if (parent / "senti_core_module").exists():
            # We found the root of the project
            return parent

    # If for some reason we cannot find it, fall back to current working directory
    # This should NEVER happen in your project but ensures defensive behavior.
    return Path(os.getcwd()).resolve()


class ModuleStorage:
    """
    Secure storage system for Senti OS modules.

    Each module gets an isolated directory under:
        <senti_system_root>/senti_data/modules/<module_name>/
    """

    def __init__(self, module_name: str):
        self.module_name = module_name

        # Determine robust Senti OS project root
        current_file = Path(__file__).resolve()
        senti_system_root = discover_senti_root(current_file)

        # Construct absolute storage path
        self.base_path = senti_system_root / "senti_data" / "modules" / module_name

        # Ensure directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve(self, path: str) -> Path:
        """
        Resolve and validate paths for safety.
        """

        path_obj = Path(path)

        # No absolute paths allowed
        if path_obj.is_absolute():
            raise ValueError(f"Absolute paths not allowed: {path}")

        # No traversal
        if ".." in path_obj.parts:
            raise ValueError(f"Path traversal not allowed: {path}")

        # Resolve relative to storage root
        resolved = (self.base_path / path_obj).resolve()

        # Must stay inside module's storage
        try:
            resolved.relative_to(self.base_path)
        except ValueError:
            raise ValueError(f"Path outside module storage: {path}")

        # Prevent symlink escape
        if resolved.is_symlink():
            real = resolved.resolve()
            try:
                real.relative_to(self.base_path)
            except ValueError:
                raise ValueError(f"Symlink points outside module storage: {path}")

        return resolved

    def read_text(self, path: str) -> str:
        resolved = self._resolve(path)

        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not resolved.is_file():
            raise ValueError(f"Not a file: {path}")

        return resolved.read_text(encoding="utf-8")

    def write_text(self, path: str, data: str) -> None:
        resolved = self._resolve(path)

        # Ensure parent directories exist
        resolved.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write
        tmp = resolved.with_suffix(resolved.suffix + ".tmp")

        try:
            tmp.write_text(data, encoding="utf-8")
            tmp.replace(resolved)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise

    def read_json(self, path: str) -> Dict[str, Any]:
        text = self.read_text(path)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}")

    def write_json(self, path: str, data: Dict[str, Any]) -> None:
        try:
            text = json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Cannot serialize JSON: {e}")

        self.write_text(path, text)

    def exists(self, path: str) -> bool:
        try:
            resolved = self._resolve(path)
            return resolved.exists()
        except ValueError:
            return False

    def list_files(self, path: str = "") -> List[str]:
        if path == "":
            resolved = self.base_path
        else:
            resolved = self._resolve(path)

        if not resolved.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        if not resolved.is_dir():
            raise ValueError(f"Not a directory: {path}")

        out = []
        for item in resolved.rglob("*"):
            if item.is_file():
                out.append(str(item.relative_to(self.base_path)))

        return sorted(out)

    def get_base_path(self) -> str:
        return str(self.base_path)
