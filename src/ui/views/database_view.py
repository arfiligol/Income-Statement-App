from nicegui import ui

from src.data.repositories.alias_repository import AliasRepository
from src.data.repositories.lawyer_repository import LawyerRepository


class DatabasePage:
    def __init__(self, lawyer_repo: LawyerRepository, alias_repo: AliasRepository):
        self.lawyer_repo = lawyer_repo
        self.alias_repo = alias_repo
        self.new_lawyer_code = ""

    # Removed render() that wraps main_layout

    def render_content(self):
        self._content()

    def _content(self):
        # Header
        with ui.row().classes("w-full items-end justify-between mb-6"):
            with ui.column().classes("gap-1"):
                ui.label("資料庫管理 (Database)").classes(
                    "text-2xl font-bold text-slate-800 tracking-tight dark:text-white"
                )
                ui.label("管理律師與別名設定").classes(
                    "text-sm text-slate-500 font-medium dark:text-slate-400"
                )

        with ui.card().classes(
            "w-full p-0 shadow-sm border border-slate-200 rounded-xl bg-white overflow-hidden dark:bg-slate-800 dark:border-slate-700"
        ):
            with ui.tabs().classes(
                "w-full text-slate-500 bg-slate-50 border-b border-slate-200 active-text-indigo-600 indicator-color-indigo dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400 dark:active-text-indigo-400"
            ) as tabs:
                lawyer_tab = ui.tab("律師名單", icon="groups").classes(
                    "h-14 font-medium"
                )
                alias_tab = ui.tab("別名設定", icon="badge").classes("h-14 font-medium")

            with ui.tab_panels(tabs, value=lawyer_tab).classes("w-full p-6"):
                # Tab 1: Lawyer List
                with ui.tab_panel(lawyer_tab):
                    with ui.row().classes("w-full items-center justify-between mb-4"):
                        ui.label("所有律師代碼").classes(
                            "text-lg font-bold text-slate-700 dark:text-slate-200"
                        )

                        with ui.row().classes("items-center gap-2"):
                            self.input_code = (
                                ui.input(placeholder="新代碼 (如 501)")
                                .props("dense outlined")
                                .classes("w-40")
                            )
                            ui.button("新增", on_click=self.add_lawyer).props(
                                "unelevated color=indigo"
                            ).classes("rounded-lg shadow-sm")

                    # Table with Tailwind styling via props is harder, Quasar table has its own style.
                    # We can style the container or use props.
                    columns = [
                        {
                            "name": "code",
                            "label": "律師代碼",
                            "field": "code",
                            "required": True,
                            "align": "left",
                        },
                        {
                            "name": "name",
                            "label": "名稱 (預留)",
                            "field": "name",
                            "align": "left",
                        },
                    ]
                    rows = [
                        {"code": l.code, "name": l.name}
                        for l in self.lawyer_repo.get_all()
                    ]

                    self.lawyer_table = (
                        ui.table(columns=columns, rows=rows, pagination=10)
                        .classes("w-full text-slate-700 dark:text-slate-300")
                        .props("flat bordered")
                    )

                # Tab 2: Aliases
                with ui.tab_panel(alias_tab):
                    ui.label("別名設定").classes(
                        "text-lg font-bold text-slate-700 mb-4 dark:text-slate-200"
                    )
                    # ... alias content implementation ...
                    columns = [
                        {
                            "name": "alias",
                            "label": "Excel 摘要關鍵字",
                            "field": "alias",
                            "align": "left",
                        },
                        {
                            "name": "code",
                            "label": "對應律師代碼",
                            "field": "lawyer_code",
                            "align": "left",
                        },
                    ]
                    rows = [
                        {
                            "alias": a.source_code,
                            "lawyer_code": ", ".join(a.target_codes),
                        }
                        for a in self.alias_repo.get_all()
                    ]
                    ui.table(columns=columns, rows=rows, pagination=10).classes(
                        "w-full text-slate-700 dark:text-slate-300"
                    ).props("flat bordered")
        self._refresh_lawyers()

    def _refresh_lawyers(self):
        self.lawyers = self.lawyer_repo.get_all()
        self.lawyer_table.rows = [
            {"code": l.code, "name": l.name} for l in self.lawyers
        ]
        self.lawyer_table.update()

    def add_lawyer(self):
        new_code = self.input_code.value
        if new_code:
            self.lawyer_repo.add(new_code, new_code)  # Name default to code
            ui.notify(f"Added {new_code}")
            self.input_code.set_value("")  # Clear input after adding
            self._refresh_lawyers()
