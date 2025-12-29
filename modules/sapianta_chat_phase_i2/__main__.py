from sapianta_chat_phase_i2.intent import detect_intent


def run():
    try:
        user_input = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nNo input. Advisory only.")
        return

    intent = detect_intent(user_input)

    print("[PHASE I.2 — INTENT DETECTED]")
    print(f"Intent: {intent}\n")
    print("Advisory only.")
    print("No execution.")


if __name__ == "__main__":
    run()
