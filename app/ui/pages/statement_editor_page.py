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
        self.step3_card = None
        self.lbl_autofill_status = None
        self.lbl_ledger_status = None
        self.link_download = None

    def render(self):
        # We hook up the shell
        app_shell(self._render_content)

    def _render_content(self):
        # Setup Effect Listeners
        self.vm.on_effect(self._handle_effect)
        self.vm.add_listener(self._on_state_change)

        # Header
        ui.label("工具包 (Toolbox)").classes("text-3xl font-bold mb-2")
        ui.label("管理資料處理工作流 (Clean Architecture)").classes("text-muted mb-8")

        # Step 1: File Selection
        with ui.card().classes(
            "w-full p-6 app-card text-fg mb-6"
        ):
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-4"):
                    ui.icon("upload_file", size="32px").classes("text-primary")
                    with ui.column().classes("gap-1"):
                        ui.label("Step 1: 選擇來源檔案").classes("text-lg font-bold")
                        self.lbl_file_status = ui.label("尚未選擇").classes(
                            "text-sm text-muted"
                        )

                FileSourcePicker(on_file_selected=self.vm.handle_file_selected)

        # Step 2: Auto Fill
        self.step2_card = ui.card().classes(
            "w-full p-6 app-card opacity-50 pointer-events-none mb-6"
        )
        with self.step2_card:
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-4"):
                    ui.icon("auto_fix_high", size="32px").classes("text-primary")
                    with ui.column().classes("gap-1"):
                        ui.label("Step 2: 自動補全律師代碼").classes(
                            "text-lg font-bold"
                        )
                        ui.label("掃描 Excel 並補全代碼。").classes("text-sm text-muted")
                        self.lbl_autofill_status = ui.label("等待執行...").classes(
                            "text-xs font-mono text-primary mt-1"
                        )

                ui.button(
                    "執行自動檢查",
                    icon="play_arrow",
                    on_click=self.vm.handle_run_auto_fill,
                ).classes(
                    "app-btn-primary shadow-sm rounded-lg px-4 py-2"
                ).props("unelevated no-caps")

        # Step 3: Separate Ledger
        self.step3_card = ui.card().classes(
            "w-full p-6 app-card opacity-50 pointer-events-none"
        )
        with self.step3_card:
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-4"):
                    ui.icon("summarize", size="32px").classes("text-primary")
                    with ui.column().classes("gap-1"):
                        ui.label("Step 3: 產生分帳報表").classes("text-lg font-bold")
                        ui.label("計算分帳金額並匯出報表。").classes("text-sm text-muted")
                        self.lbl_ledger_status = ui.label("等待執行...").classes(
                            "text-xs font-mono text-primary mt-1"
                        )

                with ui.column().classes("items-end"):
                    ui.button(
                        "產生報表",
                        icon="description",
                        on_click=self.vm.handle_run_separate_ledger,
                    ).classes(
                        "app-btn-primary shadow-sm rounded-lg px-4 py-2"
                    ).props("unelevated no-caps")
                    # Link to download (Wait, local native path vs web download)
                    # If Native mode, we just show path. If Web, could use ui.download.
                    self.link_download = ui.link("開啟檔案", "#").classes(
                        "text-xs text-primary mt-2 hidden"
                    )

    def _on_state_change(self, state):
        # Update File Label
        if state.file_source:
            self.lbl_file_status.text = f"已選擇: {state.file_source.filename}"
            self.step2_card.classes(remove="opacity-50 pointer-events-none")
        else:
            self.lbl_file_status.text = "尚未選擇檔案"
            self.step2_card.classes(add="opacity-50 pointer-events-none")
            self.step3_card.classes(add="opacity-50 pointer-events-none")

        # Update AutoFill Status & Step 3 Enable
        if state.auto_fill_result:
            self.lbl_autofill_status.text = (
                f"完成！修正 {state.auto_fill_result.updated_count} 筆。"
            )
            self.lbl_autofill_status.classes(replace="text-success")
            self.step3_card.classes(remove="opacity-50 pointer-events-none")
        elif state.is_loading and not state.separate_ledger_result:
            # Only show loading on Step 2 label if step 3 not active? Simplified logic.
            self.lbl_autofill_status.text = "執行中..."

        # Update Ledger Status
        if state.separate_ledger_result:
            path = state.separate_ledger_result.output_path
            self.lbl_ledger_status.text = f"報表已產生: {path}"
            self.lbl_ledger_status.classes(replace="text-success")
            # Link logic todo if needed

        if state.is_loading:
            ui.notify("Loading...", type="info")

    def _handle_effect(self, effect):
        if effect.get("type") == "toast":
            ui.notify(effect["message"], type=effect.get("level", "info"))
