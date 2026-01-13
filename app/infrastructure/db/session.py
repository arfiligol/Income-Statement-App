from __future__ import annotations

import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.base import Base

load_dotenv()

_engine = None
_Session = None


def _resolve_database_path() -> Path:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parents[3]

    db_filename = os.getenv("DATABASE_FILENAME", "sqlite_db.db")
    db_path = base_dir / "data" / db_filename
    if not db_path.parent.exists():
        logging.info("SQLite database directory missing, creating it.")
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def _get_engine():
    global _engine, _Session
    if _engine is None:
        db_file_path = _resolve_database_path()
        _engine = create_engine(f"sqlite:///{db_file_path}")
        Base.metadata.create_all(_engine)
        _Session = sessionmaker(bind=_engine)
    return _engine, _Session


@contextmanager
def session_scope() -> Iterator[Session]:
    _, session_factory = _get_engine()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
