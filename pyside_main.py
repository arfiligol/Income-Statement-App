from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from material_app.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica Neue", 11))
    extra = {
        "danger": "#dc3545",
        "warning": "#ffc107",
        "success": "#17a2b8",
        "font_family": "Roboto",
        "density_scale": "0",
        "button_shape": "default",
    }
    apply_stylesheet(app, theme="dark_blue.xml", extra=extra)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
