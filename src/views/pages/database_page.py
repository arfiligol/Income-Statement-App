from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFrame,
)

from src.views.components.cards import Card
from src.views.components.labels import SectionTitle, DescriptionLabel
from src.views.components.buttons import PrimaryButton, SecondaryButton
from src.views.dialogs.alias_editor_dialog import AliasEditorDialog
from src.services.dao import alias_dao


class DatabasePage(QWidget):
    """Page for managing database records, including lawyer code aliases."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Card
        header_card = Card()
        header_layout = QVBoxLayout()
        title = SectionTitle("律師代碼群組管理", icon="👥")
        desc = DescriptionLabel(
            "設定「來源代碼」與「目標代碼列表」的對應關係。\n"
            "當自動填寫功能抓取到來源代碼時，將自動替換為目標代碼列表 (用於多人分帳)。"
        )
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        header_card.add_layout(header_layout)
        layout.addWidget(header_card)

        # Action Toolbar
        toolbar = QHBoxLayout()
        self.add_btn = PrimaryButton("新增群組")
        self.add_btn.clicked.connect(self._on_add)
        self.refresh_btn = SecondaryButton("重新整理")
        self.refresh_btn.clicked.connect(self._load_data)
        
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["來源代碼 (Source)", "目標代碼列表 (Targets)", "操作"])
        
        # Column resizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive) # Allow user to resize source
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)     # Targets take remaining space
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)       # Fixed width is most stable for widgets
        
        self.table.setColumnWidth(0, 200) # Default width for Source
        self.table.setColumnWidth(2, 200) # Fixed width for actions (148px content + padding)
        
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False) # Hide row numbers
        self.table.verticalHeader().setDefaultSectionSize(60) # Ensure rows are tall enough for buttons
        self.table.setShowGrid(False) # Cleaner look
        self.table.setDefaultDropAction(Qt.DropAction.IgnoreAction)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Read-only
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        self.table.setStyleSheet(
            """
            QTableWidget {
                background-color: rgba(30, 30, 30, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                gridline-color: rgba(255, 255, 255, 0.05);
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QHeaderView::section {
                background-color: rgba(40, 40, 40, 0.8);
                color: #e0e0e0;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #5c6bc0;
            }
            QTableWidget::item:selected {
                background-color: rgba(92, 107, 192, 0.2);
            }
            """
        )
        layout.addWidget(self.table, 1)

    def _load_data(self) -> None:
        """Load aliases from database."""
        self.table.setRowCount(0)
        aliases = alias_dao.get_all_aliases()
        
        for row_idx, alias in enumerate(aliases):
            self.table.insertRow(row_idx)
            
            # Source
            source_item = QTableWidgetItem(alias.source_code)
            source_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            source_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, source_item)
            
            # Targets
            target_item = QTableWidgetItem(alias.target_codes)
            target_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            target_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, target_item)
            
            # Actions
            action_widget = QWidget()
            action_widget.setMinimumWidth(160) # Ensure enough space for buttons
            action_widget.setStyleSheet("background: transparent;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(8, 4, 8, 4)
            action_layout.setSpacing(12) # Use larger spacing
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            edit_btn = SecondaryButton("編輯")
            edit_btn.setFixedSize(60, 32)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Use default param to capture loop variable
            edit_btn.clicked.connect(lambda checked=False, s=alias.source_code, t=alias.target_codes: self._on_edit(s, t))
            
            delete_btn = SecondaryButton("刪除")
            delete_btn.setFixedSize(60, 32)
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setProperty("class", "danger") # Assuming danger class exists or just relying on red text if styled
            delete_btn.setStyleSheet("color: #ef5350; border: 1px solid rgba(239, 83, 80, 0.5); border-radius: 4px;")
            delete_btn.clicked.connect(lambda checked=False, s=alias.source_code: self._on_delete(s))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row_idx, 2, action_widget)

    @Slot()
    def _on_add(self) -> None:
        dialog = AliasEditorDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                source, targets = data
                # Check for existing
                if alias_dao.get_alias(source):
                    QMessageBox.warning(self, "錯誤", f"來源代碼 '{source}' 已經存在！")
                    return
                alias_dao.save_alias(source, targets)
                self._load_data()

    def _on_edit(self, source: str, current_targets: str) -> None:
        dialog = AliasEditorDialog(self, source_code=source, target_codes=current_targets)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                _, new_targets = data
                alias_dao.save_alias(source, new_targets)
                self._load_data()

    def _on_delete(self, source: str) -> None:
        confirm = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除律師代碼群組 '{source}' 嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            alias_dao.delete_alias(source)
            self._load_data()
