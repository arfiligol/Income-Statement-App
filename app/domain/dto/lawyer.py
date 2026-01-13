from dataclasses import dataclass


@dataclass
class Lawyer:
    """
    Represents a lawyer entity in the domain.
    """

    code: str
    name: str = ""  # Optional name, defaults to empty if not set
