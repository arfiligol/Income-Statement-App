from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class AutoFillPrompt:
    """Prompt data for user interaction when auto-fill is unsure."""

    summary: str
    row_number: int
    matched_codes: List[str] = field(default_factory=list)
    available_codes: List[str] = field(default_factory=list)


@dataclass
class AutoFillResponse:
    """User response to an auto-fill prompt."""

    selected_codes: List[str]
    action: str = "submit"  # submit, skip, skip_all, abort


@dataclass
class AutoFillResult:
    updated_count: int = 0
    is_completed: bool = False
