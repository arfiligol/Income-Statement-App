from dataclasses import dataclass


@dataclass
class CodeReplacement:
    """
    Represents a rule to replace a single Lawyer Code with a list of Lawyer Codes.
    """

    id: int | None
    source_code: str
    target_codes: str
