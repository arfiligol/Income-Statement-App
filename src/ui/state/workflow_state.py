from __future__ import annotations

import threading
from typing import Callable

from src.services.workflow_service import WorkflowService, WorkflowProcessingError
from src.domain.dtos.workflow_dto import AutoFillResultDTO, SeparateLedgerResultDTO

class WorkflowState:
    def __init__(self, workflow_service: WorkflowService):
        self.service = workflow_service
        self.is_processing = False
        self.logs: list[str] = []
        self._on_change: Callable[[], None] | None = None
        
        # Inputs
        self.selected_file: str | None = None
        self.output_dir: str | None = None

    def bind(self, callback: Callable[[], None]):
        self._on_change = callback

    def _notify(self):
        if self._on_change:
            self._on_change()

    def log(self, message: str):
        self.logs.append(message)
        print(message, flush=True)
        self._notify()

    def set_file(self, path: str):
        self.selected_file = path
        self.log(f"已選擇檔案: {path}")
        self._notify()

    def set_output_dir(self, path: str):
        self.output_dir = path
        self.log(f"已選擇輸出目錄: {path}")
        self._notify()

    def _run_task(self, task_func, *args):
        self.is_processing = True
        self._notify()
        
        def wrapper():
            try:
                task_func(*args)
            except WorkflowProcessingError as e:
                self.log(f"錯誤: {e}")
            except Exception as e:
                self.log(f"未預期的錯誤: {e}")
                import traceback
                traceback.print_exc()
            finally:
                self.is_processing = False
                self._notify()
        
        threading.Thread(target=wrapper, daemon=True).start()

    def run_auto_fill(self):
        if not self.selected_file:
            self.log("錯誤: 請先選擇 Excel 檔案")
            return
        
        self.log("開始執行：自動填寫律師代碼...")
        
        def task():
            result = self.service.run_auto_fill(self.selected_file)
            self.log(f"完成！共更新 {result.updated_count} 筆資料。")
            
        self._run_task(task)

    def run_separate_ledger(self):
        if not self.selected_file:
            self.log("錯誤: 請先選擇 Excel 檔案")
            return
        
        # If output dir is not set, use source directory or a default?
        # WorkflowService expects output_path (file path), not dir.
        # Logic in QtSeparateAccountsWorksheet was to save overwriting logical target or new file?
        # The service `write_separate_ledger_report` takes `file_path`.
        # Usually it's `source_path` (modified) or `new_file`.
        # The user requirement was "Separate Ledger" -> "程式RUN後檔案" in the SAME workbook usually.
        # But `SeparateLedgerResult` is data.
        # `ExcelReportService.write_separate_ledger_report` puts it into `程式RUN後檔案` sheet.
        # It takes `file_path`. 
        # If we pass `selected_file`, it modifies the source file.
        # That seems to be the intended behavior (add sheet to existing workbook).
        
        self.log("開始執行：明細分帳...")
        
        def task():
            # Using selected file as both source and destination (to add sheet)
            self.service.run_separate_ledger(self.selected_file, self.selected_file)
            self.log("完成！明細分帳工作表已建立。")
            
        self._run_task(task)
