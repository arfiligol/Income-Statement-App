"""Data access layer for Material app."""

from .lawyer_dao import get_lawyers, ensure_lawyers

__all__ = ["get_lawyers", "ensure_lawyers"]
