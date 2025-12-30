"""
CLI entry point for Phase I.3

Usage:
  python3 -m sapianta_chat_phase_i3 <INTENT>
"""

import sys
from modules.sapianta_chat_phase_i3.frame import frame_response


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 -m sapianta_chat_phase_i3 <INTENT>")
        sys.exit(1)

    intent = sys.argv[1].strip().upper()
    response = frame_response(intent)

    print("[PHASE I.3 — RESPONSE FRAMED]")
    print(f"Intent: {intent}\n")
    print(response)


if __name__ == "__main__":
    main()
