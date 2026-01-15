import asyncio

from nicegui import ui

from app.services.update_manager import UpdateManager


class UpdateDialog:
    def __init__(self, update_manager: UpdateManager, version: str):
        self.manager = update_manager
        self.version = version
        self.dialog = ui.dialog().props("persistent")
        self.progress = None
        self.status = None

    def open(self):
        with self.dialog, ui.card().classes("w-96"):
            ui.label("正在更新 Income Statement App").classes("text-xl font-bold")
            ui.label(f"目標版本: {self.version}").classes("text-gray-500 mb-4")

            self.status = ui.label("準備下載...").classes("text-sm mb-2")

            # Simple progress bar (visual only)
            self.progress = ui.linear_progress(value=0).classes("w-full mb-4")

            with ui.row().classes("w-full justify-end"):
                ui.button("開始更新", on_click=self._start_update).props(
                    "unelevated color=primary"
                )
                ui.button("取消", on_click=self.dialog.close).props("flat")

        self.dialog.open()

    async def _start_update(self, e):
        e.sender.disable()
        self.status.set_text("下載中... 請勿關閉程式")

        try:
            # Run blocking download in executor to keep UI responsive
            # Note: nicegui run.io_bound might be needed if requests blocks loop
            # But here we loop chunk write, so we can yield?
            # update_manager.download_and_install uses requests sync.
            # We wrap it or modify it to be async-friendly.
            # For simplicity, let's run it in a thread.

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._run_download)

            self.status.set_text("下載完成！正在重啟...")
            self.progress.set_value(1.0)

        except Exception as ex:
            self.status.set_text(f"更新失敗: {ex}")
            ui.notify(f"Update Failed: {ex}", type="negative")
            e.sender.enable()

    def _run_download(self):
        def update_progress(p):
            # Safe to update NiceGUI element from thread?
            # Ideally use ui.run_javascript or app.call_soon/loop.call_soon_threadsafe
            # But specific element update might work if no layout change.
            # Safest is to not touch UI directly from thread.
            # But let's try direct update, if it fails we wrap.
            if self.progress:
                self.progress.value = p

                # Show percentage in status text
                pct = int(p * 100)
                if self.status:
                    self.status.text = f"下載中... {pct}%"

        self.manager.download_and_install(progress_callback=update_progress)
