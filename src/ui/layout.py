from nicegui import ui

from src.ui.theme import apply_theme, toggle_dark_mode


def create_layout(on_nav):
    """
    Creates the persistent layout for the SPA.
    params:
        on_nav: callback function(page_name) to switch content
    returns:
        content_container: the ui element where pages should be rendered
    """
    # Global Style - Centralized in theme.py
    apply_theme()

    # Initialize Dark Mode Controller (Default to Dark)
    dark = ui.dark_mode(value=True)

    # Configure Quasar Layout to have Left Drawer span full height (LHh ...)
    # Reverting to standard 'hHh' (Header spans full width) as requested by user to avoid complexity.
    ui.context.client.layout.props('view="hHh LpR lff"')

    # Define Drawer FIRST to ensure it renders "under" or "before" if that affects z-order/slot implementation detail
    # Sidebar (Drawer)
    with (
        ui.left_drawer(value=True)
        .classes(
            "bg-white border-r border-slate-200 dark:!bg-slate-900 dark:!border-slate-800"
        )
        .props('width=280 behavior="desktop" bordered') as left_drawer
    ):
        with ui.column().classes("w-full h-full py-6 px-4 gap-1"):
            ui.label("MAIN MENU").classes(
                "text-xs font-bold text-slate-400 mb-3 tracking-wider dark:text-slate-500"
            )

            def nav_btn(text, icon, page_key):
                # Using Tailwind for hover effects and active states could be done via dynamic classes
                # For now, a clean flat style
                with (
                    ui.button(on_click=lambda: on_nav(page_key))
                    .props("flat no-caps align=left")
                    .classes(
                        "nav-btn w-full rounded-lg text-slate-600 hover:bg-slate-100 hover:text-indigo-600 transition-all duration-200 group py-2.5 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-indigo-400"
                    )
                ):
                    with ui.row().classes("items-center gap-3 w-full"):
                        # Fixed-width container for icon to ensure alignment
                        with ui.element("div").classes(
                            "w-6 h-6 flex items-center justify-center shrink-0"
                        ):
                            ui.icon(icon, size="20px").classes(
                                "text-slate-400 group-hover:text-indigo-500 transition-colors"
                            )
                        ui.label(text).classes("font-medium")

            # Unified Icon Style: Using consistent Material Icons (Filled)
            # - Toolbox: "handyman" (or "build")
            # - Database: "storage" (standard Material Icon for DB, "database" is FontAwesome)
            nav_btn("工具包 (Toolbox)", "handyman", "workflow")
            nav_btn("資料庫操作 (Database)", "storage", "database")

            ui.separator().classes("my-4 opacity-50 dark:bg-slate-700")

            # Footer
            with ui.column().classes("mt-auto pb-2 w-full items-start"):
                ui.label("Version 1.0.0").classes(
                    "text-xs text-slate-300 font-mono dark:text-slate-600"
                )

    # Header - Tailwind Styled
    # Using specific colors: slate-900 for dark professional look
    with ui.header().classes(
        "bg-slate-900 text-white items-center h-16 px-6 border-b border-slate-800 shadow-sm dark:bg-slate-950 dark:border-slate-900"
    ) as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
            "flat round dense color=white"
        ).classes("opacity-80 hover:opacity-100 transition-opacity")

        with ui.row().classes("items-center gap-2 ml-4"):
            ui.icon("account_balance_wallet", size="28px").classes("text-indigo-400")
            ui.label("Income Statement App").classes(
                "text-xl font-bold tracking-tight text-white"
            )

        ui.space()

        # Dark Mode Toggle
        # Use centralized toggle function from theme.py
        # Instantiate ui.dark_mode() once to ensure 'dark' object exists contextually if needed by NiceGUI internals,
        # though toggle_dark_mode in theme.py manages the toggle action.

        with (
            ui.button(on_click=lambda: toggle_dark_mode(dark))
            .props("flat round dense")
            .classes("text-slate-400 hover:text-white transition-colors")
        ):
            ui.icon("dark_mode")

    # Content Area
    # User requested full-width expansion when sidebar is toggled (removed max-w-7xl mx-auto)
    content = ui.column().classes(
        "w-full p-8 items-start gap-8 bg-slate-50 min-h-screen dark:bg-slate-900"
    )
    return content
