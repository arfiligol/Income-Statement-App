from typing import List

from app.application.ports.repositories import LawyerRepository
from app.domain.dto.lawyer import Lawyer
from src.data.db.session import session_scope

# Adapting legacy src code
from src.models.db.lawyer import Lawyer as DbLawyer


class SQLALawyerRepository(LawyerRepository):
    """
    SQLAlchemy implementation of LawyerRepository.
    Wraps the legacy src.data.db.session logic.
    """

    def get_all(self) -> List[Lawyer]:
        with session_scope() as session:
            # Sort by code
            db_lawyers = session.query(DbLawyer).order_by(DbLawyer.code).all()
            return [Lawyer(code=l.code, name=l.name or "") for l in db_lawyers]

    def add(self, lawyer: Lawyer) -> None:
        with session_scope() as session:
            if not session.get(DbLawyer, lawyer.code):
                session.add(DbLawyer(code=lawyer.code, name=lawyer.name))

    def ensure_exists(self, codes: List[str]) -> None:
        with session_scope() as session:
            for code in codes:
                if not code or not code.strip():
                    continue
                code = code.strip()
                if session.get(DbLawyer, code) is None:
                    session.add(DbLawyer(code=code))
