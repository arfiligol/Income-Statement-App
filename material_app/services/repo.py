"""Repository helpers delegating to legacy ttk_app modules."""

from ttk_app.db.crud.lawyer import fetch_all_lawyers, insert_unique_lawyers  # re-export for convenience

__all__ = ["fetch_all_lawyers", "insert_unique_lawyers"]
