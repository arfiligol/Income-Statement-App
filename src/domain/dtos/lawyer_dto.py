from dataclasses import dataclass

@dataclass
class LawyerDTO:
    """Data Transfer Object for Lawyer."""
    code: str
    name: str | None = None
