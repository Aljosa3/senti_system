"""
LLM Runtime Manager — FAZA 38 INTEGRACIJA
--------------------------------------------
Ta datoteka združuje:

FAZA 31–33:
    - LLM preflight
    - LLM routing
    - Response builder
    - Runtime context

FAZA 34–35:
    - ExecutionRouter (pretvorba ukazov → RuntimeAction)
    - ExecutionOrchestrator (izvedba akcij)

FAZA 36–37:
    - ModuleLoader (dinamično nalaganje modulov)
    - ModuleRegistry (register naloženih modulov)
    - ModuleValidation (validacija modulov)
    - CapabilityManager (capability injection system)
    - Novi ukazi: load, list

FAZA 38:
    - ModuleStorage (secure per-module storage)
    - Storage capabilities: storage.read, storage.write
    - Atomic file operations
    - Path traversal prevention

Dodano:
    - Minimalni testni ukazi:
         "run demo"
         "status"
         "task refresh"
         "load <path>"
         "list"
         "run storage_demo"  # FAZA 38

Cilj:
    Omogočiti prvi end-to-end tok Senti LLM Runtime z dinamičnim nalaganjem modulov
    in varnim per-module file storage sistemom.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

# ===============================
#  OBSTOJEČI MODULI (FAZA 31–33)
# ===============================

from senti_core_module.senti_llm.runtime.llm_runtime_preflight import LLMRuntimePreflight
from senti_core_module.senti_llm.runtime.llm_runtime_context import RuntimeContext
from senti_core_module.senti_llm.runtime.llm_response_builder import LLMResponseWrapper
from senti_core_module.senti_llm.runtime.llm_router import RuntimeRouter
from senti_core_module.senti_llm.llm_client import LLMClient

# ===============================
#  EXECUTION LAYER (FAZA 34–35)
# ===============================

from senti_core_module.senti_llm.runtime.execution_router import ExecutionRouter
from senti_core_module.senti_llm.runtime.execution_orchestrator import ExecutionOrchestrator
from senti_core_module.senti_llm.runtime.action_model import RuntimeAction


class LLMRuntimeManager:
    """
    Centralni runtime nadzornik za Senti OS — LLM plast.

    Od FAZA 36.2 naprej runtime obdeluje tudi:
        - ukaze (CLI ali LLM) preko ExecutionRouter
        - dejanja preko ExecutionOrchestrator
        - dinamično nalaganje modulov preko ModuleLoader

    Namen:
        Zagotoviti stabilno, preverjeno, modularno LLM infrastrukturo z možnostjo
        dinamičnega nalaganja modulov runtime.
    """

    def __init__(self) -> None:
        # FAZA 31 — inicializacija osnovnih komponent
        self.preflight = LLMRuntimePreflight()
        self.context = RuntimeContext(prompt="", capability="execution")
        self.router = RuntimeRouter(config={})
        self.response_wrapper = LLMResponseWrapper(provider="openai")

        # FAZA 31–33 — model client
        self.llm_client = LLMClient()

        # FAZA 34–36.2 — execution layer
        self.exec_router = ExecutionRouter()
        self.exec_orchestrator = ExecutionOrchestrator(context=self.context)

        print("[LLM Runtime Manager] Inicializiran (FAZA 36.2).")

    # ================================================================
    #                J A V N I   A P I
    # ================================================================

    def handle_input(self, user_input: str, source: str = "cli") -> Dict[str, Any]:
        """
        Glavni vhodni mehanizem za CLI / LLM / API.

        1. Preveri, ali je user_input ukaz (run/status/task/load/list).
        2. Če je ukaz → predaj v Execution Layer.
        3. Če ni ukaz → procesiraj kot naravni LLM poziv.
        """

        if self._is_execution_command(user_input):
            return self._process_execution_command(user_input, source)

        # Če ni ukaz → standardna LLM obdelava
        return self._process_llm_prompt(user_input)

    # ================================================================
    #             E X E C U T I O N   L A Y E R
    # ================================================================

    def _is_execution_command(self, text: str) -> bool:
        """
        Ukazi se prepoznajo po ključnih besedah:
            run XYZ
            status
            task XYZ
            load XYZ        # FAZA 36.2
            list            # FAZA 36.2
        """
        stripped = text.strip().lower()

        return (
            stripped.startswith("run ") or
            stripped.startswith("status") or
            stripped.startswith("task ") or
            stripped.startswith("load ") or     # FAZA 36.2
            stripped.startswith("list")          # FAZA 36.2
        )

    def _process_execution_command(self, command: str, source: str) -> Dict[str, Any]:
        print(f"[LLM Runtime] Routing execution command: '{command}'")

        # 1) Pretvorba v RuntimeAction
        action: RuntimeAction = self.exec_router.route(
            command=command,
            payload={"request_id": str(uuid.uuid4())},
            source=source,
        )

        # 2) Izvedba akcije
        result: Dict[str, Any] = self.exec_orchestrator.execute(action)

        # 3) Vrnemo strukturiran rezultat
        return {
            "input": command,
            "runtime_action": action.action_type,
            "result": result,
        }

    # ================================================================
    #                 L L M   P R O C E S S I N G
    # ================================================================

    def _process_llm_prompt(self, text: str) -> Dict[str, Any]:
        """
        Standardna LLM obdelava — uporablja FAZA 31–33 module.
        """

        # Preflight (varnost, validacija konfiguracije)
        if not self.preflight.validate():
            return {"error": "LLM preflight validation failed."}

        # Izbere pravi LLM model glede na text (using LLM client's routing)
        success, llm_raw_response = self.llm_client.generate(
            prompt=text,
            modulation="general"
        )

        if not success:
            return {"error": f"LLM generation failed: {llm_raw_response}"}

        # Wrap response
        wrapped_response = self.response_wrapper.wrap({
            "provider": "openai",
            "model": "gpt-4.1",
            "content": llm_raw_response,
            "type": "completion",
            "tokens_in": 0,
            "tokens_out": 0,
            "meta": {},
        })

        return {
            "input": text,
            "model": "gpt-4.1",
            "structured_response": wrapped_response,
        }

    # ================================================================
    #                 T E S T   K O M A N D E
    # ================================================================

    def run_demo_tests(self) -> Dict[str, Any]:
        """
        Interni test osnovnih execution ukazov.
        Namenjen je preverjanju, ali FAZA 38 deluje.
        """

        results: Dict[str, Any] = {}

        test_commands = [
            "status",
            "run demo",
            "task refresh",
            "list",                                                            # FAZA 36.2
            "load senti_core_module/senti_llm/modules/storage_demo_module.py",  # FAZA 38
            "run storage_demo",                                                # FAZA 38
        ]

        for cmd in test_commands:
            print(f"[TEST] Pošiljam ukaz: {cmd}")
            results[cmd] = self._process_execution_command(cmd, source="test")

        return results


# ================================================================
#          GLAVNI VSTOP ZA TESTIRANJE IZ TERMINALA
# ================================================================

if __name__ == "__main__":
    manager = LLMRuntimeManager()
    results = manager.run_demo_tests()

    print("\n=====================================")
    print("   TESTNI REZULTATI (FAZA 38)")
    print("=====================================\n")

    for k, v in results.items():
        print(f"> {k}")
        print(v)
        print()
