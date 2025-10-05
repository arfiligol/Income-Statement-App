from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFrame, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget, QButtonGroup


class WorkflowPage(QWidget):
    """Workflow page matching original ttk layout."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        layout.addWidget(self._build_source_section())
        layout.addWidget(self._build_action_section())
        layout.addWidget(self._build_output_section())
        layout.addStretch(1)

    def _build_source_section(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("class", "card")
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(16, 12, 16, 12)
        frame_layout.setSpacing(16)

        title = QLabel("請選擇來源檔案")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        title.setProperty("class", "section-title")

        self.source_path_label = QLabel("尚未選擇來源檔案")
        self.source_path_label.setObjectName("sourcePathLabel")
        self.source_path_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.select_source_button = QPushButton("選擇檔案")
        self.select_source_button.setObjectName("selectSourceButton")

        frame_layout.addWidget(title)
        frame_layout.addWidget(self.source_path_label, 1)
        frame_layout.addWidget(self.select_source_button)

        return frame

    def _build_action_section(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("class", "card")
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(16, 12, 16, 12)
        frame_layout.setSpacing(16)

        title = QLabel("請選擇要執行的功能")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title.setProperty("class", "section-title")

        self.auto_fill_button = QPushButton("摘要填入律師代碼")
        self.auto_fill_button.setCheckable(True)
        self.auto_fill_button.setObjectName("autoFillButton")

        self.separate_ledger_button = QPushButton("律師收入明細")
        self.separate_ledger_button.setCheckable(True)
        self.separate_ledger_button.setObjectName("separateLedgerButton")

        frame_layout.addWidget(title)
        frame_layout.addWidget(self.auto_fill_button)
        frame_layout.addWidget(self.separate_ledger_button)
        frame_layout.addStretch(1)

        self.action_group = QButtonGroup(self)
        self.action_group.setExclusive(True)
        self.action_group.addButton(self.auto_fill_button)
        self.action_group.addButton(self.separate_ledger_button)

        return frame

    def _build_output_section(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("class", "card")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 16, 16, 16)
        frame_layout.setSpacing(16)

        title = QLabel("輸出設定")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setProperty("class", "section-title")
        frame_layout.addWidget(title)

        dir_row = QHBoxLayout()
        dir_row.setSpacing(12)
        dir_label = QLabel("輸出資料夾")
        self.output_dir_path = QLabel("尚未選擇資料夾")
        self.output_dir_path.setObjectName("outputDirLabel")
        self.output_dir_path.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.select_output_dir_button = QPushButton("選擇資料夾")
        self.select_output_dir_button.setObjectName("selectDirButton")
        dir_row.addWidget(dir_label)
        dir_row.addWidget(self.output_dir_path, 1)
        dir_row.addWidget(self.select_output_dir_button)
        frame_layout.addLayout(dir_row)

        filename_row = QHBoxLayout()
        filename_row.setSpacing(12)
        filename_label = QLabel("輸出檔案名稱: ")
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("輸入輸出檔名")
        self.filename_input.setObjectName("filenameInput")
        filename_row.addWidget(filename_label)
        filename_row.addWidget(self.filename_input, 1)
        frame_layout.addLayout(filename_row)

        submit_row = QHBoxLayout()
        submit_row.setSpacing(12)
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.submit_button = QPushButton("執行功能 (Submit)")
        self.submit_button.setObjectName("submitButton")
        submit_row.addWidget(self.status_label, 1)
        submit_row.addWidget(self.submit_button)
        frame_layout.addLayout(submit_row)

        return frame

    def set_action_highlight(self, action_name: str | None) -> None:
        active_style = "background-color: #1976d2; color: white;"
        default_style = ""
        self.auto_fill_button.setStyleSheet(active_style if action_name == "auto_fill_remark" else default_style)
        self.separate_ledger_button.setStyleSheet(active_style if action_name == "separate_the_ledger" else default_style)

    def set_status_message(self, message: str) -> None:
        self.status_label.setText(message)
