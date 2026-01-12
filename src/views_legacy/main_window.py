"""Main application window assembling Navbar, Sidebar, and ContentArea."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from qt_material import QtStyleTools

from src.views.layouts import Navbar, Sidebar, ContentArea
from src.views.pages.workflow import WorkflowPage
from src.views.pages.database_page import DatabasePage

if TYPE_CHECKING:
    from src.controllers.app_controller import AppController


class MainWindow(QtStyleTools, QMainWindow):
    """Modern main window with hamburger menu, collapsible sidebar, and content area."""

    # Signals for controller communication
    selectSourceRequested: Signal = Signal()
    selectOutputDirRequested: Signal = Signal()
    actionSelected: Signal = Signal(str)
    submitRequested: Signal = Signal()
    updateRequested: Signal = Signal()

    # Instance variable type annotations
    navbar: Navbar
    sidebar: Sidebar
    content_area: ContentArea
    workflow_page: WorkflowPage
    database_page: DatabasePage
    settings_page: QWidget

    def __init__(self) -> None:
        super().__init__()

        # Controller reference (set by AppController)
        self.controller: AppController | None = None

        self.setWindowTitle("Income Statement App")
        self.resize(1100, 720)

        # Apply qt_material extra settings
        self.extra: dict[str, str] = {
            "danger": "#dc3545",
            "warning": "#ffc107",
            "success": "#17a2b8",
            "font_family": "Roboto",
            "density_scale": "0",
            "button_shape": "default",
        }
        self.set_extra(self.extra)  # pyright: ignore[reportUnknownMemberType]

        # Build the UI
        self._build_ui()
        self._wire_signals()

    def _build_ui(self) -> None:
        """Build the main window layout."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main horizontal layout (Sidebar on left, Navbar + Content on right)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (full height on left)
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Right side (Navbar on top, Content below)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Navbar
        self.navbar = Navbar(title="Income Statement App v0.1.5")
        right_layout.addWidget(self.navbar)

        # Content Area
        self.content_area = ContentArea()

        # Create and add pages
        self.workflow_page = WorkflowPage()
        self.database_page = DatabasePage()
        self.settings_page = self._create_placeholder_page("設定頁面 (開發中)")

        self.content_area.add_page("workflow", self.workflow_page)
        self.content_area.add_page("database", self.database_page)
        self.content_area.add_page("settings", self.settings_page)

        right_layout.addWidget(self.content_area, 1)

        main_layout.addWidget(right_container, 1)

        # Show default page
        _ = self.content_area.show_page("workflow")

    def _create_placeholder_page(self, text: str) -> QWidget:
        """Create a placeholder page for development."""
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #666;")
        layout.addWidget(label)
        return page

    def _wire_signals(self) -> None:
        """Connect internal signals to external signals."""
        # Navbar signals
        _ = self.navbar.hamburgerClicked.connect(self.sidebar.toggle_visibility)
        _ = self.navbar.updateClicked.connect(self.updateRequested.emit)

        # Sidebar navigation
        _ = self.sidebar.navigationChanged.connect(self._on_navigation_changed)

        # Workflow page signals
        _ = self.workflow_page.selectSourceRequested.connect(self.selectSourceRequested.emit)
        _ = self.workflow_page.selectOutputDirRequested.connect(self.selectOutputDirRequested.emit)
        _ = self.workflow_page.tabChanged.connect(self.actionSelected.emit)
        _ = self.workflow_page.submitRequested.connect(self.submitRequested.emit)

    @Slot(str)
    def _on_navigation_changed(self, target: str) -> None:
        """Handle sidebar navigation change."""
        _ = self.content_area.show_page(target)

    # Public interface methods (for controller)
    def set_source_path(self, path: str) -> None:
        """Set the source file path."""
        self.workflow_page.set_source_path(path)

    def set_output_dir(self, path: str) -> None:
        """Set the output directory path."""
        self.workflow_page.set_output_dir(path)

    def set_status_message(self, message: str) -> None:
        """Set the status message."""
        self.workflow_page.set_status_message(message)

    def set_selected_action(self, action_name: str | None) -> None:
        """Set the selected action (for compatibility)."""
        # The new WorkflowPage automatically handles this via tabs
        pass

    def set_submit_state(self, state: str) -> None:
        """Set the submit button state."""
        self.workflow_page.set_submit_state(state)

    @property
    def current_view(self) -> str:
        """Get the current view name."""
        return self.content_area.current_page_name() or "workflow"

    def get_output_filename(self) -> str:
        """Get the output filename."""
        return self.workflow_page.get_output_filename()

    def get_current_action(self) -> str:
        """Get the current workflow action."""
        return self.workflow_page.get_current_action()

    @Slot(str)
    def show_update_message(self, version: str) -> None:
        """Show the update available notification."""
        self.navbar.show_update_available(version)
