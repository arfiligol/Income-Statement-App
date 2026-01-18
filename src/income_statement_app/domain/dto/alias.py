from dataclasses import dataclass, field


@dataclass
class Alias:
    """
    Represents an alias rule for extracting lawyer codes from text.
    source_code: The keyword found in Excel Summary.
    target_codes: The list of actual lawyer codes it maps to.
    """

    source_code: str
    target_codes: list[str] = field(default_factory=list)
