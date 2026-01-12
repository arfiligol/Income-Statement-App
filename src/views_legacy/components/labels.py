"""Reusable label components with consistent styling."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QFrame


class SectionTitle(QLabel):
    """A styled section title label with optional icon."""

    def __init__(
        self,
        text: str,
        icon: str = "",
        parent: QWidget | None = None,
    ) -> None:
        display_text = f"{icon}  {text}" if icon else text
        super().__init__(display_text, parent)
        self.setStyleSheet(
            "font-size: 16px; "
            "font-weight: bold; "
            "color: #ffffff; "
            "padding: 4px 0; "
            "border-bottom: 2px solid rgba(144, 202, 249, 0.3);"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)


class StatusLabel(QLabel):
    """A label for displaying status messages."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "status-label")
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

    def set_status(self, message: str, status_type: str = "info") -> None:
        """Set the status message and type (info, success, warning, danger)."""
        self.setText(message)
        self.setProperty("status", status_type)
        self.style().unpolish(self)
        self.style().polish(self)


class DescriptionLabel(QLabel):
    """A label for displaying descriptive text."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setStyleSheet("color: #b0bec5; font-size: 15px; line-height: 1.5;")
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)


class InstructionBox(QFrame):
    """A styled box for displaying instructions with an icon header."""

    def __init__(
        self,
        title: str = "使用說明",
        instructions: list[str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setStyleSheet(
            "background-color: rgba(144, 202, 249, 0.08); "
            "border: 1px solid rgba(144, 202, 249, 0.2); "
            "border-radius: 8px; "
            "padding: 12px;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Header with icon
        header = QLabel(f"📋 {title}")
        header.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #90caf9; "
            "background: transparent; border: none; padding: 0;"
        )
        layout.addWidget(header)

        # Instruction items
        if instructions:
            for i, instruction in enumerate(instructions, 1):
                item = QLabel(f"{i}. {instruction}")
                item.setWordWrap(True)
                item.setStyleSheet(
                    "color: #b0bec5; font-size: 14px; "
                    "background: transparent; border: none; padding: 0;"
                )
                layout.addWidget(item)


class LogDisplay(QFrame):
    """A log-style display area for status messages and operation feedback."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.3); "
            "border: 1px solid rgba(255, 255, 255, 0.1); "
            "border-radius: 6px;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Header
        header = QLabel("📝 執行狀態")
        header.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #78909c; "
            "background: transparent; border: none;"
        )
        layout.addWidget(header)

        # Status message
        self._status_label = QLabel("準備就緒")
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet(
            "font-size: 15px; color: #e0e0e0; "
            "background: transparent; border: none; "
            "font-family: 'SF Mono', 'Consolas', monospace;"
        )
        layout.addWidget(self._status_label)

    def set_message(self, message: str, msg_type: str = "info") -> None:
        """Set the log message with type-based coloring."""
        colors = {
            "info": "#e0e0e0",
            "success": "#81c784",
            "warning": "#ffb74d",
            "error": "#ef5350",
        }
        color = colors.get(msg_type, "#e0e0e0")
        self._status_label.setText(message)
        self._status_label.setStyleSheet(
            f"font-size: 15px; color: {color}; "
            "background: transparent; border: none; "
            "font-family: 'SF Mono', 'Consolas', monospace;"
        )
