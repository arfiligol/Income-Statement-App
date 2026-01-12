from __future__ import annotations

from typing import Optional

from src.domain.dtos.alias_dto import AliasDTO
from src.models.db.alias import Alias
from src.data.db.session import session_scope


class AliasRepository:
    """Repository involves CRUD operations for Alias."""

    def get_all(self) -> list[AliasDTO]:
        """Get all aliases ordered by source code."""
        with session_scope() as session:
            aliases = session.query(Alias).order_by(Alias.source_code).all()
            return [
                AliasDTO(
                    source_code=a.source_code,
                    target_codes=[t.strip() for t in a.target_codes.split(",") if t.strip()]
                )
                for a in aliases
            ]

    def get_by_source(self, source_code: str) -> Optional[AliasDTO]:
        """Get an alias by source code."""
        with session_scope() as session:
            alias = session.get(Alias, source_code)
            if alias:
                return AliasDTO(
                    source_code=alias.source_code,
                    target_codes=[t.strip() for t in alias.target_codes.split(",") if t.strip()]
                )
            return None

    def save(self, dto: AliasDTO) -> None:
        """Save or update an alias."""
        with session_scope() as session:
            alias = session.get(Alias, dto.source_code)
            target_str = ",".join(dto.target_codes)
            if alias:
                alias.target_codes = target_str
            else:
                session.add(Alias(source_code=dto.source_code, target_codes=target_str))

    def delete(self, source_code: str) -> None:
        """Delete an alias."""
        with session_scope() as session:
            alias = session.get(Alias, source_code)
            if alias:
                session.delete(alias)
