from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QLabel, QMainWindow, QStackedWidget, QToolBar, QVBoxLayout, QWidget
from qt_material import QtStyleTools

from src.views.pages.database_page import DatabasePage
from src.views.pages.workflow_page import WorkflowPage


class MainWindow(QtStyleTools, QMainWindow):
    """Qt-Material styled main window using toolbars similar to official demo."""

    selectSourceRequested = Signal()
    selectOutputDirRequested = Signal()
    actionSelected = Signal(str)
    submitRequested = Signal()

    def __init__(self) -> None:
        super().__init__()
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
        self.stack.addWidget(self.workflow_page)
        self.stack.addWidget(self.database_page)

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
        self.toolBar.setAllowedAreas(Qt.TopToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        title_label = QLabel("小倩工具箱")
        title_label.setProperty("class", "app-title")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 4px 12px;")
        self.toolBar.addWidget(title_label)
        self.toolBar.addSeparator()

        # Secondary navigation toolbar (vertical like official demo)
        self.toolBar_2 = QToolBar("Navigation", self)
        self.toolBar_2.setObjectName("toolBar_2")
        self.toolBar_2.setMovable(False)
        self.toolBar_2.setOrientation(Qt.Vertical)
        self.toolBar_2.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar_2)

        group = QActionGroup(self)
        group.setExclusive(True)

        self.workflow_action = QAction("工作包", self)
        self.workflow_action.setCheckable(True)
        self.database_action = QAction("資料庫操作", self)
        self.database_action.setCheckable(True)

        group.addAction(self.workflow_action)
        group.addAction(self.database_action)

        self.workflow_action.triggered.connect(lambda: self.switch_view("workflow"))
        self.database_action.triggered.connect(lambda: self.switch_view("database"))

        self.toolBar_2.addAction(self.workflow_action)
        self.toolBar_2.addAction(self.database_action)
        for action in (self.workflow_action, self.database_action):
            button = self.toolBar_2.widgetForAction(action)
            if button is not None:
                button.setMinimumWidth(150)
                button.setMaximumWidth(150)

    def _wire_workflow_controls(self) -> None:
        self.workflow_page.select_source_button.clicked.connect(self.selectSourceRequested.emit)
        self.workflow_page.select_output_dir_button.clicked.connect(self.selectOutputDirRequested.emit)
        self.workflow_page.auto_fill_button.toggled.connect(self._on_auto_fill_toggled)
        self.workflow_page.separate_ledger_button.toggled.connect(self._on_separate_toggled)
        self.workflow_page.submit_button.clicked.connect(self.submitRequested.emit)

    def switch_view(self, target_view: str) -> None:
        if target_view not in {"workflow", "database"}:
            return
        if target_view == self._current_view:
            return

        self._current_view = target_view
        self.stack.setCurrentWidget(self.workflow_page if target_view == "workflow" else self.database_page)
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

    def set_selected_action(self, action_name: Optional[str]) -> None:
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
