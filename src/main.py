import os
import sys
from pathlib import Path

# Ensure 'app' (and root) is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import ui

from ui.routers.home import register_routes


def run() -> None:
    # Fix for packaged GUI apps where stdout/stderr may be None (causes Uvicorn crash)
    # Briefcase does NOT set sys.frozen, so we check directly for None streams
    if sys.stdout is None or sys.stderr is None:
        try:
            app_name = "Income-Statement-App"
            if sys.platform == "win32":
                log_dir = Path(os.environ["LOCALAPPDATA"]) / app_name / "logs"
            elif sys.platform == "darwin":
                log_dir = (
                    Path.home() / "Library" / "Application Support" / app_name / "logs"
                )
            else:
                log_dir = Path.home() / ".local" / "share" / app_name / "logs"

            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "startup.log"

            # Configure basic logging to file
            import logging

            # Clear existing handlers to ensure file logging works
            logging.getLogger().handlers = []
            logging.basicConfig(
                level=logging.DEBUG,
                filename=log_file,
                filemode="w",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            logging.info(f"Startup at {os.getcwd()}")
            logging.info(f"Python: {sys.version}")

            # Redirect stdout/stderr to this file
            class FileLogWriter:
                def __init__(self, logger_func):
                    self.logger_func = logger_func

                def write(self, text):
                    if text.strip():
                        self.logger_func(text.strip())

                def flush(self):
                    pass

                def isatty(self):
                    return False

            sys.stdout = FileLogWriter(logging.info)
            sys.stderr = FileLogWriter(logging.error)

        except Exception:
            # Fallback if logging fails
            pass

    # 1. Register Routes (and setup dependency graph)
    register_routes()

    # Ensure clean exit on shutdown to prevent hanging processes (e.g. background threads)
    from nicegui import app

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
