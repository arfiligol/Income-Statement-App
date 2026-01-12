"""Reusable label components with consistent styling."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


class SectionTitle(QLabel):
    """A styled section title label."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "section-title")
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)


class StatusLabel(QLabel):
    """A label for displaying status messages."""

    def __init__(self, text: str = "", parent=None) -> None:
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

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "description")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
