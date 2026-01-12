"""Reusable button components with consistent styling."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy


class PrimaryButton(QPushButton):
    """A primary action button with prominent styling."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "primary")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(36)


class SecondaryButton(QPushButton):
    """A secondary action button with subtle styling."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "secondary")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(36)


class IconButton(QPushButton):
    """A button designed for icons (e.g., hamburger menu)."""

    def __init__(self, text: str = "", parent=None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "icon-button")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(44, 44)
        self.setFlat(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 24px;
                font-weight: bold;
                color: #b0bec5;
            }
            QPushButton:hover {
                background-color: rgba(144, 202, 249, 0.15);
                border-radius: 8px;
                color: #90caf9;
            }
            QPushButton:pressed {
                background-color: rgba(144, 202, 249, 0.3);
            }
        """)


class NavButton(QPushButton):
    """A navigation button for sidebar items."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "nav-button")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(44)
