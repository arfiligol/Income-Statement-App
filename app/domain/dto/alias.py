from dataclasses import dataclass, field
from typing import List


@dataclass
class Alias:
    """
    Represents an alias rule for extracting lawyer codes from text.
    source_code: The keyword found in Excel Summary.
    target_codes: The list of actual lawyer codes it maps to.
    """

    source_code: str
    target_codes: List[str] = field(default_factory=list)
