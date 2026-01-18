from typing import Any


import openpyxl
import pandas as pd

from income_statement_app.application.ports.repositories import ExcelRepository
from income_statement_app.common.errors import InfrastructureError, ValidationError
from income_statement_app.common.types import Result
from income_statement_app.domain.dto.file_source import FileSource
from income_statement_app.domain.dto.statement import Statement, StatementLineItem


class ExcelPandasRepository(ExcelRepository):
    """
    Implementation of ExcelRepository using pandas and openpyxl.
    """

    def read_statement(self, source: FileSource) -> Result[Statement, Exception]:
        try:
            file_path = self._resolve_source(source)
            if not file_path:
                return Result.failure(
                    ValidationError("Invalid file source: Path could not be resolved.")
                )

            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                return Result.failure(
                    InfrastructureError(f"Failed to read Excel file: {str(e)}")
                )

            # Convert DataFrame to Statement DTO
            statement = Statement()

            for _, row in df.iterrows():
                row_dict = row.fillna("").to_dict()
                item = StatementLineItem(
                    year=2024,  # Mock
                    month=1,  # Mock
                    description=str(row_dict.get("摘要", "Unknown")),
                    amount=0.0,
                    category=str(row_dict.get("科目", "")),
                )
                statement.add_item(item)

            return Result.success(statement)

        except Exception as e:
            return Result.failure(e)

    def read_raw_rows(self, source: FileSource) -> Result[list[list[Any]], Exception]:
        try:
            file_path = self._resolve_source(source)
            if not file_path:
                return Result.failure(ValidationError("Invalid file source."))

            # Read without header to get absolute row indices consistent with openpyxl
            df = pd.read_excel(file_path, header=None)
            # Convert to list of lists, handle NaN
            rows = df.fillna("").values.tolist()
            return Result.success(rows)
        except Exception as e:
            return Result.failure(InfrastructureError(f"Failed to read raw rows: {e}"))

    def update_cells(
        self, source: FileSource, updates: list[tuple[int, int, Any]]
    ) -> Result[int, Exception]:
        """
        updates: List of (row_index, col_index, value).
        Assume 1-based indexing for row/col to match Excel/Openpyxl.
        """
        try:
            file_path = self._resolve_source(source)
            if not file_path:
                return Result.failure(ValidationError("Invalid file source."))

            wb = openpyxl.load_workbook(file_path)
            ws = wb.active

            count = 0
            for row_idx, col_idx, value in updates:
                # openpyxl: cell(row=r, column=c).value = v
                ws.cell(row=row_idx, column=col_idx).value = value
                count += 1

            wb.save(file_path)
            wb.close()
            return Result.success(count)

        except Exception as e:
            return Result.failure(InfrastructureError(f"Failed to update cells: {e}"))

    def _resolve_source(self, source: FileSource) -> str | None:
        if source.is_local:
            return str(source.path)
        if source.path:
            return str(source.path)
        return None
