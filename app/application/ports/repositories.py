from typing import Any, Protocol


from app.common.types import Result
from app.domain.dto.code_replacement import CodeReplacement
from app.domain.dto.file_source import FileSource
from app.domain.dto.lawyer import Lawyer
from app.domain.dto.statement import Statement


class ExcelRepository(Protocol):
    """
    Interface for accessing Excel data.
    Infrastructure layer will implement this using pandas/openpyxl.
    """

    def read_statement(self, source: FileSource) -> Result[Statement, Exception]:
        """Reads an Excel file and converts it into a Statement DTO."""
        ...

    def read_raw_rows(self, source: FileSource) -> Result[list[list[Any]], Exception]:
        """Reads raw rows for low-level processing (e.g. AutoFill)."""
        ...

    def update_cells(
        self, source: FileSource, updates: list[tuple[int, int, Any]]
    ) -> Result[int, Exception]:
        """Updates specific cells in the Excel file. updates = [(row, col, value), ...]"""
        ...


class SettingsRepository(Protocol):
    """Interface for app settings persistence."""

    def get(self, key: str, default: Any = None) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...


class LawyerRepository(Protocol):
    """Interface for accessing Lawyer data."""

    def get_all(self) -> list[Lawyer]: ...
    def add(self, lawyer: Lawyer) -> None: ...
    def ensure_exists(self, codes: list[str]) -> None: ...


class CodeReplacementRepository(Protocol):
    """Interface for accessing CodeReplacement data."""

    def get_all(self) -> list[CodeReplacement]: ...
    def add(self, replacement: CodeReplacement) -> None: ...
    def update(self, replacement: CodeReplacement) -> None: ...
    def delete(self, id: int) -> None: ...
    def get_by_source(self, source_code: str) -> CodeReplacement | None: ...
