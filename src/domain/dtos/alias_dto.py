from dataclasses import dataclass

@dataclass
class AliasDTO:
    """Data Transfer Object for Lawyer Code Alias."""
    source_code: str
    target_codes: list[str]

    @property
    def target_codes_str(self) -> str:
        """Returns target codes as a comma-separated string."""
        return ", ".join(self.target_codes)
