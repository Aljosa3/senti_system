"""
FAZA 48 — Sandbox Context
FILE 1/6: sandbox_context.py

Immutable execution context for sandboxed runtime operations.

Purpose:
- Carry execution metadata
- Define execution scope
- No execution logic
- No I/O
- No mutation after creation
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SandboxContext:
    """
    Immutable sandbox execution context.

    Attributes:
        target (str): Canonical runtime target (e.g. "senti")
        action (str): Action being executed
        path (Optional[str]): Optional path involved in execution
        source (str): Command source (cli, api, llm)
    """

    target: str
    action: str
    path: Optional[str] = None
    source: str = "runtime"
