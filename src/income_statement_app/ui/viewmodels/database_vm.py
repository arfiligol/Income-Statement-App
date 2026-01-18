from dataclasses import dataclass, field


from income_statement_app.application.ports.repositories import (
    CodeReplacementRepository,
    LawyerRepository,
)
from income_statement_app.domain.dto.code_replacement import CodeReplacement
from income_statement_app.domain.dto.lawyer import Lawyer
from income_statement_app.ui.viewmodels.base import BaseViewModel


@dataclass
class DatabaseState:
    lawyers: list[Lawyer] = field(default_factory=list)
    replacements: list[CodeReplacement] = field(default_factory=list)
    is_loading: bool = False
    error_message: str | None = None


class DatabaseViewModel(BaseViewModel[DatabaseState]):
    """
    ViewModel for the Database Management Page.
    """

    def __init__(
        self, lawyer_repo: LawyerRepository, replacement_repo: CodeReplacementRepository
    ):
        super().__init__(DatabaseState())
        self._lawyer_repo = lawyer_repo
        self._replacement_repo = replacement_repo

    def load_data(self):
        """Intent: Load all initial data."""
        self.update_state(is_loading=True)
        try:
            lawyers = self._lawyer_repo.get_all()
            replacements = self._replacement_repo.get_all()
            self.update_state(
                lawyers=lawyers, replacements=replacements, is_loading=False
            )
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

    def add_replacement(self, source: str, targets: str):
        """Intent: Add a new replacement rule."""
        if not source or not targets:
            self.emit_effect(
                {
                    "type": "toast",
                    "message": "Source and Targets cannot be empty",
                    "level": "warning",
                }
            )
            return

        # Parse targets to check for existence
        target_list = [
            t.strip() for t in targets.replace("，", ",").split(",") if t.strip()
        ]
        if not target_list:
            self.emit_effect(
                {
                    "type": "toast",
                    "message": "Targets cannot be empty",
                    "level": "warning",
                }
            )
            return

        # Check missing lawyers
        # We rely on current state for existing lawyers check
        existing_codes = {l.code for l in self.state.lawyers}
        missing = [code for code in target_list if code not in existing_codes]

        if missing:
            self.emit_effect(
                {
                    "type": "confirm_create_lawyers",
                    "message": f"發現未建立的律師代碼: {', '.join(missing)}。\n是否要自動建立這些代碼並儲存規則？",
                    "payload": {
                        "source": source,
                        "targets": targets,
                        "missing": missing,
                    },
                }
            )
            return

        # Check if source already exists
        existing = self._replacement_repo.get_by_source(source.strip())
        if existing:
            self.emit_effect(
                {
                    "type": "toast",
                    "message": f"代碼 '{source}' 的替換規則已存在，請先刪除舊規則。",
                    "level": "warning",
                }
            )
            return

        # Validate and Normalize
        normalized_targets = ", ".join(target_list)

        try:
            item = CodeReplacement(
                id=None, source_code=source.strip(), target_codes=normalized_targets
            )
            self._replacement_repo.add(item)
            self._reload_replacements()
            self.emit_effect(
                {"type": "toast", "message": "Replacement added", "level": "success"}
            )
        except Exception as e:
            self.emit_effect(
                {
                    "type": "toast",
                    "message": f"Add replacement failed: {e}",
                    "level": "error",
                }
            )

    def confirm_add_replacement_with_new_lawyers(
        self, source: str, targets: str, new_codes: list[str]
    ):
        """Intent: Create missing lawyers and then add replacement."""
        try:
            self._lawyer_repo.ensure_exists(new_codes)
            # Reload lawyers to update state and ensure checking passes
            self.update_state(lawyers=self._lawyer_repo.get_all())

            # Proceed to add replacement
            self.add_replacement(source, targets)
        except Exception as e:
            self.emit_effect(
                {
                    "type": "toast",
                    "message": f"Failed to create lawyers: {e}",
                    "level": "error",
                }
            )

    def delete_replacement(self, id: int):
        """Intent: Delete a replacement rule."""
        try:
            self._replacement_repo.delete(id)
            self._reload_replacements()
            self.emit_effect(
                {"type": "toast", "message": "Replacement deleted", "level": "info"}
            )
        except Exception as e:
            self.emit_effect(
                {
                    "type": "toast",
                    "message": f"Delete failed: {e}",
                    "level": "error",
                }
            )

    def update_replacement(self, item: CodeReplacement):
        """Intent: Update a replacement rule."""
        try:
            self._replacement_repo.update(item)
            self._reload_replacements()
            self.emit_effect(
                {"type": "toast", "message": "Replacement updated", "level": "success"}
            )
        except Exception as e:
            self.emit_effect(
                {
                    "type": "toast",
                    "message": f"Update failed: {e}",
                    "level": "error",
                }
            )

    def _reload_replacements(self):
        replacements = self._replacement_repo.get_all()
        self.update_state(replacements=replacements)
