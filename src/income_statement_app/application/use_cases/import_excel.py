from income_statement_app.application.ports.repositories import ExcelRepository
from income_statement_app.common.types import Result
from income_statement_app.domain.dto.file_source import FileSource
from income_statement_app.domain.dto.statement import Statement


class ImportExcelUseCase:
    """
    Use Case: Import Excel File
    Orchestrates the process of reading an Excel file and converting it to a domain Statement.
    """

    def __init__(self, excel_repo: ExcelRepository):
        self._excel_repo = excel_repo

    def execute(self, source: FileSource) -> Result[Statement, Exception]:
        # 1. Validation (Optional Step: check file extension etc. if not done in Gateway)

        # 2. Read from Repository
        result = self._excel_repo.read_statement(source)

        # 3. Post-processing (Optional: Auto-classification, applying Rules)
        if result.is_success:
            statement = result.value
            # Apply domain rules here (e.g. self._rules.apply(statement))
            pass

        return result
