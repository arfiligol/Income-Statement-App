from nicegui import ui
from nicegui.functions import notify as notify_fn

from app.ui.components.layout.shell import app_shell
from app.ui.viewmodels.database_vm import DatabaseViewModel


class DatabasePage:
    """
    Page for managing Database (Lawyers, Aliases).
    """

    def __init__(self, vm: DatabaseViewModel):
        self.vm = vm
        self.table_lawyers = None
        self.table_replacements = None
        self.input_code = None
        self.input_source = None
        self.input_targets = None
        self._client = None

    def render(self):
        app_shell(self._render_content)
        # Load initial data
        self.vm.load_data()

    def render_content(self):
        self._render_content()
        self.vm.load_data()

    def _render_content(self):
        self._client = ui.context.client

        self.vm.on_effect(self._handle_effect)
        self.vm.add_listener(self._on_state_change)

        # Header
        with ui.row().classes("w-full items-end justify-between mb-6"):
            with ui.column().classes("gap-1"):
                ui.label("資料庫管理 (Database)").classes("text-3xl font-bold")
                ui.label("管理律師代碼與自動替換規則").classes("text-muted")

        # Main Card with Tabs
        with ui.card().classes(
            "w-full p-0 shadow-sm border border-border rounded-xl bg-surface overflow-hidden"
        ):
            with ui.tabs().classes(
                "w-full text-muted border-b border-border active-text-primary indicator-color-primary"
            ) as tabs:
                tab_lawyers = ui.tab("律師代碼", icon="groups").classes(
                    "h-14 font-medium"
                )
                tab_replacements = ui.tab("自動替換", icon="rule").classes(
                    "h-14 font-medium"
                )

            with (
                ui.tab_panels(tabs, value=tab_lawyers)
                .classes("w-full p-6 bg-transparent")
                .props("animated transition-prev=fade transition-next=fade")
            ):
                # Tab 1: Lawyers
                with ui.tab_panel(tab_lawyers).classes("p-0"):
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
                    ]
                    self.table_lawyers = (
                        ui.table(columns=cols, rows=[], pagination=10)
                        .classes("w-full")
                        .props("flat")
                    )

                # Tab 2: Replacements
                with ui.tab_panel(tab_replacements).classes("p-0"):
                    with ui.column().classes("w-full gap-4"):
                        ui.label("自動替換規則 (Step 2)").classes("text-lg font-bold")
                        with ui.row().classes("w-full items-center gap-2"):
                            self.input_source = (
                                ui.input(placeholder="來源代碼 (如 KW)")
                                .props("dense outlined")
                                .classes("w-40")
                            )
                            ui.label("➜").classes("text-muted font-bold")
                            self.input_targets = (
                                ui.input(placeholder="替換目標 (如 KW, HL, JH)")
                                .props("dense outlined")
                                .classes("flex-grow")
                            )
                            ui.button(
                                "新增替換", on_click=self._on_add_replacement_click
                            ).classes("app-btn-primary rounded-lg shadow-sm").props(
                                "unelevated no-caps"
                            )

                        cols_rep = [
                            {
                                "name": "id",
                                "label": "ID",
                                "field": "id",
                                "align": "left",
                                "sortable": True,
                            },
                            {
                                "name": "source_code",
                                "label": "來源代碼",
                                "field": "source_code",
                                "align": "left",
                                "sortable": True,
                            },
                            {
                                "name": "target_codes",
                                "label": "替換目標",
                                "field": "target_codes",
                                "align": "left",
                            },
                            {
                                "name": "actions",
                                "label": "操作",
                                "field": "actions",
                                "align": "center",
                            },
                        ]
                        self.table_replacements = (
                            ui.table(columns=cols_rep, rows=[], pagination=10)
                            .classes("w-full")
                            .props("flat")
                        )
                        # Add Action Slots
                        self.table_replacements.add_slot(
                            "body-cell-actions",
                            r"""
                            <q-td key="actions" :props="props">
                                <q-btn icon="delete" flat dense color="negative" size="sm" 
                                    @click="$parent.$emit('delete_rep', props.row)" 
                                />
                            </q-td>
                        """,
                        )
                        self.table_replacements.on(
                            "delete_rep",
                            lambda e: self.vm.delete_replacement(e.args["id"]),
                        )

    def _on_add_click(self):
        if self.input_code:
            self.vm.add_lawyer(self.input_code.value)
            self.input_code.value = ""

    def _on_add_replacement_click(self):
        if self.input_source and self.input_targets:
            self.vm.add_replacement(self.input_source.value, self.input_targets.value)
            self.input_source.value = ""
            self.input_targets.value = ""

    def _on_state_change(self, state):
        if self.table_lawyers:
            self.table_lawyers.rows = [{"code": l.code} for l in state.lawyers]
            self.table_lawyers.update()

        if self.table_replacements:
            self.table_replacements.rows = [
                {
                    "id": r.id,
                    "source_code": r.source_code,
                    "target_codes": r.target_codes,
                }
                for r in state.replacements
            ]
            self.table_replacements.update()

    async def _on_confirm_create(self, dialog, payload):
        dialog.close()
        self.vm.confirm_add_replacement_with_new_lawyers(
            payload["source"], payload["targets"], payload["missing"]
        )

    def _show_confirm_dialog(self, effect):
        msg = effect["message"]
        payload = effect["payload"]
        with ui.dialog() as dialog, ui.card():
            ui.label("建立缺少的律師代碼？").classes("text-lg font-bold")
            ui.label(msg).classes("whitespace-pre-wrap")
            with ui.row().classes("w-full justify-end"):
                ui.button("取消", on_click=dialog.close).props("flat")
                ui.button(
                    "建立並儲存",
                    on_click=lambda: self._on_confirm_create(dialog, payload),
                ).classes("bg-primary text-white")
        dialog.open()

    def _handle_effect(self, effect):
        if effect.get("type") == "toast":
            self._notify(effect["message"], level=effect.get("level", "info"))
        elif effect.get("type") == "confirm_create_lawyers":
            self._show_confirm_dialog(effect)

    def _notify(self, message: str, level: str = "info") -> None:
        if not self._client:
            return
        options = {"message": str(message), "type": level}
        options = {notify_fn.ARG_MAP.get(k, k): v for k, v in options.items()}
        self._client.outbox.enqueue_message("notify", options, self._client.id)
