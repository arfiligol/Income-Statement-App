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
        self.setFixedSize(40, 40)
        self.setFlat(True)


class NavButton(QPushButton):
    """A navigation button for sidebar items."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "nav-button")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(44)
