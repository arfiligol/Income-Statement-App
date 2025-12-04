from __future__ import annotations

from collections.abc import Iterable

from src.models import LawyerDTO
from src.models.db.lawyer import Lawyer
from src.services.dao.session import session_scope


def get_lawyers() -> list[LawyerDTO]:
    with session_scope() as session:
        return [LawyerDTO(code=lawyer.code) for lawyer in session.query(Lawyer).order_by(Lawyer.code)]


def ensure_lawyers(codes: Iterable[str]) -> None:
    with session_scope() as session:
        for code in {code.strip() for code in codes if code.strip()}:
            if session.get(Lawyer, code) is None:
                session.add(Lawyer(code=code))
