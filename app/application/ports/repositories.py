from typing import Any, List, Optional, Protocol

from app.common.types import Result
from app.domain.dto.alias import Alias
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


class AliasRepository(Protocol):
    """Interface for accessing Alias data."""

    def get_all(self) -> list[Alias]: ...
    def get_by_source(self, source_code: str) -> Optional[Alias]: ...
    def save(self, alias: Alias) -> None: ...
    def delete(self, source_code: str) -> None: ...
