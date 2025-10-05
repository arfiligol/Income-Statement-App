from __future__ import annotations

import logging
from typing import Iterable, List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..database import get_session
from ..models import Lawyer


def fetch_all_lawyers() -> List[Lawyer]:
    session = get_session()

    try:
        return session.query(Lawyer).all()
    except SQLAlchemyError as err:
        logging.error("An error occurred while fetching lawyers: %s", err)
        return []
    finally:
        session.close()


def insert_unique_lawyers(code_list: Iterable[str]) -> None:
    session = get_session()

    try:
        for code in code_list:
            new_lawyer = Lawyer(code=code)
            session.add(new_lawyer)

            try:
                session.commit()
            except IntegrityError:
                session.rollback()
    finally:
        session.close()
