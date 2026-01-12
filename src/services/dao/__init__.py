"""Data access layer for Material app."""

from .lawyer_dao import get_lawyers, ensure_lawyers
from . import alias_dao

__all__ = ["get_lawyers", "ensure_lawyers", "alias_dao"]
