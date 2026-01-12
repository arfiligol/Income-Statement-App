from __future__ import annotations

from typing import Optional

from src.models.db.alias import Alias
from src.services.dao.session import session_scope


def get_all_aliases() -> list[Alias]:
    """Get all aliases ordered by source code."""
    with session_scope() as session:
        # We need to expunge objects or return DTOs if we want to use them outside the session scope safely
        # But for simple usage in this app (synchronous), returning ORM objects detached *might* work if we don't lazy load.
        # However, session_scope closes the session.
        # Let's return a list of dictionaries or simple objects to be safe, OR rely on expire_on_commit=False?
        # Actually, simpler to just return list of DTOs or detached copies if needed.
        # But for now, let's just query and see.
        # Standard SQLAlchemy: objects are expired on commit. Accessing them after session close raises DetachedInstanceError.
        # Solution: expunge or re-query.
        # Or, simpler: Copy the data we need.
        aliases = session.query(Alias).order_by(Alias.source_code).all()
        session.expunge_all()
        return aliases


def get_alias(source_code: str) -> Optional[Alias]:
    """Get an alias by source code."""
    with session_scope() as session:
        alias = session.get(Alias, source_code)
        if alias:
            session.expunge(alias)
        return alias


def save_alias(source_code: str, target_codes: str) -> None:
    """Save or update an alias."""
    with session_scope() as session:
        alias = session.get(Alias, source_code)
        if alias:
            alias.target_codes = target_codes
        else:
            session.add(Alias(source_code=source_code, target_codes=target_codes))


def delete_alias(source_code: str) -> None:
    """Delete an alias."""
    with session_scope() as session:
        alias = session.get(Alias, source_code)
        if alias:
            session.delete(alias)
