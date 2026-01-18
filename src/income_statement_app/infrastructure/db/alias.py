from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from income_statement_app.infrastructure.db.base import Base


class Alias(Base):
    __tablename__ = "aliases"

    source_code: Mapped[str] = mapped_column(String, primary_key=True)
    target_codes: Mapped[str] = mapped_column(String, nullable=False)
