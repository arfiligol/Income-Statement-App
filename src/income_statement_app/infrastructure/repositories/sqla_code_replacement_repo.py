from income_statement_app.application.ports.repositories import CodeReplacementRepository
from income_statement_app.domain.dto.code_replacement import CodeReplacement
from income_statement_app.infrastructure.db.code_replacement import DbCodeReplacement
from income_statement_app.infrastructure.db.session import session_scope


class SQLACodeReplacementRepository(CodeReplacementRepository):
    def get_all(self) -> list[CodeReplacement]:
        with session_scope() as session:
            rows = session.query(DbCodeReplacement).order_by(DbCodeReplacement.id).all()
            return [
                CodeReplacement(
                    id=r.id, source_code=r.source_code, target_codes=r.target_codes
                )
                for r in rows
            ]

    def add(self, replacement: CodeReplacement) -> None:
        with session_scope() as session:
            # Check if source already exists? unique constraint handles it, but maybe check?
            # For simplicity, we trust VM handles validation or we catch integrity error.
            db_obj = DbCodeReplacement(
                source_code=replacement.source_code,
                target_codes=replacement.target_codes,
            )
            session.add(db_obj)

    def update(self, replacement: CodeReplacement) -> None:
        with session_scope() as session:
            db_obj = session.get(DbCodeReplacement, replacement.id)
            if db_obj:
                db_obj.source_code = replacement.source_code
                db_obj.target_codes = replacement.target_codes

    def delete(self, id: int) -> None:
        with session_scope() as session:
            db_obj = session.get(DbCodeReplacement, id)
            if db_obj:
                session.delete(db_obj)

    def get_by_source(self, source_code: str) -> CodeReplacement | None:
        with session_scope() as session:
            r = (
                session.query(DbCodeReplacement)
                .filter(DbCodeReplacement.source_code == source_code)
                .first()
            )
            if r:
                return CodeReplacement(
                    id=r.id, source_code=r.source_code, target_codes=r.target_codes
                )
            return None
