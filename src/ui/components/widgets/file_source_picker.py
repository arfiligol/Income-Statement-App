import asyncio
from typing import Callable


from nicegui import events, ui

from domain.dto.file_source import FileSource


class FileSourcePicker(ui.element):
    """
    A unified File Picker component.
    - Web Mode: Uses ui.upload (hidden) + ui.button trigger.
    - Native Mode: Uses ui.button -> emits pick intent.
    """

    def __init__(
        self,
        on_file_selected: Callable[[FileSource], None],
        is_native: bool | None = None,
    ):
        super().__init__("div")
        from nicegui import app

        self.on_file_selected = on_file_selected
        if is_native is None:
            import sys

            # Simple heuristic: If main.py requested native=True, usually 'webview' is imported.
            self.is_native = "webview" in sys.modules
            print(f"DEBUG: Auto-detected native mode: {self.is_native}")
        else:
            self.is_native = is_native

        with self:
            self.render()

    def _emit_file_selected(self, source: FileSource) -> None:
        result = self.on_file_selected(source)
        if asyncio.iscoroutine(result):
            asyncio.create_task(result)

    def render(self):
        with ui.row().classes("items-center gap-4 relative"):
            if self.is_native:
                # Native Mode: Simple Button
                ui.button(
                    "Select File (Native)",
                    icon="folder_open",
                    on_click=self._handle_native_pick,
                ).props("unelevated no-caps")
            else:
                # Web Mode: Hidden Upload + Trigger Button
                self._setup_web_upload()

    def _setup_web_upload(self):
        # We use the detailed "hidden opacity-0" trick for robust web upload
        self.upload = (
            ui.upload(
                auto_upload=True,
                on_upload=self._handle_web_upload,
                max_files=1,
            )
            .props('accept=".xlsx,.xls" flat')
            .classes("absolute top-0 left-0 w-0 h-0 opacity-0 overflow-hidden")
        )

        ui.button("選擇 Excel 檔案", icon="upload_file").classes(
            "app-btn-primary shadow-sm rounded-lg text-sm px-4 py-2"
        ).props("unelevated no-caps").on(
            "click", lambda: self.upload.run_method("pickFiles")
        )

    def _handle_web_upload(self, e: events.UploadEventArguments):
        import shutil
        import tempfile

        upload = e.file
        filename = upload.filename or "upload.xlsx"
        upload.file.seek(0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            shutil.copyfileobj(upload.file, tmp)
            temp_path = tmp.name

        source = FileSource(path=temp_path, filename=filename)
        self._emit_file_selected(source)

    async def _handle_native_pick(self):
        try:
            from nicegui import app
            import webview

            # Verify if native mode is active and main_window is available
            if not app.native.main_window:
                ui.notify("Native window not available", type="warning")
                return

            file_paths = await app.native.main_window.create_file_dialog(
                dialog_type=webview.FileDialog.OPEN,
                allow_multiple=False,
                file_types=("Excel Files (*.xlsx;*.xls)", "All Files (*.*)"),
            )

            if file_paths and len(file_paths) > 0:
                # Native dialog returns a tuple or list of strings
                path = file_paths[0]
                # In native mode, we access the file directly
                source = FileSource(path=path, filename=path.split("/")[-1])
                self._emit_file_selected(source)

        except Exception as e:
            ui.notify(f"Native Pick Failed: {e}", type="error")
