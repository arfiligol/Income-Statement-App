from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Lawyer(Base):
    __tablename__ = "lawyers"

    code: Mapped[str] = mapped_column(String, primary_key=True)
