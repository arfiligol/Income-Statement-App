from dataclasses import dataclass, field


from income_statement_app.application.use_cases.auto_fill import AutoFillUseCase
from income_statement_app.application.use_cases.import_excel import ImportExcelUseCase
from income_statement_app.application.use_cases.separate_ledger import SeparateLedgerUseCase
from income_statement_app.domain.dto.auto_fill import AutoFillResult
from income_statement_app.domain.dto.file_source import FileSource
from income_statement_app.domain.dto.separate_ledger import SeparateLedgerResult
from income_statement_app.domain.dto.statement import Statement
from income_statement_app.ui.viewmodels.base import BaseViewModel


@dataclass
class StatementState:
    file_source: FileSource | None = None
    statement: Statement | None = None
    auto_fill_result: AutoFillResult | None = None
    separate_ledger_result: SeparateLedgerResult | None = None
    is_loading: bool = False
    error_message: str | None = None

    @property
    def has_file(self) -> bool:
        return self.file_source is not None


class StatementViewModel(BaseViewModel[StatementState]):
    """
    ViewModel for the Statement Editor / Workflow Page.
    """

    def __init__(
        self,
        import_use_case: ImportExcelUseCase,
        auto_fill_use_case: AutoFillUseCase,
        separate_ledger_use_case: SeparateLedgerUseCase,
    ):
        super().__init__(StatementState())
        self._import_use_case = import_use_case
        self._auto_fill_use_case = auto_fill_use_case
        self._separate_ledger_use_case = separate_ledger_use_case

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

    async def handle_run_separate_ledger(self):
        """Intent: Run Step 3 (Separate Ledger)."""
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
            # We assume AutoFill is done or implicit.
            result = self._separate_ledger_use_case.execute(self.state.file_source)
            if result.is_success:
                self.update_state(separate_ledger_result=result.value, is_loading=False)
                # Effect: Download or Show success
                path = result.value.output_path
                self.emit_effect(
                    {
                        "type": "toast",
                        "message": f"Report generated at {path}",
                        "level": "success",
                    }
                )
            else:
                error_msg = str(result.error)
                self.update_state(is_loading=False, error_message=error_msg)
                self.emit_effect(
                    {
                        "type": "toast",
                        "message": f"Separate Ledger failed: {error_msg}",
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
