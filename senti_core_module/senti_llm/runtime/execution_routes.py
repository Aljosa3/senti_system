"""
FAZA 47 — Execution Routing Layer
FILE 2/5: execution_routes.py

Static execution route definitions.
Maps normalized actions to execution route identifiers.

Purpose:
- Define which actions exist
- Define which executor type they map to
- No logic, no routing, no execution

Rules:
- No I/O
- No imports
- No functions
- No classes
- Pure static definitions
"""

# =====================================================================
# Execution Routes
# =====================================================================

# Canonical execution routes
EXECUTION_ROUTES = {
    # File-related actions
    "read": "file_executor",
    "write": "file_executor",
    "delete": "file_executor",

    # Module-related actions
    "load_module": "module_executor",
    "unload_module": "module_executor",

    # Runtime / system-safe actions
    "status": "runtime_executor",
    "inspect": "runtime_executor",
}

# Actions explicitly allowed for execution
ALLOWED_ACTIONS = tuple(EXECUTION_ROUTES.keys())

# Actions explicitly blocked at routing layer
BLOCKED_ACTIONS = (
    "rm",
    "shutdown",
    "reboot",
    "format",
)
