from __future__ import annotations

from threading import Thread
from typing import Optional

from PySide6.QtCore import QObject, Slot

from src.version import __version__
from src.models import AppState
from src.services.update_service import UpdateService, UpdateInfo
from src.views.main_window import MainWindow
from .workflow_controller import WorkflowController
from src.views.dialogs.update_dialog import UpdateProgressDialog


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
            from PySide6.QtCore import QMetaObject, Qt, Q_ARG

            QMetaObject.invokeMethod(
                self.window,
                "show_update_message",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, update_info.version),
            )

    @Slot()
    def on_update_requested(self) -> None:
        """Handle the user's request to update the application."""
        update_info = self.update_service.get_available_update()
        if not update_info:
            return

        # Create and show the modal dialog
        self.update_dialog = UpdateProgressDialog(self.window)

        # Wire up cancellation
        # Note: We need to use lambda or partial if we want to pass arguments,
        # but here cancel_update takes no arguments.
        # Direct connection is safe because update_service.cancel_update is thread-safe (just sets a flag).
        self.update_dialog.canceled.connect(self.update_service.cancel_update)

        # Define callbacks that update the dialog via invokeMethod for thread safety
        from PySide6.QtCore import QMetaObject, Qt, Q_ARG, QTimer

        def progress_wrapper(val: int):
            QMetaObject.invokeMethod(
                self.update_dialog,
                "update_progress",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(int, val),
            )

        def error_wrapper(msg: str):
            QMetaObject.invokeMethod(
                self.update_dialog,
                "show_error",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, msg),
            )

        def completion_wrapper(msi_path: str):
            # 1. Show success message
            QMetaObject.invokeMethod(
                self.update_dialog,
                "show_success",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, "下載完成！即將啟動安裝程式..."),
            )

            # 2. Launch installer after a short delay (to let user see the message)
            # We use QTimer.singleShot in the main thread (invoked via invokeMethod indirectly or assume invokeMethod runs slot in main thread)
            # Actually, completion_wrapper runs in the background thread.
            # We can't use QTimer directly easily from here without correct context.
            # Better to have a slot in AppController or MainWindow to handle "finish update".
            # Or invoke a lambda.

            def launch():
                self.update_service.launch_installer_and_exit(msi_path)

            # We want to schedule 'launch' to run in the main thread or just run it via service
            # (launch_installer_and_exit uses os.startfile and sys.exit, works from any thread usually,
            # but sys.exit might kill thread only? No, sys.exit in thread raises SystemExit in thread.
            # We need to exit the main process.)
            # os._exit might be needed if sys.exit only kills thread.
            # UpdateService.launch_installer_and_exit uses sys.exit(0).
            # In a thread, sys.exit() just kills the thread.
            # We MUST trigger main thread exit.

            # Let's use QMetaObject to invoke a method on self (AppController is QObject) that handles the launch.
            QMetaObject.invokeMethod(
                self,
                "finalize_update",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, msi_path),
            )

        self.update_service.perform_update(
            update_info,
            progress_callback=progress_wrapper,
            error_callback=error_wrapper,
            completion_callback=completion_wrapper,
        )

        # Block until dialog is closed
        self.update_dialog.exec()

    @Slot(str)
    def finalize_update(self, msi_path: str):
        """Called when update download is complete. Launches installer and exits."""
        # Wait a bit to let the user read the 'Success' message
        from PySide6.QtCore import QTimer

        # 3000ms delay
        QTimer.singleShot(
            3000, lambda: self.update_service.launch_installer_and_exit(msi_path)
        )
