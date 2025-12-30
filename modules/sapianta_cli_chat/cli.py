"""
Sapianta CLI Chat — Phase A (read-only)

Purpose:
- Provide a human-facing CLI interface
- Route all input through the advisory pipeline
- Never allow execution

Authority: NONE
Execution: FORBIDDEN
"""

from modules.sapianta_chat_mandate_bridge.bridge import process_chat_input
from modules.sapianta_advisory_renderer.render import render_advisory_output
from modules.sapianta_output_channel.channel import output_advisory


def run_cli_chat():
    """
    Start interactive CLI chat session.
    """

    print("Sapianta CLI Chat (read-only)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Session closed.")
            break

        # Phase V.1 — chat → mandate → intent
        advisory_pipeline = process_chat_input(user_input)

        # Phase V.2 — render advisory output
        rendered = render_advisory_output(
            advisory_pipeline.get("advisory_policy", {})
        )

        # Phase V.3 — output channel (CLI)
        output = output_advisory(
            rendered,
            channel="CLI"
        )

        print("\n--- Advisory Output ---")
        print(output.get("content", {}).get("explanation", "No explanation"))
        print("----------------------\n")


if __name__ == "__main__":
    run_cli_chat()
