from __future__ import annotations

from threading import Thread
from typing import Optional

from PySide6.QtCore import QObject, Slot

from src import __version__
from src.models import AppState
from src.services.update_service import UpdateService, UpdateInfo
from src.views.main_window import MainWindow
from .workflow_controller import WorkflowController


class AppController(QObject):
    """Top-level application controller that orchestrates page controllers."""

    def __init__(self, window: MainWindow) -> None:
        super().__init__(window)
        self.window: MainWindow = window
        self.state: AppState = AppState()

        self.workflow_controller: WorkflowController = WorkflowController(
            window, self.state.workflow
        )
        # Placeholder: self.database_controller = DatabaseController(...)

        # Update Service
        self.update_service = UpdateService(current_version=__version__)
        self.window.updateRequested.connect(self.on_update_requested)

        # Check for updates in background
        self._check_update_thread = Thread(target=self._check_updates, daemon=True)
        self._check_update_thread.start()

    def _check_updates(self) -> None:
        update_info = self.update_service.check_for_updates()
        if update_info:
            # Update UI in main thread (using rudimentary polling or signal if we had one,
            # ideally should use QThread/Signal, but invokeMethod or simply checking visible
            # state is safer. Since we are in a controller, we can't easily emit to UI from thread
            # without signals. Let's rely on atomic update of state or just risk it for this simple app,
            # OR better: use variable and poll, or proper signal.)
            #
            # Best practice: define a signal on Controller or use QMetaObject.
            # Here I will use QMetaObject.invokeMethod to be thread-safe.
            from PySide6.QtCore import QMetaObject, Qt, Q_ARG

            QMetaObject.invokeMethod(
                self.window,
                "show_update_message",
                Qt.QueuedConnection,
                Q_ARG(str, update_info.version),
            )

    @Slot()
    def on_update_requested(self) -> None:
        update_info = self.update_service.get_available_update()
        if update_info:
            self.window.set_status_message("正在下載更新，請稍候...")
            self.window.set_submit_state("warning")
            # This runs in background thread
            self.update_service.perform_update(update_info)
