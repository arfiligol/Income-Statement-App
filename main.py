import os
import sys

# Ensure 'app' (and root) is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import ui

from app.ui.routers.home import register_routes


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
    )


if __name__ in {"__main__", "__mp_main__"}:
    try:
        run()
    except KeyboardInterrupt:
        pass
