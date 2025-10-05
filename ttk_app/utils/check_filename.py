from __future__ import annotations


def check_filename_is_valid(filename: str) -> bool:
    invalid_chars = '<>:"/\\|?*'
    return any(char in invalid_chars for char in filename)
