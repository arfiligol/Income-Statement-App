from nicegui import ui

from domain.dto.auto_fill import AutoFillResponse


class LawyerSelectionDialog:
    """
    A custom dialog for selecting or inputting lawyer codes.
    Uses ui.dialog() with a custom Tailwind-styled card.
    """

    def __init__(self, row_number: int, summary: str, available_codes: list[str]):
        self.row_number = row_number
        self.summary = summary
        self.available_codes = available_codes
        self._dialog = ui.dialog()
        self._result: AutoFillResponse | None = None
        self._selected_values = []
        self._manual_input = None

        with self._dialog, ui.card().classes("w-[600px] p-0 gap-0 app-card"):
            self._render_header()
            self._render_content()
            self._render_footer()

    def _render_header(self):
        with ui.row().classes(
            "w-full items-center justify-between p-4 border-b border-border"
        ):
            with ui.row().classes("items-center gap-2"):
                ui.icon("gavel", size="24px").classes("text-primary")
                ui.label(f"Row {self.row_number}: 補全律師代碼").classes(
                    "text-lg font-bold text-fg"
                )
            ui.button(icon="close", on_click=self.abort).props(
                "flat round dense"
            ).classes("text-muted hover:text-fg")

    def _render_content(self):
        with ui.column().classes("w-full p-6 gap-6"):
            # Context
            with ui.column().classes("w-full gap-2"):
                ui.label("摘要內容 (Summary)").classes("text-sm font-bold text-muted")
                ui.label(self.summary).classes(
                    "w-full p-3 bg-bg rounded border border-border text-fg font-mono"
                )

            # Selection
            with ui.column().classes("w-full gap-4"):
                ui.label("選擇律師代碼").classes("text-sm font-bold text-muted")

                # Multi-select for existing
                if not self.available_codes:
                    ui.label("⚠️ 資料庫尚無律師代碼，請先手動輸入。").classes(
                        "text-sm text-warning italic"
                    )
                    self._select = ui.select(options=[]).classes(
                        "hidden"
                    )  # Hidden dummy
                else:
                    self._select = (
                        ui.select(
                            options=self.available_codes,
                            multiple=True,
                            label="現有列表",
                            with_input=True,
                        )
                        .classes("w-full")
                        .props("outlined dense use-chips")
                    )

                # Manual Input
                self._manual_input = (
                    ui.input(
                        label="手動輸入 (用逗號隔開)",
                        placeholder="例如: NEW1, NEW2",
                    )
                    .classes("w-full")
                    .props("outlined dense")
                )

    def _render_footer(self):
        with ui.row().classes(
            "w-full items-center justify-between p-4 bg-bg border-t border-border rounded-b-xl"
        ):
            # Left Actions (Skips)
            with ui.row().classes("gap-2"):
                ui.button("跳過全部", on_click=self.skip_all).classes(
                    "text-muted hover:text-fg"
                ).props("flat no-caps")

                ui.button("跳過此筆", on_click=self.skip).classes(
                    "text-muted hover:text-fg"
                ).props("flat no-caps")

            # Right Actions (Submit)
            ui.button("確認 (Confirm)", on_click=self.submit).classes(
                "app-btn-primary px-6"
            ).props("unelevated no-caps")

    def open(self):
        self._dialog.open()

    def close(self):
        self._dialog.close()

    async def await_result(self) -> AutoFillResponse:
        self.open()
        await self._dialog
        return self._result or AutoFillResponse(selected_codes=[], action="abort")

    def submit(self):
        # Merge selection + manual
        codes = []
        if self.available_codes:
            codes = list(self._select.value or [])

        manual_text = self._manual_input.value
        if manual_text:
            manual_codes = [c.strip() for c in manual_text.split(",") if c.strip()]
            codes.extend(manual_codes)

        # Deduplicate
        codes = list(dict.fromkeys(codes))

        self._result = AutoFillResponse(selected_codes=codes, action="submit")
        self.close()

    def skip(self):
        self._result = AutoFillResponse(selected_codes=[], action="skip")
        self.close()

    def skip_all(self):
        self._result = AutoFillResponse(selected_codes=[], action="skip_all")
        self.close()

    def abort(self):
        self._result = AutoFillResponse(selected_codes=[], action="abort")
        self.close()
