"""
String Formatting Utilities - FAZA 31 Extended Preflight
"""


def capitalize_words(text):
    """Capitalize first letter of each word."""
    return ' '.join(word.capitalize() for word in text.split())


def reverse_string(text):
    """Reverse the string."""
    return text[::-1]


def truncate(text, max_length, suffix='...'):
    """Truncate text to max_length, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def pad_left(text, width, char=' '):
    """Pad text on the left to reach width."""
    return text.rjust(width, char)


def pad_right(text, width, char=' '):
    """Pad text on the right to reach width."""
    return text.ljust(width, char)


def center(text, width, char=' '):
    """Center text within width."""
    return text.center(width, char)


def remove_whitespace(text):
    """Remove all whitespace from text."""
    return ''.join(text.split())