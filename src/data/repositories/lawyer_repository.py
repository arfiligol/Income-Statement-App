from __future__ import annotations

from collections.abc import Iterable

from src.domain.dtos.lawyer_dto import LawyerDTO
from src.models.db.lawyer import Lawyer
from src.data.db.session import session_scope


class LawyerRepository:
    """Repository invloves CRUD operations for Lawyer."""

    def get_all(self) -> list[LawyerDTO]:
        """Get all lawyers."""
        with session_scope() as session:
            return [LawyerDTO(code=lawyer.code) for lawyer in session.query(Lawyer).order_by(Lawyer.code)]

    def ensure_lawyers(self, codes: Iterable[str]) -> None:
        """Ensure lawyers exist in database."""
        with session_scope() as session:
            for code in {code.strip() for code in codes if code.strip()}:
                if session.get(Lawyer, code) is None:
                    session.add(Lawyer(code=code))
