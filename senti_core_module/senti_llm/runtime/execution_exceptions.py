"""
FAZA 47 — Execution Routing Layer
FILE 1/5: execution_exceptions.py

Exception definitions for execution routing.
Defines all errors that can occur during command routing
before any execution happens.

Rules:
- No logic
- No I/O
- No imports
- Pure exception hierarchy
"""


class ExecutionRoutingError(Exception):
    """Base exception for execution routing errors."""


class UnknownActionError(ExecutionRoutingError):
    """Raised when no route exists for a given action."""


class RouteNotAllowedError(ExecutionRoutingError):
    """Raised when action is known but not allowed by policy."""


class ExecutionPolicyError(ExecutionRoutingError):
    """Raised when execution violates routing policy."""


class InvalidExecutionPlanError(ExecutionRoutingError):
    """Raised when execution plan structure is invalid."""
