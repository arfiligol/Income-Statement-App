"""Data models for the Material app."""

from .state import AppState, WorkflowPageState
from .dto.lawyer_dto import LawyerDTO

__all__ = ["AppState", "WorkflowPageState", "LawyerDTO"]
