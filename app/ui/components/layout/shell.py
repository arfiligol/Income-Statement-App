import time
from pathlib import Path
from typing import Callable

from nicegui import run, ui

from app.services.update_manager import UpdateManager
from app.ui.components.dialogs.update_dialog import UpdateDialog
from app.ui.state.app_store import AppStore

_styles_loaded = False
_last_check_time = 0.0
_cached_update_info = (False, None, None)


def app_shell(content_builder: Callable):
    """
    Main App Shell Layout.
    Provides Header, Sidebar, and Content Area.
    """
    store = AppStore()

    global _styles_loaded
    if not _styles_loaded:
        styles_dir = Path(__file__).resolve().parents[2] / "styles"
        ui.add_css(str(styles_dir / "theme.css"), shared=True)
        ui.add_css(str(styles_dir / "components.css"), shared=True)
        _styles_loaded = True

    def apply_dark_mode(is_dark: bool) -> None:
        dark.set_value(is_dark)
        ui.run_javascript(
            f"document.body.classList.toggle('dark', {str(is_dark).lower()});"
        )

    async def check_updates():
        global _last_check_time, _cached_update_info

        # Cache for 1 hour to prevent API rate limits
        if time.time() - _last_check_time < 3600:
            exists, ver, url = _cached_update_info
        else:
            mgr = UpdateManager()
            exists, ver = await run.io_bound(mgr.check_for_update)
            url = mgr.download_url
            _last_check_time = time.time()
            _cached_update_info = (exists, ver, url)

        if exists and ver:
            update_btn.classes(remove="hidden")
            update_btn.tooltip(f"New version {ver} available")

            def start_update():
                # Re-create manager with cached URL
                m = UpdateManager()
                m.download_url = url
                UpdateDialog(m, ver).open()

            # Re-bind click to include version
            update_btn.on_click(start_update)

    # 1. Global Theme/Style setup (single source of truth)
    dark = ui.dark_mode()
    apply_dark_mode(store.state.is_dark_mode)
    ui.query("body").classes("bg-bg text-fg")
    ui.query(".q-layout").style("width: 100%; max-width: none;")
    ui.query(".q-page-container").style("width: 100%; max-width: none;")
    ui.query(".q-page").style("width: 100%; max-width: none;")

    # 2. Header
    with ui.header().classes(
        "bg-surface text-fg h-16 px-6 items-center shadow-sm border-b border-border"
    ):
        ui.button(icon="menu", on_click=lambda: left_drawer.toggle()).props(
            "flat round dense"
        ).classes("text-muted")
        ui.label("Income Statement App").classes("text-lg font-bold ml-4")

        ui.space()

        # Update Button
        update_btn = (
            ui.button("Upgrade!", icon="cloud_download")
            .props("unelevated color=deep-orange size=sm")
            .classes("mr-4 hidden font-bold")
        )

        # Use a background task for update check that doesn't block shutdown
        # Triggered once after startup. Using timer is fine if we handle exceptions or use run.io_bound correctly.
        # But 'run.io_bound' keeps a thread pool.
        # Let's try explicitly handling it or just re-enable it now that Ctrl+C is cleaner?
        # User said "Window close -> delayed but clean" BUT "Ctrl+C -> error".
        # We fixed Ctrl+C error.
        # The delay might be unavoidable if requests is waiting.
        # Let's uncomment it but maybe increase delay to ensure UI loads first?
        ui.timer(2.0, check_updates, once=True)

        # Dark Mode Toggle
        # Note: ui.dark_mode toggles Quasar's body--dark. We also need Tailwind's 'dark' class.
        def toggle_dark_mode():
            store.toggle_dark_mode()
            apply_dark_mode(store.state.is_dark_mode)

        ui.button(icon="dark_mode", on_click=toggle_dark_mode).props(
            "flat round dense"
        ).classes("text-muted")

    # 3. Sidebar (Drawer)
    with ui.left_drawer(value=False).classes(
        "bg-bg border-r border-border"
    ) as left_drawer:
        with ui.column().classes("w-full gap-2 p-4"):
            ui.label("主選單").classes("text-xs font-bold text-muted mb-2")

            def nav_btn(label, icon, target):
                ui.button(
                    label, icon=icon, on_click=lambda: ui.navigate.to(target)
                ).props("flat align=left no-caps").classes(
                    "w-full justify-start app-nav-item rounded-lg"
                )

            nav_btn("資料處理 (Toolbox)", "handyman", "/")
            nav_btn("資料庫 (Database)", "storage", "/database")

            ui.space()
            from app.common.version import __version__

            ui.label(f"v{__version__}").classes(
                "text-xs text-muted font-mono opacity-50"
            )

    # 4. Main Content
    with ui.element("div").classes("q-page-container w-full p-0 bg-bg text-fg"):
        with ui.element("div").classes("q-page w-full"):
            with (
                ui.column()
                .classes("w-full max-w-none px-6 py-8 gap-6 items-stretch")
                .style("width: 100%; max-width: none;")
            ):
                content_builder()
