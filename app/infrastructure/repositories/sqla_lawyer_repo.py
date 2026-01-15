from app.application.ports.repositories import LawyerRepository
from app.domain.dto.lawyer import Lawyer
from app.infrastructure.db.lawyer import Lawyer as DbLawyer
from app.infrastructure.db.session import session_scope


class SQLALawyerRepository(LawyerRepository):
    """SQLAlchemy implementation of LawyerRepository."""

    def get_all(self) -> list[Lawyer]:
        with session_scope() as session:
            # Sort by code
            db_lawyers = session.query(DbLawyer).order_by(DbLawyer.code).all()
            return [Lawyer(code=l.code) for l in db_lawyers]

    def add(self, lawyer: Lawyer) -> None:
        with session_scope() as session:
            if not session.get(DbLawyer, lawyer.code):
                session.add(DbLawyer(code=lawyer.code))

    def ensure_exists(self, codes: list[str]) -> None:
        with session_scope() as session:
            for code in codes:
                if not code or not code.strip():
                    continue
                code = code.strip()
                if session.get(DbLawyer, code) is None:
                    session.add(DbLawyer(code=code))
