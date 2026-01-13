from app.application.ports.repositories import AliasRepository
from app.domain.dto.alias import Alias
from app.infrastructure.db.alias import Alias as DbAlias
from app.infrastructure.db.session import session_scope


class SQLAAliasRepository(AliasRepository):
    """SQLAlchemy implementation of AliasRepository."""

    def get_all(self) -> list[Alias]:
        with session_scope() as session:
            db_aliases = session.query(DbAlias).order_by(DbAlias.source_code).all()
            return [
                Alias(
                    source_code=a.source_code,
                    target_codes=[
                        t.strip()
                        for t in (a.target_codes or "").split(",")
                        if t.strip()
                    ],
                )
                for a in db_aliases
            ]

    def get_by_source(self, source_code: str) -> Alias | None:
        with session_scope() as session:
            db_alias = session.get(DbAlias, source_code)
            if db_alias:
                return Alias(
                    source_code=db_alias.source_code,
                    target_codes=[
                        t.strip()
                        for t in (db_alias.target_codes or "").split(",")
                        if t.strip()
                    ],
                )
            return None

    def save(self, alias: Alias) -> None:
        with session_scope() as session:
            db_alias = session.get(DbAlias, alias.source_code)
            target_str = ",".join(alias.target_codes)

            if db_alias:
                db_alias.target_codes = target_str
            else:
                session.add(
                    DbAlias(source_code=alias.source_code, target_codes=target_str)
                )

    def delete(self, source_code: str) -> None:
        with session_scope() as session:
            db_alias = session.get(DbAlias, source_code)
            if db_alias:
                session.delete(db_alias)
