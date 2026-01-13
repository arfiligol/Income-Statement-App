from dataclasses import dataclass, field
from typing import List, Optional

from app.application.use_cases.auto_fill import AutoFillUseCase
from app.application.use_cases.import_excel import ImportExcelUseCase
from app.domain.dto.auto_fill import AutoFillResult
from app.domain.dto.file_source import FileSource
from app.domain.dto.statement import Statement
from app.ui.viewmodels.base import BaseViewModel


@dataclass
class StatementState:
    file_source: Optional[FileSource] = None
    statement: Optional[Statement] = None
    auto_fill_result: Optional[AutoFillResult] = None
    is_loading: bool = False
    error_message: Optional[str] = None

    @property
    def has_file(self) -> bool:
        return self.file_source is not None


class StatementViewModel(BaseViewModel[StatementState]):
    """
    ViewModel for the Statement Editor / Workflow Page.
    """

    def __init__(
        self, import_use_case: ImportExcelUseCase, auto_fill_use_case: AutoFillUseCase
    ):
        super().__init__(StatementState())
        self._import_use_case = import_use_case
        self._auto_fill_use_case = auto_fill_use_case

    # -- Intents --

    async def handle_file_selected(self, source: FileSource):
        """Intent: User selected a file (Uploaded or Native Picked)."""
        self.update_state(file_source=source, is_loading=True, error_message=None)

        try:
            result = self._import_use_case.execute(source)
            if result.is_success:
                self.update_state(statement=result.value, is_loading=False)
                self.emit_effect(
                    {
                        "type": "toast",
                        "message": "File imported successfully!",
                        "level": "success",
                    }
                )
            else:
                error_msg = str(result.error)
                self.update_state(is_loading=False, error_message=error_msg)
                self.emit_effect(
                    {
                        "type": "toast",
                        "message": f"Import failed: {error_msg}",
                        "level": "error",
                    }
                )
        except Exception as e:
            self.update_state(is_loading=False, error_message=str(e))
            self.emit_effect(
                {
                    "type": "toast",
                    "message": f"Unexpected error: {str(e)}",
                    "level": "error",
                }
            )

    async def handle_run_auto_fill(self):
        """Intent: Run Step 2 (Auto Fill Lawyers)."""
        if not self.state.file_source:
            self.emit_effect(
                {
                    "type": "toast",
                    "message": "Please select a file first.",
                    "level": "warning",
                }
            )
            return

        self.update_state(is_loading=True)
        try:
            result = await self._auto_fill_use_case.execute(self.state.file_source)
            if result.is_success:
                self.update_state(auto_fill_result=result.value, is_loading=False)
                count = result.value.updated_count
                self.emit_effect(
                    {
                        "type": "toast",
                        "message": f"Auto-fill complete. Corrected {count} items.",
                        "level": "success",
                    }
                )
            else:
                error_msg = str(result.error)
                self.update_state(is_loading=False, error_message=error_msg)
                self.emit_effect(
                    {
                        "type": "toast",
                        "message": f"Auto-fill failed: {error_msg}",
                        "level": "error",
                    }
                )
        except Exception as e:
            self.update_state(is_loading=False, error_message=str(e))
            self.emit_effect(
                {
                    "type": "toast",
                    "message": f"Unexpected error: {str(e)}",
                    "level": "error",
                }
            )
