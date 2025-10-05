from __future__ import annotations

from PySide6.QtCore import QObject

from material_app.models.dto import AppState
from material_app.views.main_window import MainWindow
from .workflow_controller import WorkflowController


class AppController(QObject):
    """Top-level application controller that orchestrates page controllers."""

    def __init__(self, window: MainWindow) -> None:
        super().__init__(window)
        self.window = window
        self.state = AppState()

        self.workflow_controller = WorkflowController(window, self.state)
        # Placeholder: self.database_controller = DatabaseController(...)

