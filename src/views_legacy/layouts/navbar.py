"""Top navigation bar component."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget

from src.views.components.buttons import IconButton


class Navbar(QFrame):
    """Top navigation bar with hamburger menu, title, and action buttons."""

    hamburgerClicked: Signal = Signal()
    updateClicked: Signal = Signal()

    hamburger_btn: IconButton
    title_label: QLabel
    update_btn: IconButton

    def __init__(
        self,
        title: str = "Income Statement App",
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setProperty("class", "navbar")
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 16, 0)
        layout.setSpacing(8)

        # Hamburger menu button
        self.hamburger_btn = IconButton("☰")
        self.hamburger_btn.setToolTip("Toggle sidebar")
        _ = self.hamburger_btn.clicked.connect(self.hamburgerClicked.emit)
        layout.addWidget(self.hamburger_btn)

        # App title
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "app-title")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding-left: 8px;")
        layout.addWidget(self.title_label)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(spacer)

        # Update notification button (hidden by default)
        self.update_btn = IconButton("⬆")
        self.update_btn.setToolTip("發現新版本 (點擊更新)")
        self.update_btn.setVisible(False)
        _ = self.update_btn.clicked.connect(self.updateClicked.emit)
        layout.addWidget(self.update_btn)

    def show_update_available(self, version: str) -> None:
        """Show the update button with version info."""
        self.update_btn.setToolTip(f"發現新版本 v{version} (點擊更新)")
        self.update_btn.setVisible(True)

    def hide_update(self) -> None:
        """Hide the update button."""
        self.update_btn.setVisible(False)
