from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LawyerDTO:
    """Lightweight representation of a lawyer record."""

    code: str
