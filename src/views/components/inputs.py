"""Reusable input components with consistent styling."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QLabel, QPushButton, QWidget


class StyledLineEdit(QLineEdit):
    """A styled text input field."""

    def __init__(self, placeholder: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setProperty("class", "styled-input")
        self.setMinimumHeight(36)


class FilePathInput(QWidget):
    """A composite widget for file/directory path selection."""

    def __init__(
        self,
        label: str,
        button_text: str = "選擇",
        placeholder: str = "尚未選擇",
        parent=None,
    ) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.label = QLabel(label)
        self.label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.path_display = QLabel(placeholder)
        self.path_display.setProperty("class", "path-display")
        self.path_display.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.browse_button = QPushButton(button_text)
        self.browse_button.setProperty("class", "secondary")
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.label)
        layout.addWidget(self.path_display, 1)
        layout.addWidget(self.browse_button)

    def set_path(self, path: str) -> None:
        """Update the displayed path."""
        self.path_display.setText(path)

    def get_path(self) -> str:
        """Get the currently displayed path."""
        return self.path_display.text()
