"""Main content area component using QStackedWidget."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QStackedWidget, QVBoxLayout, QWidget


class ContentArea(QFrame):
    """Main content container that holds stacked pages."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("class", "content-area")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        # Page name to widget mapping
        self._pages: dict[str, QWidget] = {}

    def add_page(self, name: str, widget: QWidget) -> None:
        """Add a page to the content area."""
        self._pages[name] = widget
        self._stack.addWidget(widget)

    def show_page(self, name: str) -> bool:
        """Switch to the specified page. Returns True if successful."""
        if name in self._pages:
            self._stack.setCurrentWidget(self._pages[name])
            return True
        return False

    def current_page_name(self) -> str | None:
        """Get the name of the currently visible page."""
        current = self._stack.currentWidget()
        for name, widget in self._pages.items():
            if widget is current:
                return name
        return None

    def get_page(self, name: str) -> QWidget | None:
        """Get a page widget by name."""
        return self._pages.get(name)
