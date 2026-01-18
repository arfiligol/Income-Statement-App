from dataclasses import dataclass, field


@dataclass
class AutoFillPrompt:
    """Prompt data for user interaction when auto-fill is unsure."""

    summary: str
    row_number: int
    matched_codes: list[str] = field(default_factory=list)
    available_codes: list[str] = field(default_factory=list)


@dataclass
class AutoFillResponse:
    """User response to an auto-fill prompt."""

    selected_codes: list[str]
    action: str = "submit"  # submit, skip, skip_all, abort


@dataclass
class AutoFillResult:
    updated_count: int = 0
    is_completed: bool = False
