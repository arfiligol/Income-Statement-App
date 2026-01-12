from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QMessageBox,
)

from src.views.components.inputs import LabeledInput


class AliasEditorDialog(QDialog):
    """Dialog for creating or editing a lawyer code alias."""

    def __init__(
        self,
        parent: QWidget | None = None,
        source_code: str | None = None,
        target_codes: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("編輯律師代碼群組" if source_code else "新增律師代碼群組")
        self.resize(400, 250)

        self._source_code = source_code
        self._target_codes = target_codes
        self._result: tuple[str, str] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Inputs
        self.source_input = LabeledInput(
            label="來源代碼 (Source Code)",
            placeholder="例如: KW",
        )
        if source_code:
            self.source_input.setText(source_code)
            # If editing, maybe disable source code editing? 
            # Usually better to allow deleting and re-adding if they want to change PK,
            # or just disable it. Let's disable it for edit mode to simplify PK handling.
            self.source_input.input_field.setReadOnly(True)
            self.source_input.input_field.setToolTip("來源代碼無法修改，請刪除後重新建立")
        
        layout.addWidget(self.source_input)

        self.target_input = LabeledInput(
            label="目標代碼列表 (Target Codes)",
            placeholder="例如: KW, JH, JL (使用逗號分隔)",
        )
        if target_codes:
            self.target_input.setText(target_codes)
        layout.addWidget(self.target_input)

        layout.addStretch(1)

        # Buttons
        button_row = QHBoxLayout()
        button_row.addStretch(1)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self.cancel_button)

        self.save_button = QPushButton("儲存")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setProperty("class", "primary")
        button_row.addWidget(self.save_button)

        layout.addLayout(button_row)

    def _on_save(self) -> None:
        source = self.source_input.text().strip()
        targets = self.target_input.text().strip()

        if not source:
            QMessageBox.warning(self, "警告", "來源代碼不能為空")
            return
        if not targets:
            QMessageBox.warning(self, "警告", "目標代碼列表不能為空")
            return

        self._result = (source, targets)
        self.accept()

    def get_data(self) -> tuple[str, str] | None:
        """Return the (source_code, target_codes) tuple if saved, else None."""
        return self._result
