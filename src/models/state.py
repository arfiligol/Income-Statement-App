"""Application state containers used by controllers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WorkflowPageState:
    """UI state tracked by the workflow page controller."""

    source_path: Optional[str] = None
    output_dir: Optional[str] = None
    selected_action: Optional[str] = None
    output_filename: Optional[str] = None


@dataclass
class AppState:
    """Root application state composed of per-page state containers."""

    workflow: WorkflowPageState = field(default_factory=WorkflowPageState)
