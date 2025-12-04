from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from src.controllers import AppController
from src.views.main_window import MainWindow
from src.theme import DEFAULT_THEME, DEFAULT_EXTRA


def run(theme: str = DEFAULT_THEME, extra: dict | None = None) -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica Neue", 11))
    apply_stylesheet(app, theme=theme, extra=extra or DEFAULT_EXTRA)

    window = MainWindow()
    controller = AppController(window)
    window.controller = controller
    window.show()

    sys.exit(app.exec())
