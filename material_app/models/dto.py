from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AppState:
    """Container for front-end state shared between view and controller."""

    source_path: Optional[str] = None
    output_dir: Optional[str] = None
    selected_action: Optional[str] = None
    output_filename: Optional[str] = None
