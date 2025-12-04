from __future__ import annotations

from PySide6.QtCore import QObject

from src.models import AppState
from src.views.main_window import MainWindow
from .workflow_controller import WorkflowController


class AppController(QObject):
    """Top-level application controller that orchestrates page controllers."""

    def __init__(self, window: MainWindow) -> None:
        super().__init__(window)
        self.window = window
        self.state = AppState()

        self.workflow_controller = WorkflowController(window, self.state.workflow)
        # Placeholder: self.database_controller = DatabaseController(...)
