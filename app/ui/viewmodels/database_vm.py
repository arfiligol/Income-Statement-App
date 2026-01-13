from dataclasses import dataclass, field
from typing import List, Optional

from app.application.ports.repositories import AliasRepository, LawyerRepository
from app.domain.dto.alias import Alias
from app.domain.dto.lawyer import Lawyer
from app.ui.viewmodels.base import BaseViewModel


@dataclass
class DatabaseState:
    lawyers: list[Lawyer] = field(default_factory=list)
    aliases: list[Alias] = field(default_factory=list)
    is_loading: bool = False
    error_message: Optional[str] = None


class DatabaseViewModel(BaseViewModel[DatabaseState]):
    """
    ViewModel for the Database Management Page.
    """

    def __init__(self, lawyer_repo: LawyerRepository, alias_repo: AliasRepository):
        super().__init__(DatabaseState())
        self._lawyer_repo = lawyer_repo
        self._alias_repo = alias_repo

    def load_data(self):
        """Intent: Load all initial data."""
        self.update_state(is_loading=True)
        try:
            lawyers = self._lawyer_repo.get_all()
            aliases = self._alias_repo.get_all()
            self.update_state(lawyers=lawyers, aliases=aliases, is_loading=False)
        except Exception as e:
            self.update_state(is_loading=False, error_message=str(e))
            self.emit_effect(
                {"type": "toast", "message": f"Load failed: {e}", "level": "error"}
            )

    def add_lawyer(self, code: str):
        """Intent: Add a new lawyer."""
        if not code or not code.strip():
            self.emit_effect(
                {"type": "toast", "message": "Code cannot be empty", "level": "warning"}
            )
            return

        self.update_state(is_loading=True)
        try:
            self._lawyer_repo.add(Lawyer(code=code.strip()))

            # Refresh list
            lawyers = self._lawyer_repo.get_all()
            self.update_state(lawyers=lawyers, is_loading=False)
            self.emit_effect(
                {"type": "toast", "message": f"Lawyer {code} added", "level": "success"}
            )
        except Exception as e:
            self.update_state(is_loading=False, error_message=str(e))
            self.emit_effect(
                {"type": "toast", "message": f"Add failed: {e}", "level": "error"}
            )
