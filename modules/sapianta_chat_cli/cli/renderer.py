def render_output(result: dict) -> str:
    """
    Render command output in a structured, text-only format.
    """
    if "error" in result:
        return f"ERROR: {result['error']}"

    content = result.get("content", "")

    if isinstance(content, dict):
        lines = []
        for key, value in content.items():
            lines.append(f"{key.upper()}:")
            lines.append(str(value))
            lines.append("")
        return "\n".join(lines).strip()

    if isinstance(content, list):
        return "\n".join(content)

    return str(content)
