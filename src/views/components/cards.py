"""Reusable card components for content containers."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QLayout


class Card(QFrame):
    """A styled container with rounded corners and subtle shadow."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("class", "card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

    def add_widget(self, widget: QWidget) -> None:
        """Add a widget to the card's layout."""
        self._layout.addWidget(widget)

    def add_layout(self, layout: QLayout) -> None:
        """Add a layout to the card's layout."""
        self._layout.addLayout(layout)


class InfoCard(Card):
    """A card displaying informational content with a title."""

    def __init__(self, title: str, description: str = "", parent=None) -> None:
        super().__init__(parent)

        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "section-title")
        self._layout.addWidget(self.title_label)

        if description:
            self.description_label = QLabel(description)
            self.description_label.setWordWrap(True)
            self.description_label.setProperty("class", "description")
            self._layout.addWidget(self.description_label)


class FormCard(Card):
    """A card designed to contain form elements."""

    def __init__(
        self,
        title: str = "",
        icon: str = "⚙️",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        if title:
            from src.views.components.labels import SectionTitle
            self.title_label = SectionTitle(title, icon=icon)
            self._layout.addWidget(self.title_label)
