"""
Sapianta CLI Chat — Phase A (read-only)

Purpose:
- Provide a human-facing CLI interface
- Route all input through the advisory pipeline
- Never allow execution

Authority: NONE
Execution: FORBIDDEN
"""

import json
from modules.sapianta_chat_mandate_bridge.bridge import process_chat_input
from modules.sapianta_advisory_renderer.render import render_advisory_output
from modules.sapianta_output_channel.channel import output_advisory
# FAZA IV: Chat Inspect wiring
from modules.sapianta_chat_state_machine.machine import ChatStateMachine
from modules.sapianta_chat_inspect.inspect import inspect_full


def run_cli_chat():
    """
    Start interactive CLI chat session.
    """

    print("Sapianta CLI Chat (read-only)")
    print("Type 'exit' to quit.\n")

    # FAZA IV: Initialize state machine for inspect functionality
    machine = ChatStateMachine()

    while True:
        user_input = input("> ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Session closed.")
            break

        # FAZA IV: Route "chat inspect" command (read-only)
        if user_input.lower() in {"chat inspect", "inspect"}:
            try:
                result = inspect_full(machine)
                print("\n--- Chat State Inspection ---")
                print(json.dumps(result, indent=2, default=str))
                print("-----------------------------\n")
            except Exception as e:
                print(f"\n[ERROR] Inspect failed: {e}\n")
            continue

        # Phase V.1 — chat → mandate → intent
        advisory_pipeline = process_chat_input(user_input)

        # FAZA V.1: Store mandate from pipeline in ChatStateMachine context (PRE-EBM)
        mandate = advisory_pipeline.get("mandate")
        if mandate is not None:
            machine.context["mandate"] = mandate

        # -------------------------------
        # Phase V.2 — renderer adapter
        # -------------------------------
        # IMPORTANT:
        # Renderer expects a FLAT payload:
        # {
        #   "intent": "...",
        #   "policy": {...}
        # }
        # CLI is the boundary layer that adapts internal pipeline structure.
        renderer_payload = {
            "intent": advisory_pipeline
                .get("mandate_intent_binding", {})
                .get("intent", "UNKNOWN"),
            "policy": advisory_pipeline.get("advisory_policy", {})
        }

        rendered = render_advisory_output(renderer_payload)

        # Phase V.3 — output channel (CLI)
        output = output_advisory(
            rendered,
            channel="CLI"
        )

        # Extract intent detection results (Phase I.2)
        intent_detection = advisory_pipeline.get("intent_detection", {})
        detected_intent = intent_detection.get("intent", "UNKNOWN")
        detection_reason = intent_detection.get("reason", "No reason provided")

        # Extract final binding intent
        binding_result = advisory_pipeline.get("mandate_intent_binding", {})
        final_intent = binding_result.get("intent", "NO_BINDING")

        print("\n--- Advisory Output ---")
        print(f"Detected Intent: {detected_intent}")
        print(f"  Reason: {detection_reason}")
        print(f"Final Advisory Intent: {final_intent}")
        print()
        print(output.get("content", {}).get("explanation", "No explanation"))
        print("----------------------\n")


if __name__ == "__main__":
    run_cli_chat()
