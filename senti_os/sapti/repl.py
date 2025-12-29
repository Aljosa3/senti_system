import os
from .state import SessionState
from . import events


def run_chat_repl():
    state = SessionState()
    events.emit("SESSION_STARTED")
    print(f"{state.mode} > ", end="", flush=True)

    while True:
        try:
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            events.emit("SESSION_ABORTED")
            print("\nexit")
            break

        if not user_input:
            print(f"{state.mode} > ", end="", flush=True)
            continue

        cmd = user_input.lower()

        # ── EXIT ─────────────────────────
        if cmd in ("exit", "quit"):
            events.emit("SESSION_ENDED")
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
            if cmd == "propose":
                events.emit("PROPOSE_ENTERED")
            print(f"{state.mode} > ", end="", flush=True)
            continue

        # ── IMPLICIT DRAFT (B10.1) ───────
        if state.mode == "INSPECT":
            events.emit("IMPLICIT_DRAFT_TRIGGERED")
            state.set_mode("DRAFT")
            print(f"{state.mode} > ", end="", flush=True)

        # ── CONTENT LINE ─────────────────
        state.add_line(user_input)
        print(f"{state.mode} > ", end="", flush=True)
