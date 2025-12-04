from __future__ import annotations

from typing import Iterable, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
)


class LawyerSelectionDialog(QDialog):
    """PySide6 dialog for selecting and adding lawyer codes."""

    def __init__(self, summary: str, row_number: int, available_codes: Iterable[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("選擇律師代碼")
        self.resize(420, 360)

        self.skip_remaining = False
        self.selected_codes: List[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        row_label = QLabel(f"列號：{row_number}")
        row_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(row_label)

        summary_label = QLabel(summary)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("color: #b0bec5;")
        layout.addWidget(summary_label)

        codes_label = QLabel("既有律師代碼")
        layout.addWidget(codes_label)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        for code in sorted(set(available_codes)):
            item = QListWidgetItem(code)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget, 1)

        self.new_code_input = QLineEdit()
        self.new_code_input.setPlaceholderText("輸入新增代碼，空格分隔")
        layout.addWidget(self.new_code_input)

        button_row = QHBoxLayout()
        button_row.addStretch(1)

        self.skip_button = QPushButton("跳過後續手動")
        self.skip_button.clicked.connect(self._on_skip)
        button_row.addWidget(self.skip_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self.cancel_button)

        self.confirm_button = QPushButton("確認")
        self.confirm_button.clicked.connect(self._on_confirm)
        button_row.addWidget(self.confirm_button)

        layout.addLayout(button_row)

    def _on_confirm(self) -> None:
        selected = [item.text() for item in self.list_widget.selectedItems()]
        new_codes_text = self.new_code_input.text().strip()
        if new_codes_text:
            new_codes = [code.strip() for code in new_codes_text.split(" ") if code.strip()]
            selected.extend(new_codes)

        self.selected_codes = []
        seen = set()
        for code in selected:
            if code and code not in seen:
                seen.add(code)
                self.selected_codes.append(code)

        if not self.selected_codes:
            return

        self.accept()

    def _on_skip(self) -> None:
        self.skip_remaining = True
        self.selected_codes = []
        self.accept()
