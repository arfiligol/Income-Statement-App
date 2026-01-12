"""Collapsible sidebar component for navigation."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QButtonGroup

from src.views.components.buttons import NavButton


class Sidebar(QFrame):
    """Collapsible sidebar with navigation items."""

    navigationChanged: Signal = Signal(str)  # Emits the navigation target name

    _nav_group: QButtonGroup
    _nav_buttons: dict[str, NavButton]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("class", "sidebar")
        self.setFixedWidth(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(8)

        # Navigation button group (exclusive selection)
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        # Navigation items
        self._nav_buttons: dict[str, NavButton] = {}

        # Add default navigation items
        self._add_nav_item("workflow", "📋 工作包", layout)
        self._add_nav_item("database", "💾 資料庫操作", layout)
        self._add_nav_item("settings", "⚙️ 設定", layout)

        layout.addStretch(1)

        # Connect button group signal
        _ = self._nav_group.buttonClicked.connect(self._on_nav_clicked)

        # Default selection
        self._nav_buttons["workflow"].setChecked(True)

    def _add_nav_item(self, name: str, text: str, layout: QVBoxLayout) -> None:
        """Add a navigation item to the sidebar."""
        btn = NavButton(text)
        btn.setProperty("nav-target", name)
        self._nav_buttons[name] = btn
        self._nav_group.addButton(btn)
        layout.addWidget(btn)

    def _on_nav_clicked(self, button) -> None:
        """Handle navigation button click."""
        target = button.property("nav-target")
        if target and isinstance(target, str):
            self.navigationChanged.emit(target)

    def select_item(self, name: str) -> None:
        """Programmatically select a navigation item."""
        if name in self._nav_buttons:
            self._nav_buttons[name].setChecked(True)

    def toggle_visibility(self) -> None:
        """Toggle sidebar visibility."""
        self.setVisible(not self.isVisible())
