"""Reusable input components with consistent styling."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget


class StyledLineEdit(QLineEdit):
    """A styled text input field."""

    def __init__(self, placeholder: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setProperty("class", "styled-input")
        self.setMinimumHeight(36)
        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.05); "
            "border: 1px solid rgba(255, 255, 255, 0.1); "
            "border-radius: 6px; "
            "padding: 8px 12px; "
            "color: #e0e0e0; "
            "font-size: 15px;"
        )


class LabeledInput(QWidget):
    """A text input with a label on top for clear visual hierarchy."""

    def __init__(
        self,
        label: str,
        placeholder: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Label on top
        self.label = QLabel(label)
        self.label.setStyleSheet("font-weight: bold; color: #90caf9; font-size: 15px;")
        layout.addWidget(self.label)

        # Input field
        self.input_field = StyledLineEdit(placeholder)
        layout.addWidget(self.input_field)

    def text(self) -> str:
        """Get the input text."""
        return self.input_field.text()

    def setText(self, text: str) -> None:
        """Set the input text."""
        self.input_field.setText(text)


class FilePathInput(QWidget):
    """A composite widget for file/directory path selection with clear visual hierarchy."""

    def __init__(
        self,
        label: str,
        button_text: str = "選擇",
        placeholder: str = "尚未選擇",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        # Label on top
        self.label = QLabel(label)
        self.label.setProperty("class", "field-label")
        self.label.setStyleSheet("font-weight: bold; color: #90caf9; font-size: 15px;")
        main_layout.addWidget(self.label)

        # Input row (path display + button)
        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(12)

        self.path_display = QLabel(placeholder)
        self.path_display.setProperty("class", "path-display")
        self.path_display.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.05); "
            "border: 1px solid rgba(255, 255, 255, 0.1); "
            "border-radius: 6px; "
            "padding: 8px 12px; "
            "color: #b0bec5; "
            "font-size: 15px;"
        )
        self.path_display.setMinimumHeight(36)

        self.browse_button = QPushButton(button_text)
        self.browse_button.setProperty("class", "secondary")
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.setMinimumWidth(100)

        input_row.addWidget(self.path_display, 1)
        input_row.addWidget(self.browse_button)

        main_layout.addLayout(input_row)

    def set_path(self, path: str) -> None:
        """Update the displayed path."""
        self.path_display.setText(path)
        self.path_display.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.05); "
            "border: 1px solid rgba(144, 202, 249, 0.3); "
            "border-radius: 6px; "
            "padding: 8px 12px; "
            "color: #e0e0e0; "
            "font-size: 15px;"
        )

    def get_path(self) -> str:
        """Get the currently displayed path."""
        return self.path_display.text()
