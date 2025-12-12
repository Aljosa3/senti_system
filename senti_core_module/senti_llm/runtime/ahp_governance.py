"""
FAZA 46 — AHP Governance Rules
FILE 5/8: ahp_governance.py

Static governance definitions for Anti-Hallucination Protocol (AHP).
This module defines forbidden operations, imports, and calls.
No logic, no validation, no execution.
"""

FORBIDDEN_SYSTEM_COMMANDS = (
    "rm ",
    "rm -rf",
    "sudo",
    "shutdown",
    "reboot",
    "mkfs",
    "dd ",
    ":(){",
)

FORBIDDEN_IMPORTS = (
    "os",
    "sys",
    "subprocess",
    "shutil",
    "socket",
    "ctypes",
    "pickle",
)

FORBIDDEN_PYTHON_CALLS = (
    "eval",
    "exec",
    "compile",
    "__import__",
    "open",
    "input",
)
