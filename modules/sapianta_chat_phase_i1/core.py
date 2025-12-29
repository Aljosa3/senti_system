def run():
    print("────────────────────────────────────")
    print(" SAPIANTA CHAT — PHASE I.1")
    print(" Advisory-only | No execution | No LLM")
    print("────────────────────────────────────")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession terminated. No actions were taken.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Session closed. No actions were taken.")
            break

        print(advisory_response(user_input))


def advisory_response(text: str) -> str:
    return (
        "\n[PHASE I.1 — ADVISORY ONLY]\n"
        f"Input acknowledged: \"{text}\"\n\n"
        "No execution capability exists.\n"
        "No actions were taken.\n"
        "Decision authority remains with the human.\n"
    )
