import os
from .state import SessionState


def run_chat_repl():
    state = SessionState()
    print(f"{state.mode} > ", end="", flush=True)

    while True:
        try:
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\nexit")
            break

        if not user_input:
            print(f"{state.mode} > ", end="", flush=True)
            continue

        cmd = user_input.lower()

        # ── EXIT ─────────────────────────
        if cmd in ("exit", "quit"):
            print("Session ended.")
            break

        # ── CLEAR ────────────────────────
        if cmd == "clear":
            os.system('clear' if os.name != 'nt' else 'cls')
            print(f"{state.mode} > ", end="", flush=True)
            continue

        # ── SUMMARY ──────────────────────
        if cmd == "summary":
            print(state.summary())
            print(f"{state.mode} > ", end="", flush=True)
            continue

        # ── EXPLICIT MODE SWITCH ─────────
        if cmd in ("draft", "propose"):
            state.set_mode(cmd.upper())
            print(f"{state.mode} > ", end="", flush=True)
            continue

        # ── IMPLICIT DRAFT (B10.1) ───────
        if state.mode == "INSPECT":
            state.set_mode("DRAFT")
            print(f"{state.mode} > ", end="", flush=True)

        # ── CONTENT LINE ─────────────────
        state.add_line(user_input)
        print(f"{state.mode} > ", end="", flush=True)
