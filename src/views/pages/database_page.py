from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DatabasePage(QWidget):
    """Placeholder for database management UI."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addStretch(1)

        label = QLabel("資料庫操作頁面開發中…")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty("class", "section-title")
        layout.addWidget(label)

        layout.addStretch(1)
