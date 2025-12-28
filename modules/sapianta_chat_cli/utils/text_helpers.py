def normalize_text(text: str) -> str:
    """
    Normalize text for display purposes.
    """
    return text.strip()


def extract_section(text: str, header: str) -> str:
    """
    Extract a markdown section starting with '## <header>'
    until the next '## ' header or end of text.
    """
    lines = text.splitlines()
    start_index = None
    collected = []

    for i, line in enumerate(lines):
        if line.strip().lower() == f"## {header.lower()}":
            start_index = i + 1
            break

    if start_index is None:
        return ""

    for line in lines[start_index:]:
        if line.startswith("## "):
            break
        collected.append(line)

    return "\n".join(collected).strip()


def first_paragraph(text: str) -> str:
    """
    Return the first non-empty paragraph from the text.
    """
    for block in text.split("\n\n"):
        cleaned = block.strip()
        if cleaned:
            return cleaned
    return ""
