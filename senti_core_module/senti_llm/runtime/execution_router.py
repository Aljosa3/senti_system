"""
FAZA 39 — Execution Router (LLM Runtime)
Pretvarja CLI/LLM/API ukaze v RuntimeAction objekte.

POSODOBLJENO:
- Dodana podpora za load.module (nalaganje modulov)
- Dodana podpora za list.modules (seznam naloženih modulov)
- FAZA 39: Parse key=value arguments for run command
"""

from typing import Any, Dict

from .action_model import RuntimeAction
from .runtime_exceptions import RouterError, InvalidActionError


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
            "load.module",      # FAZA 36.2
            "list.modules",     # FAZA 36.2
        }

    def route(self, command: str, payload: Dict[str, Any] | None = None, source: str = "cli") -> RuntimeAction:
        """
        Pretvori plain string ukaz v strukturirano RuntimeAction instanco.

        Primeri:
            "run trading"           -> action_type="run.module", payload={"module": "trading"}
            "status"                -> action_type="query.status"
            "task sync_state"       -> action_type="execute.task", payload={"task_name": "sync_state"}
            "load path/to/mod.py"   -> action_type="load.module", payload={"path": "path/to/mod.py"}
            "list"                  -> action_type="list.modules"
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

            # FAZA 39: Parse additional key=value arguments
            for i in range(2, len(parts)):
                if "=" in parts[i]:
                    key, value = parts[i].split("=", 1)
                    payload[key] = value

        elif parts[0] == "status":
            action_type = "query.status"

        elif parts[0] == "task" and len(parts) >= 2:
            action_type = "execute.task"
            payload["task_name"] = parts[1]

        # FAZA 36.2 — Nalaganje modulov
        elif parts[0] == "load" and len(parts) >= 2:
            action_type = "load.module"
            payload["path"] = parts[1]

        # FAZA 36.2 — Seznam naloženih modulov
        elif parts[0] == "list":
            action_type = "list.modules"

        else:
            raise RouterError(f"Neznan ukaz: {command}")

        if action_type not in self.valid_actions:
            raise InvalidActionError(f"Neveljaven action_type: {action_type}")

        return RuntimeAction(
            action_type=action_type,
            payload=payload,
            source=source,
        )
