from __future__ import annotations

INVALID_FILENAME_CHARS = '<>:"/\\|?*'

def filename_has_invalid_chars(filename: str) -> bool:
    return any(char in INVALID_FILENAME_CHARS for char in filename)
