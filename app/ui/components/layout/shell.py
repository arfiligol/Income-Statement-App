from typing import Callable

from nicegui import ui

from app.ui.state.app_store import AppStore


def app_shell(content_builder: Callable):
    """
    Main App Shell Layout.
    Provides Header, Sidebar, and Content Area.
    """
    store = AppStore()

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
        "bg-white dark:bg-slate-900 text-slate-900 dark:text-white h-16 px-6 items-center shadow-sm border-b border-slate-200 dark:border-slate-800"
    ):
        ui.button(icon="menu", on_click=lambda: left_drawer.toggle()).props(
            "flat round dense"
        ).classes("text-slate-600 dark:text-slate-300")
        ui.label("Income Statement App").classes("text-lg font-bold ml-4")

        ui.space()

        # Dark Mode Toggle
        # Note: ui.dark_mode toggles Quasar's body--dark. We also need Tailwind's 'dark' class.
        def toggle_dark_mode():
            store.toggle_dark_mode()
            apply_dark_mode(store.state.is_dark_mode)

        ui.button(icon="dark_mode", on_click=toggle_dark_mode).props(
            "flat round dense"
        ).classes("text-slate-600 dark:text-slate-300")

    # 3. Sidebar (Drawer)
    with ui.left_drawer(value=True).classes(
        "bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800"
    ) as left_drawer:
        with ui.column().classes("w-full gap-2 p-4"):
            ui.label("主選單").classes("text-xs font-bold text-slate-400 mb-2")

            def nav_btn(label, icon, target):
                ui.button(
                    label, icon=icon, on_click=lambda: ui.navigate.to(target)
                ).props("flat align=left no-caps").classes(
                    "w-full justify-start text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
                )

            nav_btn("資料處理 (Toolbox)", "handyman", "/")
            nav_btn("資料庫 (Database)", "storage", "/database")

    # 4. Main Content
    with ui.column().classes(
        "w-full p-8 bg-white dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100"
    ):
        content_builder()
