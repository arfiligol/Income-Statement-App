from __future__ import annotations

import logging
import os
from typing import Optional, Sequence

import pandas as pd
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox

from src.models import WorkflowPageState
from src.services.workflow_service import (
    AutoFillPrompt,
    AutoFillResponse,
    WorkflowProcessingError,
    build_separate_ledger,
    get_filename_validator,
)
from src.services.workflow_service import (
    auto_fill_lawyer_codes as run_auto_fill_workflow,
)
from src.services.worksheets import QtSeparateAccountsWorksheet
from src.views.dialogs import LawyerSelectionDialog
from src.views.main_window import MainWindow


class WorkflowController(QObject):
    """Handles workflow-tab user interactions."""

    def __init__(self, window: MainWindow, state: WorkflowPageState) -> None:
        super().__init__(window)
        self.window: MainWindow = window
        self.state: WorkflowPageState = state
        self._skip_manual_prompts: bool = False

        self.window.selectSourceRequested.connect(self.select_source_file)
        self.window.selectOutputDirRequested.connect(self.select_output_dir)
        self.window.actionSelected.connect(self.on_action_selected)
        self.window.submitRequested.connect(self.on_submit)

    # ------------------------------------------------------------------
    @Slot()
    def select_source_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self.window,
            "選擇來源檔案",
            filter="Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            logging.debug("使用者取消選擇來源檔案")
            return

        if os.path.splitext(file_path)[1].lower() not in {".xlsx", ".xls"}:
            QMessageBox.warning(self.window, "警告", "選擇的檔案不是 .xls 或 .xlsx，請重新選擇！")
            return

        logging.info("用戶選擇檔案: %s", file_path)
        self.state.source_path = file_path
        self.state.output_filename = None
        self.window.set_source_path(file_path)

        auto_output_dir = os.path.dirname(file_path)
        self.state.output_dir = auto_output_dir
        self.window.set_output_dir(auto_output_dir)
        self.window.set_status_message("已載入來源檔案")
        self.window.set_submit_state("warning")

    @Slot()
    def select_output_dir(self) -> None:
        dir_path = QFileDialog.getExistingDirectory(self.window, "選擇輸出資料夾")
        if not dir_path:
            logging.debug("使用者取消選擇輸出資料夾")
            return

        logging.info("用戶選擇輸出位置: %s", dir_path)
        self.state.output_dir = dir_path
        self.window.set_output_dir(dir_path)
        self.window.set_status_message("已更新輸出資料夾")
        self.window.set_submit_state("warning")

    @Slot(str)
    def on_action_selected(self, action_name: str) -> None:
        if not action_name:
            return
        self.state.selected_action = action_name
        self.window.set_selected_action(action_name)
        self.window.set_status_message(f"已選擇功能：{self._action_label(action_name)}")
        self.window.set_submit_state("warning")

    @Slot()
    def on_submit(self) -> None:
        source_path = self.state.source_path
        if source_path is None:
            QMessageBox.warning(self.window, "警告", "請先選擇來源檔案！")
            self.window.set_submit_state("danger")
            return

        action = self.state.selected_action
        if action == "auto_fill_remark":
            self.auto_fill_lawyer_codes()
        elif action == "separate_the_ledger":
            if self.state.output_dir is None:
                auto_dir = os.path.dirname(source_path)
                self.state.output_dir = auto_dir
                self.window.set_output_dir(auto_dir)

            filename = self.window.get_output_filename().strip()
            if filename in {"", "輸入輸出檔名"}:
                QMessageBox.warning(self.window, "警告", "請先輸入輸出檔案名稱！")
                self.window.set_status_message("請輸入輸出檔案名稱")
                self.window.set_submit_state("danger")
                return
            if get_filename_validator()(filename):
                QMessageBox.critical(self.window, "錯誤", "輸出檔名包含不合法字元")
                self.window.set_submit_state("danger")
                return

            self.state.output_filename = filename

            self.separate_the_ledger()
        else:
            QMessageBox.information(self.window, "提示", "請先選擇要執行的功能！")
            self.window.set_status_message("請先選擇要執行的功能！")
            self.window.set_submit_state("warning")

    # ------------------------------------------------------------------
    def auto_fill_lawyer_codes(self) -> None:
        source_path = self.state.source_path
        if source_path is None:
            return

        workbook_path = self._ensure_openpyxl_compatible_workbook(source_path)
        self._skip_manual_prompts = False

        def prompt_handler(prompt: AutoFillPrompt) -> Optional[AutoFillResponse]:
            if self._skip_manual_prompts:
                return AutoFillResponse(selected_codes=[], skip_remaining=True)

            response = self._prompt_for_codes(prompt.summary, prompt.row_number, prompt.known_codes)
            if response and response.skip_remaining:
                self._skip_manual_prompts = True
            return response

        try:
            result = run_auto_fill_workflow(workbook_path, prompt_handler=prompt_handler)
        except WorkflowProcessingError as err:
            QMessageBox.warning(self.window, "提示", str(err))
            self.window.set_status_message(str(err))
            self.window.set_submit_state("danger")
            return

        self.window.set_status_message(f"已更新 {result.updated_count} 筆備註欄位。")
        self.window.set_submit_state("success")

    def separate_the_ledger(self) -> None:
        output_dir = self.state.output_dir
        source_path = self.state.source_path
        output_name = self.state.output_filename
        if output_dir is None or source_path is None or output_name is None:
            return

        try:
            result = build_separate_ledger(source_path)
        except WorkflowProcessingError as err:
            QMessageBox.warning(self.window, "提示", str(err))
            logging.warning("Separate ledger failed: %s", err)
            self.window.set_submit_state("danger")
            return

        try:
            output_path = os.path.join(output_dir, f"{output_name}.xlsx")
            target_sheet = QtSeparateAccountsWorksheet(self.window, output_path)
            target_sheet.write_data_to_worksheet(
                result.rows,
                total_debit=result.total_debit,
                total_credit=result.total_credit,
            )
        except Exception as err:  # pylint: disable=broad-except
            detail = str(err).strip() or "寫入資料時發生未知錯誤"
            QMessageBox.critical(
                self.window,
                "寫入資料時發生錯誤",
                f"請確認目標檔案是否已被其他程式開啟，或檢查錯誤訊息：\n{detail}",
            )
            logging.error("寫入目標工作表時發生錯誤: %s", err, exc_info=True)
            self.window.set_submit_state("danger")
            return

        self.window.set_status_message("處理完畢！")
        self.window.set_submit_state("success")

    # ------------------------------------------------------------------
    def _prompt_for_codes(
        self,
        summary: str,
        row_number: int,
        available_codes: Sequence[str],
    ) -> Optional[AutoFillResponse]:
        dialog = LawyerSelectionDialog(summary, row_number, list(available_codes), parent=self.window)
        if dialog.exec():
            return AutoFillResponse(
                selected_codes=list(dialog.selected_codes),
                skip_remaining=bool(getattr(dialog, "skip_remaining", False)),
            )
        return None

    @staticmethod
    def _get_excel_read_engine(file_path: str) -> str:
        return "xlrd" if file_path.lower().endswith(".xls") else "openpyxl"

    def _ensure_openpyxl_compatible_workbook(self, file_path: str) -> str:
        if not file_path.lower().endswith(".xls"):
            return file_path

        converted_path = os.path.splitext(file_path)[0] + "_converted.xlsx"
        if not os.path.exists(converted_path):
            read_engine = self._get_excel_read_engine(file_path)
            xls = pd.ExcelFile(file_path, engine=read_engine)
            with pd.ExcelWriter(converted_path, engine="openpyxl") as writer:
                for sheet_name in xls.sheet_names:
                    df = pd.DataFrame(xls.parse(sheet_name))
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        return converted_path

    @staticmethod
    def _action_label(action_name: str) -> str:
        return {
            "auto_fill_remark": "摘要抓律師代碼",
            "separate_the_ledger": "律師收入明細",
        }.get(action_name, action_name)
