from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from src.controllers.app_controller import AppController
from src.views.main_window import MainWindow
from src.theme import DEFAULT_THEME, DEFAULT_EXTRA


def run(theme: str = DEFAULT_THEME, extra: dict[str, str] | None = None) -> None:
    print("DEBUG: Application starting...")
    try:
        app = QApplication(sys.argv)
        print("DEBUG: QApplication created")
        app.setFont(QFont("Helvetica Neue", 11))
        apply_stylesheet(app, theme=theme, extra=extra or DEFAULT_EXTRA)
        print("DEBUG: Stylesheet applied")

        window = MainWindow()
        print("DEBUG: MainWindow created")
        controller = AppController(window)
        window.controller = controller
        window.show()
        print("DEBUG: Window shown, entering event loop")

        sys.exit(app.exec())
    except Exception as e:
        import traceback
        print("CRITICAL ERROR:")
        traceback.print_exc()
        input("Press Enter to exit...")
