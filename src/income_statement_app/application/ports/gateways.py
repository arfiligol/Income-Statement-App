from typing import Protocol


from income_statement_app.common.types import Result
from income_statement_app.domain.dto.auto_fill import AutoFillPrompt, AutoFillResponse
from income_statement_app.domain.dto.file_source import FileSource
from income_statement_app.domain.dto.separate_ledger import SeparateLedgerResult


class FilePickerGateway(Protocol):
    """
    Interface for file selection.
    """

    async def pick_file(self) -> FileSource | None:
        """Triggers the file picking process and returns a FileSource if successful."""
        ...


class NotificationGateway(Protocol):
    """Interface for user notifications (Toast, Dialog, etc.)."""

    def show_toast(self, message: str, type: str = "info") -> None: ...
    def show_error(self, message: str) -> None: ...


class UserInteractionGateway(Protocol):
    """Interface for direct user interaction (Dialogs)."""

    async def select_lawyers(self, prompt: AutoFillPrompt) -> AutoFillResponse:
        """Asks the user to select lawyers from a list."""
        ...


class ReportGateway(Protocol):
    """Interface for generating reports."""

    def generate_ledger_report(
        self, data: SeparateLedgerResult, output_path: str
    ) -> Result[str, Exception]:
        """Generates the separate ledger Excel report."""
        ...
