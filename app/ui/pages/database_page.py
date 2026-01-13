from nicegui import ui

from app.ui.components.layout.shell import app_shell
from app.ui.viewmodels.database_vm import DatabaseViewModel


class DatabasePage:
    """
    Page for managing Database (Lawyers, Aliases).
    """

    def __init__(self, vm: DatabaseViewModel):
        self.vm = vm
        self.table_lawyers = None
        self.table_aliases = None
        self.input_code = None

    def render(self):
        app_shell(self._render_content)
        # Load initial data
        self.vm.load_data()

    def _render_content(self):
        self.vm.on_effect(self._handle_effect)
        self.vm.add_listener(self._on_state_change)

        # Header
        with ui.row().classes("w-full items-end justify-between mb-6"):
            with ui.column().classes("gap-1"):
                ui.label("資料庫管理 (Database)").classes("text-3xl font-bold")
                ui.label("管理律師與別名設定").classes("text-muted")

        # Tabs
        with ui.card().classes(
            "w-full p-0 shadow-sm border border-border rounded-xl bg-surface overflow-hidden"
        ):
            with ui.tabs().classes(
                "w-full text-muted bg-bg border-b border-border active-text-primary indicator-color-primary"
            ) as tabs:
                lawyer_tab = ui.tab("律師名單", icon="groups").classes(
                    "h-14 font-medium"
                )
                alias_tab = ui.tab("別名設定", icon="badge").classes("h-14 font-medium")

            with ui.tab_panels(tabs, value=lawyer_tab).classes(
                "w-full p-6 bg-bg"
            ):
                # Lawyer Panel
                with ui.tab_panel(lawyer_tab):
                    with ui.row().classes("w-full items-center justify-between mb-4"):
                        ui.label("所有律師代碼").classes("text-lg font-bold")
                        with ui.row().classes("items-center gap-2"):
                            self.input_code = (
                                ui.input(placeholder="新代碼")
                                .props("dense outlined")
                                .classes("w-40")
                            )
                            ui.button("新增", on_click=self._on_add_click).classes(
                                "app-btn-primary rounded-lg shadow-sm"
                            ).props("unelevated no-caps")

                    cols = [
                        {
                            "name": "code",
                            "label": "律師代碼",
                            "field": "code",
                            "align": "left",
                        },
                        {
                            "name": "name",
                            "label": "名稱",
                            "field": "name",
                            "align": "left",
                        },
                    ]
                    self.table_lawyers = (
                        ui.table(columns=cols, rows=[], pagination=10)
                        .classes("w-full")
                        .props("flat")
                    )

                # Alias Panel
                with ui.tab_panel(alias_tab):
                    ui.label("別名設定").classes("text-lg font-bold mb-4")
                    cols_alias = [
                        {
                            "name": "source",
                            "label": "關鍵字",
                            "field": "source",
                            "align": "left",
                        },
                        {
                            "name": "targets",
                            "label": "對應代碼",
                            "field": "targets",
                            "align": "left",
                        },
                    ]
                    self.table_aliases = (
                        ui.table(columns=cols_alias, rows=[], pagination=10)
                        .classes("w-full")
                        .props("flat")
                    )

    def _on_add_click(self):
        if self.input_code:
            self.vm.add_lawyer(self.input_code.value)
            self.input_code.value = ""

    def _on_state_change(self, state):
        if self.table_lawyers:
            self.table_lawyers.rows = [
                {"code": l.code, "name": l.name} for l in state.lawyers
            ]
            self.table_lawyers.update()

        if self.table_aliases:
            self.table_aliases.rows = [
                {"source": a.source_code, "targets": ", ".join(a.target_codes)}
                for a in state.aliases
            ]
            self.table_aliases.update()

    def _handle_effect(self, effect):
        if effect.get("type") == "toast":
            ui.notify(effect["message"], type=effect.get("level", "info"))
