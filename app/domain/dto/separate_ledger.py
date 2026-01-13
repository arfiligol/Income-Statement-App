from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SeparateLedgerRow:
    date: str
    abstract: str
    department: str
    debit: int
    credit: int
    lawyer_code: str


@dataclass
class SeparateLedgerResult:
    rows: list[SeparateLedgerRow]
    total_debit: int
    total_credit: int
    output_path: str = ""
