"""
FAZA 34 — Execution Router (LLM Runtime)
Pretvarja CLI/LLM/API ukaze v RuntimeAction objekte.
"""

from typing import Any, Dict

from senti_llm.runtime.action_model import RuntimeAction
from senti_llm.runtime.runtime_exceptions import RouterError, InvalidActionError


class ExecutionRouter:
    """
    Glavna komponenta, ki routa user input / LLM output
    v interni akcijski model za LLM Runtime.
    """

    def __init__(self) -> None:
        self.valid_actions = {
            "run.module",
            "query.status",
            "execute.task",
        }

    def route(self, command: str, payload: Dict[str, Any] | None = None, source: str = "cli") -> RuntimeAction:
        """
        Pretvori plain string ukaz v strukturirano RuntimeAction instanco.

        Primeri:
            "run trading"           -> action_type="run.module", payload={"module": "trading"}
            "status"                -> action_type="query.status"
            "task sync_state"       -> action_type="execute.task", payload={"task_name": "sync_state"}
        """

        if payload is None:
            payload = {}

        parts = command.strip().split()

        if not parts:
            raise InvalidActionError("Prazen ukaz.")

        # Definicija action_type
        if parts[0] == "run" and len(parts) >= 2:
            action_type = "run.module"
            payload["module"] = parts[1]

        elif parts[0] == "status":
            action_type = "query.status"

        elif parts[0] == "task" and len(parts) >= 2:
            action_type = "execute.task"
            payload["task_name"] = parts[1]

        else:
            raise RouterError(f"Neznan ukaz: {command}")

        if action_type not in self.valid_actions:
            raise InvalidActionError(f"Neveljaven action_type: {action_type}")

        return RuntimeAction(
            action_type=action_type,
            payload=payload,
            source=source,
        )
