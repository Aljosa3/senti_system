"""
FAZA 34–35 — Action Model za LLM Runtime
Standardiziran objekt, ki predstavlja ukaz ali zahtevo,
ki jo ExecutionRouter pretvori v interni format.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class RuntimeAction:
    """
    Model, ki predstavlja eno dejanje, ki ga mora LLM Runtime obdelati.
    Primeri action_type:
      - "run.module"
      - "query.status"
      - "execute.task"
    """

    action_type: str                     # npr. "run.module", "query.status", "execute.task"
    payload: Dict[str, Any] = field(default_factory=dict)
    source: str = "cli"                  # "cli", "llm", "api"
    request_id: Optional[str] = None     # unique ID za logiranje in trace

    def __post_init__(self) -> None:
        if not isinstance(self.payload, dict):
            raise ValueError("RuntimeAction.payload must be a dictionary.")
