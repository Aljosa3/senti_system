class SessionState:
    """
    In-memory session state for sapti chat.
    Nothing is persisted. Session ends on exit.
    """
    def __init__(self):
        self.mode = "INSPECT"
        self.buffer = {
            "INSPECT": [],
            "DRAFT": [],
            "PROPOSE": []
        }

    def set_mode(self, mode: str):
        self.mode = mode

    def add_line(self, line: str):
        self.buffer[self.mode].append(line)

    def snapshot(self):
        return {
            "mode": self.mode,
            "content": self.buffer
        }

    def summary(self) -> str:
        """Return formatted summary of session content."""
        lines = []
        lines.append("=== SESSION SUMMARY ===")
        lines.append(f"Current mode: {self.mode}")
        lines.append("")

        for mode in ["INSPECT", "DRAFT", "PROPOSE"]:
            lines.append(f"[{mode}]")
            if self.buffer[mode]:
                for line in self.buffer[mode]:
                    lines.append(f"  {line}")
            else:
                lines.append("  (empty)")
            lines.append("")

        return "\n".join(lines)

