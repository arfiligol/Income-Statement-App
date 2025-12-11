from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from qt_material import QtStyleTools  # type: ignore

from src.views.pages.database_page import DatabasePage
from src.views.pages.workflow_page import WorkflowPage

if TYPE_CHECKING:
    from src.controllers.app_controller import AppController


class MainWindow(QtStyleTools, QMainWindow):
    """Qt-Material styled main window using toolbars similar to official demo."""

    selectSourceRequested: Signal = Signal()
    selectOutputDirRequested: Signal = Signal()
    actionSelected: Signal = Signal(str)
    submitRequested: Signal = Signal()
    updateRequested: Signal = Signal()

    def __init__(self) -> None:
        super().__init__()

        # Initialize instance variables
        self.controller: AppController | None = None
        self.extra: dict[str, str]
        self.workflow_page: WorkflowPage
        self.database_page: DatabasePage
        self.stack: QStackedWidget
        self._current_view: str
        self.toolBar: QToolBar
        self.toolBar_2: QToolBar
        self.workflow_action: QAction
        self.database_action: QAction
        self.update_action: QAction

        self.setWindowTitle("小倩工具箱 - Qt Material")
        self.resize(1100, 720)

        self.extra = {
            "danger": "#dc3545",
            "warning": "#ffc107",
            "success": "#17a2b8",
            "font_family": "Roboto",
            "density_scale": "0",
            "button_shape": "default",
        }
        self.set_extra(self.extra)

        self.workflow_page = WorkflowPage()
        self.database_page = DatabasePage()

        self.stack = QStackedWidget()
        _ = self.stack.addWidget(self.workflow_page)
        _ = self.stack.addWidget(self.database_page)

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(16, 16, 16, 16)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.stack)
        self.setCentralWidget(central)

        self._build_toolbars()

        self._current_view = "workflow"
        self._wire_workflow_controls()
        self._update_navigation()

    def _build_toolbars(self) -> None:
        # Primary app bar
        self.toolBar = QToolBar("AppBar", self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        title_label = QLabel("小倩工具箱")
        title_label.setProperty("class", "app-title")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; padding: 4px 12px;"
        )
        _ = self.toolBar.addWidget(title_label)

        # Spacer to push update button to the right
        spacer = QWidget()
        spacer.setSizePolicy(
            self.toolBar.widgetForAction(self.toolBar.actions()[0])
            .sizePolicy()
            .horizontalPolicy(),
            self.toolBar.widgetForAction(self.toolBar.actions()[0])
            .sizePolicy()
            .verticalPolicy(),
        )
        spacer.setStyleSheet("background: transparent;")
        from PySide6.QtWidgets import QSizePolicy

        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        _ = self.toolBar.addWidget(spacer)

        self.update_action = QAction("發現新版本 (點擊更新)", self)
        self.update_action.setVisible(False)
        self.update_action.triggered.connect(self.updateRequested.emit)
        _ = self.toolBar.addAction(self.update_action)

        # Apply style to update button (make it flashy)
        update_btn = self.toolBar.widgetForAction(self.update_action)
        if update_btn:
            update_btn.setStyleSheet("color: #ffc107; font-weight: bold;")

        _ = self.toolBar.addSeparator()

        # Secondary navigation toolbar (vertical like official demo)
        self.toolBar_2 = QToolBar("Navigation", self)
        self.toolBar_2.setObjectName("toolBar_2")
        self.toolBar_2.setMovable(False)
        self.toolBar_2.setOrientation(Qt.Orientation.Vertical)
        self.toolBar_2.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolBar_2)

        group = QActionGroup(self)
        group.setExclusive(True)

        self.workflow_action = QAction("工作包", self)
        self.workflow_action.setCheckable(True)
        self.database_action = QAction("資料庫操作", self)
        self.database_action.setCheckable(True)

        _ = group.addAction(self.workflow_action)
        _ = group.addAction(self.database_action)

        _ = self.workflow_action.triggered.connect(lambda: self.switch_view("workflow"))
        _ = self.database_action.triggered.connect(lambda: self.switch_view("database"))

        self.toolBar_2.addAction(self.workflow_action)
        self.toolBar_2.addAction(self.database_action)
        for action in (self.workflow_action, self.database_action):
            button = self.toolBar_2.widgetForAction(action)
            if button is not None:
                button.setMinimumWidth(150)
                button.setMaximumWidth(150)

    def _wire_workflow_controls(self) -> None:
        _ = self.workflow_page.select_source_button.clicked.connect(
            self.selectSourceRequested.emit
        )
        _ = self.workflow_page.select_output_dir_button.clicked.connect(
            self.selectOutputDirRequested.emit
        )
        _ = self.workflow_page.auto_fill_button.toggled.connect(
            self._on_auto_fill_toggled
        )
        _ = self.workflow_page.separate_ledger_button.toggled.connect(
            self._on_separate_toggled
        )
        _ = self.workflow_page.submit_button.clicked.connect(self.submitRequested.emit)

    def switch_view(self, target_view: str) -> None:
        if target_view not in {"workflow", "database"}:
            return
        if target_view == self._current_view:
            return

        self._current_view = target_view
        self.stack.setCurrentWidget(
            self.workflow_page if target_view == "workflow" else self.database_page
        )
        self._update_navigation()

    def _update_navigation(self) -> None:
        workflow_active = self._current_view == "workflow"
        self.workflow_action.setChecked(workflow_active)
        self.database_action.setChecked(not workflow_active)

    def set_source_path(self, path: str) -> None:
        self.workflow_page.source_path_label.setText(path)

    def set_output_dir(self, path: str) -> None:
        self.workflow_page.output_dir_path.setText(path)

    def set_status_message(self, message: str) -> None:
        self.workflow_page.set_status_message(message)

    def set_selected_action(self, action_name: str | None) -> None:
        self.workflow_page.set_action_highlight(action_name)

    def set_submit_state(self, state: str) -> None:
        self.workflow_page.set_submit_state(state)

    @property
    def current_view(self) -> str:
        return self._current_view

    def get_output_filename(self) -> str:
        return self.workflow_page.filename_input.text()

    # internal ---------------------------------------------------------
    @Slot(bool)
    def _on_auto_fill_toggled(self, checked: bool) -> None:
        if checked:
            self.actionSelected.emit("auto_fill_remark")

    @Slot(bool)
    def _on_separate_toggled(self, checked: bool) -> None:
        if checked:
            self.actionSelected.emit("separate_the_ledger")

    def show_update_message(self, version: str) -> None:
        self.update_action.setText(f"發現新版本 v{version} (點擊更新)")
        self.update_action.setVisible(True)
