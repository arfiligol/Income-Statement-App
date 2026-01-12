from typing import Protocol,runtime_checkable

@runtime_checkable
class UserInteractionProvider(Protocol):
    """Interface for services to request user interaction."""

    def confirm(self, title: str, message: str) -> bool:
        """Prompt user for confirmation."""
        ...

    def show_message(self, title: str, message: str) -> None:
        """Show a message to the user."""
        ...

    def select_lawyers(self, summary_text: str, row_number: int, available_codes: list[str]) -> tuple[list[str], str]:
        """
        Prompt user to select lawyers.
        Returns: (selected_codes, action)
        action can be 'confirm', 'skip_all', 'skip_single', 'abort'
        """
        ...
        
    # Maybe add file picker methods here if Service needs to ask for files?
    # Usually Service receives paths from UI, so maybe not needed generally.
