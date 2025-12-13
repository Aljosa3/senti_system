"""
FAZA 48 — Executor Resolver
FILE 5/6: executor_resolver.py

Resolves execution route identifiers into executor callables.

This layer:
- Does NOT execute anything
- Does NOT validate commands
- Does NOT perform I/O
- Only binds route name -> executor function

Pure deterministic binding layer.
"""

from senti_core_module.senti_llm.runtime.executors.file_executor import file_executor
from senti_core_module.senti_llm.runtime.executors.module_executor import module_executor
from senti_core_module.senti_llm.runtime.executors.runtime_executor import runtime_executor


# =====================================================================
# Exceptions
# =====================================================================

class ExecutorResolutionError(Exception):
    """Raised when executor resolution fails."""


# =====================================================================
# Executor Registry
# =====================================================================

EXECUTOR_REGISTRY = {
    "file_executor": file_executor,
    "module_executor": module_executor,
    "runtime_executor": runtime_executor,
}


# =====================================================================
# Resolver
# =====================================================================

def resolve_executor(route: str):
    """
    Resolve execution route to executor callable.

    Args:
        route (str): Execution route identifier.

    Returns:
        callable: Executor function.

    Raises:
        ExecutorResolutionError: If route is invalid or unresolved.
    """
    if not isinstance(route, str):
        raise ExecutorResolutionError(f"Route must be str, got: {type(route)}")

    if route not in EXECUTOR_REGISTRY:
        raise ExecutorResolutionError(f"No executor registered for route: {route}")

    executor = EXECUTOR_REGISTRY[route]

    if not callable(executor):
        raise ExecutorResolutionError(f"Resolved executor for '{route}' is not callable")

    return executor
