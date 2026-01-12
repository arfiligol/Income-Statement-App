from dataclasses import dataclass

@dataclass(frozen=True)
class SeparateLedgerResultDTO:
    """Result payload for the separate-the-ledger workflow."""
    rows: list[list[object]]
    total_debit: int
    total_credit: int


@dataclass(frozen=True)
class AutoFillResultDTO:
    """Result payload for auto-fill workflow."""
    updated_count: int


@dataclass(frozen=True)
class AutoFillPromptDTO:
    summary: str
    row_number: int
    known_codes: list[str]


@dataclass(frozen=True)
class AutoFillResponseDTO:
    selected_codes: list[str]
    skip_remaining: bool = False
