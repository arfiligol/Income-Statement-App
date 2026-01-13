from typing import Callable

from nicegui import events, ui

from app.domain.dto.file_source import FileSource


class FileSourcePicker(ui.element):
    """
    A unified File Picker component.
    - Web Mode: Uses ui.upload (hidden) + ui.button trigger.
    - Native Mode: Uses ui.button -> emits pick intent.
    """

    def __init__(
        self, on_file_selected: Callable[[FileSource], None], is_native: bool = False
    ):
        super().__init__("div")
        self.on_file_selected = on_file_selected
        self.is_native = is_native

        with self:
            self.render()

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
            "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm rounded-lg text-sm px-4 py-2"
        ).props("unelevated no-caps").on(
            "click", js_handler=f"getElement({self.upload.id}).pickFiles()"
        )

    def _handle_web_upload(self, e: events.UploadEventArguments):
        # In NiceGUI, e.content is a temporary file-like object or we can get path
        # Typically e.name is filename, e.content is SpooledTemporaryFile
        # For simplicity in this DTO, we assume we can treat it as a bytes source or temp path
        # But wait, to be robust, we should probably save it to a temp dir managed by infra?
        # For now, let's assume the Gateway/Repo knows how to handle the 'upload_id' or we pass the object differently.
        # Ideally, we convert to FileSource right here.

        # NOTE: In a real implementation we might need to persist `e.content` to a known temp path
        # so Pandas can read it easily via path.

        source = FileSource(
            upload_id=str(e.sender.id), filename=e.name
        )  # Placeholder ID
        # HACK: Attach the content directly for now so Repo can read it?
        # Clean Architecture says DTO shouldn't hold binary streams ideally,
        # but for simplicity let's assume infrastructure resolves 'upload_id'.
        # Actually better: NiceGUI's handle_upload runs on server. We can save to /tmp.

        import shutil
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            shutil.copyfileobj(e.content, tmp)
            temp_path = tmp.name

        source = FileSource(path=temp_path, filename=e.name)
        self.on_file_selected(source)

    def _handle_native_pick(self):
        # Logic to trigger native dialog usually goes through a VM intent -> Gateway
        # But here we are the UI component.
        # If we want to support "VM handles pick", we should emit an event "pick_requested".
        # But for this component, let's assume we just emit 'file_selected' if we can?
        # Only if we can self-manage. If not, we need an 'on_pick_requested' callback.
        # Let's keep it simple: Web Native Parity.
        pass
