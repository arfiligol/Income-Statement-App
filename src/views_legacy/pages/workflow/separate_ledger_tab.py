"""Separate Ledger tab content for the Workflow page."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.views.components.cards import FormCard
from src.views.components.inputs import FilePathInput, LabeledInput


class SeparateLedgerTab(QWidget):
    """Tab content for the Separate Ledger feature with output configuration."""

    selectOutputDirRequested: Signal = Signal()

    output_card: FormCard
    output_dir_input: FilePathInput
    filename_input: LabeledInput

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Output configuration card
        self.output_card = FormCard(title="輸出設定")

        # Output directory selector
        self.output_dir_input = FilePathInput(
            label="輸出資料夾",
            button_text="選擇資料夾",
            placeholder="尚未選擇資料夾",
        )
        _ = self.output_dir_input.browse_button.clicked.connect(
            self.selectOutputDirRequested.emit
        )
        self.output_card.add_widget(self.output_dir_input)

        # Output filename input
        self.filename_input = LabeledInput(
            label="輸出檔案名稱",
            placeholder="輸入輸出檔名 (例如: 律師收入明細.xlsx)",
        )
        self.output_card.add_widget(self.filename_input)

        layout.addWidget(self.output_card)
        layout.addStretch(1)

    def set_output_dir(self, path: str) -> None:
        """Set the output directory path."""
        self.output_dir_input.set_path(path)

    def get_output_filename(self) -> str:
        """Get the entered output filename."""
        return self.filename_input.text().strip()
