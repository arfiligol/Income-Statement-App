from nicegui import ui

from app.ui.components.layout.shell import app_shell
from app.ui.components.widgets.file_source_picker import FileSourcePicker
from app.ui.viewmodels.statement_vm import StatementViewModel


class StatementEditorPage:
    """
    The main page for editing Income Statements.
    Replaces the old 'WorkflowPage'.
    """

    def __init__(self, vm: StatementViewModel):
        self.vm = vm
        self.lbl_file_status = None
        self.step2_card = None
        self.lbl_autofill_status = None

    def render(self):
        # We hook up the shell
        app_shell(self._render_content)

    def _render_content(self):
        # Setup Effect Listeners
        self.vm.on_effect(self._handle_effect)
        self.vm.add_listener(self._on_state_change)

        # Header
        ui.label("工具包 (Toolbox)").classes("text-3xl font-bold mb-2")
        ui.label("管理資料處理工作流").classes("text-slate-500 mb-8")

        # Step 1: File Selection
        with ui.card().classes(
            "w-full p-6 rounded-xl border border-slate-200 shadow-sm dark:bg-slate-800 dark:border-slate-700 mb-6"
        ):
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-4"):
                    ui.icon("upload_file", size="32px").classes("text-indigo-500")
                    with ui.column().classes("gap-1"):
                        ui.label("Step 1: 選擇來源檔案").classes("text-lg font-bold")
                        # State Binding: File Label
                        self.lbl_file_status = ui.label("尚未選擇").classes(
                            "text-sm text-slate-400"
                        )

                # Component: File Picker
                FileSourcePicker(on_file_selected=self.vm.handle_file_selected)

        # Step 2: Auto Fill (Lawyer Codes)
        self.step2_card = ui.card().classes(
            "w-full p-6 rounded-xl border border-slate-200 shadow-sm dark:bg-slate-800 dark:border-slate-700 opacity-50 pointer-events-none"
        )
        with self.step2_card:
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-4"):
                    ui.icon("autofill", size="32px").classes(
                        "text-indigo-500"
                    )  # 'autofill' might not be valid material icon, checking... 'auto_fix_high' is better
                    with ui.column().classes("gap-1"):
                        ui.label("Step 2: 自動補全律師代碼").classes(
                            "text-lg font-bold"
                        )
                        ui.label(
                            "系統將掃描 Excel 並嘗試填入代碼。若有不明確項目，將會詢問您。"
                        ).classes("text-sm text-slate-500")
                        self.lbl_autofill_status = ui.label("等待執行...").classes(
                            "text-xs font-mono text-indigo-400 mt-1"
                        )

                ui.button(
                    "執行自動檢查",
                    icon="play_arrow",
                    on_click=self.vm.handle_run_auto_fill,
                ).classes(
                    "bg-indigo-600 text-white shadow-sm rounded-lg px-4 py-2"
                ).props("unelevated no-caps")

    def _on_state_change(self, state):
        # Update File Label
        if state.file_source:
            self.lbl_file_status.text = f"已選擇: {state.file_source.filename}"
            # Enable Step 2
            self.step2_card.classes(remove="opacity-50 pointer-events-none")
        else:
            self.lbl_file_status.text = "尚未選擇檔案"
            self.step2_card.classes(add="opacity-50 pointer-events-none")

        # Update AutoFill Status
        if state.auto_fill_result:
            self.lbl_autofill_status.text = (
                f"完成！修正了 {state.auto_fill_result.updated_count} 筆資料。"
            )
            self.lbl_autofill_status.classes(replace="text-green-500")
        elif state.is_loading:
            self.lbl_autofill_status.text = "執行中..."
        else:
            # Reset if needed, or keep last state
            pass

        if state.is_loading:
            ui.notify("Loading...", type="info")  # Or show spinner

    def _handle_effect(self, effect):
        if effect.get("type") == "toast":
            ui.notify(effect["message"], type=effect.get("level", "info"))
