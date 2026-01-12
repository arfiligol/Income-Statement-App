from __future__ import annotations

from typing import Callable

from src.data.repositories.alias_repository import AliasRepository
from src.domain.dtos.alias_dto import AliasDTO


class DatabaseState:
    def __init__(self, alias_repo: AliasRepository):
        self.alias_repo = alias_repo
        self.aliases: list[AliasDTO] = []
        self._on_change: Callable[[], None] | None = None
        self.error_message: str | None = None

    def bind(self, callback: Callable[[], None]):
        self._on_change = callback

    def _notify(self):
        if self._on_change:
            self._on_change()

    def load_data(self):
        try:
            self.aliases = self.alias_repo.get_all()
            self.error_message = None
        except Exception as e:
            self.error_message = str(e)
            self.aliases = []
        self._notify()

    def add_alias(self, source: str, targets: str):
        dto = AliasDTO(
            source_code=source.strip(),
            target_codes=[t.strip() for t in targets.split(",") if t.strip()]
        )
        try:
            self.alias_repo.save(dto)
            self.load_data()
        except Exception as e:
            self.error_message = str(e)
            self._notify()

    def delete_alias(self, source: str):
        try:
            self.alias_repo.delete(source)
            self.load_data()
        except Exception as e:
            self.error_message = str(e)
            self._notify()
