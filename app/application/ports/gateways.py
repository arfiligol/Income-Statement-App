from typing import Optional, Protocol

from app.domain.dto.auto_fill import AutoFillPrompt, AutoFillResponse
from app.domain.dto.file_source import FileSource


class FilePickerGateway(Protocol):
    """
    Interface for file selection.
    """

    async def pick_file(self) -> Optional[FileSource]:
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
