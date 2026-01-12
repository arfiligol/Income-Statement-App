"""Workflow page with tabs for different workflow features."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from src.views.components.cards import Card
from src.views.components.inputs import FilePathInput
from src.views.components.buttons import PrimaryButton
from src.views.components.labels import StatusLabel
from src.views.pages.workflow.auto_fill_tab import AutoFillTab
from src.views.pages.workflow.separate_ledger_tab import SeparateLedgerTab


class WorkflowPage(QWidget):
    """Workflow page containing source selection, tabs, and submit action."""

    selectSourceRequested: Signal = Signal()
    selectOutputDirRequested: Signal = Signal()
    tabChanged: Signal = Signal(str)  # Emits action name
    submitRequested: Signal = Signal()

    # Action name mapping
    ACTION_MAP = {
        0: "auto_fill_remark",
        1: "separate_the_ledger",
    }

    # Instance variable type annotations
    source_card: Card
    source_input: FilePathInput
    tab_widget: QTabWidget
    auto_fill_tab: AutoFillTab
    separate_ledger_tab: SeparateLedgerTab
    status_label: StatusLabel
    submit_button: PrimaryButton

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Source file selection card
        self.source_card = Card()
        self.source_input = FilePathInput(
            label="來源檔案",
            button_text="選擇檔案",
            placeholder="尚未選擇來源檔案",
        )
            placeholder="尚未選擇來源檔案",
        )
        _ = self.source_input.browse_button.clicked.connect(
            self.selectSourceRequested.emit
        )
        self.source_card.add_widget(self.source_input)
        layout.addWidget(self.source_card)

        # Workflow tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        self.auto_fill_tab = AutoFillTab()
        self.separate_ledger_tab = SeparateLedgerTab()
        self.auto_fill_tab = AutoFillTab()
        self.separate_ledger_tab = SeparateLedgerTab()
        _ = self.separate_ledger_tab.selectOutputDirRequested.connect(
            self.selectOutputDirRequested.emit
        )

        _ = self.tab_widget.addTab(self.auto_fill_tab, "摘要抓律師代碼")
        _ = self.tab_widget.addTab(self.separate_ledger_tab, "律師收入明細")
        _ = self.tab_widget.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tab_widget, 1)

        # Submit section
        submit_card = Card()
        submit_row = QHBoxLayout()
        submit_row.setSpacing(12)

        self.status_label = StatusLabel("")
        submit_row.addWidget(self.status_label, 1)

        self.submit_button = PrimaryButton("執行功能 (Submit)")
        self.submit_button = PrimaryButton("執行功能 (Submit)")
        _ = self.submit_button.clicked.connect(self.submitRequested.emit)
        submit_row.addWidget(self.submit_button)

        submit_card.add_layout(submit_row)
        layout.addWidget(submit_card)

        # Initialize with first tab
        self._on_tab_changed(0)

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change and emit action name."""
        action_name = self.ACTION_MAP.get(index, "")
        if action_name:
            self.tabChanged.emit(action_name)

    # Public interface methods
    def set_source_path(self, path: str) -> None:
        """Set the source file path display."""
        self.source_input.set_path(path)

    def set_output_dir(self, path: str) -> None:
        """Set the output directory path display."""
        self.separate_ledger_tab.set_output_dir(path)

    def get_output_filename(self) -> str:
        """Get the output filename from the separate ledger tab."""
        return self.separate_ledger_tab.get_output_filename()

    def set_status_message(self, message: str) -> None:
        """Set the status message."""
        self.status_label.setText(message)

    def set_submit_state(self, state: str) -> None:
        """Set the submit button state (success, warning, danger)."""
        self.submit_button.setProperty("class", f"primary {state}")
        self.submit_button.style().unpolish(self.submit_button)
        self.submit_button.style().polish(self.submit_button)

    def get_current_action(self) -> str:
        """Get the current workflow action based on active tab."""
        return self.ACTION_MAP.get(self.tab_widget.currentIndex(), "")
