from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class StatementLineItem:
    """Represents a single line item in the income statement."""

    year: int
    month: int
    description: str
    amount: float
    category: Optional[str] = None
    remarks: Optional[str] = None


@dataclass
class Statement:
    """
    Represents the full income statement data structure.
    This DTO is the main currency between Application and UI layers.
    """

    items: list[StatementLineItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_amount(self) -> float:
        return sum(item.amount for item in self.items)

    def add_item(self, item: StatementLineItem):
        self.items.append(item)
