from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class DbCodeReplacement(Base):
    __tablename__ = "code_replacements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    target_codes: Mapped[str] = mapped_column(String, nullable=False)
