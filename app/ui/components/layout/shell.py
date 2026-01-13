from pathlib import Path
from typing import Callable

from nicegui import ui

from app.ui.state.app_store import AppStore

_styles_loaded = False


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

    # 1. Global Theme/Style setup (single source of truth)
    dark = ui.dark_mode()
    apply_dark_mode(store.state.is_dark_mode)

    # 2. Header
    with ui.header().classes(
        "bg-surface text-fg h-16 px-6 items-center shadow-sm border-b border-border"
    ):
        ui.button(icon="menu", on_click=lambda: left_drawer.toggle()).props(
            "flat round dense"
        ).classes("text-muted")
        ui.label("Income Statement App").classes("text-lg font-bold ml-4")

        ui.space()

        # Dark Mode Toggle
        # Note: ui.dark_mode toggles Quasar's body--dark. We also need Tailwind's 'dark' class.
        def toggle_dark_mode():
            store.toggle_dark_mode()
            apply_dark_mode(store.state.is_dark_mode)

        ui.button(icon="dark_mode", on_click=toggle_dark_mode).props(
            "flat round dense"
        ).classes("text-muted")

    # 3. Sidebar (Drawer)
    with ui.left_drawer(value=True).classes(
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

    # 4. Main Content
    with ui.column().classes(
        "w-full p-8 bg-bg min-h-screen text-fg"
    ):
        content_builder()
