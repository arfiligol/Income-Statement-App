import os
import sys

# Ensure 'app' (and root) is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import ui

from income_statement_app.ui.routers.home import register_routes


def run() -> None:
    # 1. Register Routes (and setup dependency graph)
    register_routes()

    # Ensure clean exit on shutdown to prevent hanging processes (e.g. background threads)
    from nicegui import app
    import os

    app.on_shutdown(lambda: os._exit(0))

    # 2. Run App
    # Common screen size for desktop apps
    ui.run(
        title="Income Statement App (Clean Arch)",
        native=True,
        window_size=(1200, 800),
        reload=False,
        favicon=resource_path("static/mom_accounting.ico"),
    )


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


if __name__ in {"__main__", "__mp_main__"}:
    try:
        run()
    except KeyboardInterrupt:
        pass
