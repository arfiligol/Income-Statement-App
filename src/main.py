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
            # Clear existing handlers to ensure file logging works
            logging.getLogger().handlers = []

            # Create handler that flushes immediately
            file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )

            # Root logger config
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            root_logger.addHandler(file_handler)

            logging.info(f"Startup at {os.getcwd()}")
            logging.info(f"Python: {sys.version}")
            logging.info(f"Executable: {sys.executable}")
            logging.info(f"Platform: {sys.platform}")

            # Redirect stdout/stderr to this file
            class FileLogWriter:
                def __init__(self, logger_func):
                    self.logger_func = logger_func

                def write(self, text):
                    if text and text.strip():
                        self.logger_func(text.strip())
                        # Force flush handler
                        for handler in logging.getLogger().handlers:
                            handler.flush()

                def flush(self):
                    for handler in logging.getLogger().handlers:
                        handler.flush()

                def isatty(self):
                    return False

            sys.stdout = FileLogWriter(logging.info)
            sys.stderr = FileLogWriter(logging.error)

            logging.info("Logging configured successfully. Checkpoints initialized.")

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
    # Workaround for hidden window issue on some machines:
    # Disable hardware acceleration and GPU compositing
    os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (
        "--disable-gpu --disable-d3d11"
    )

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


import multiprocessing

if __name__ in {"__main__", "__mp_main__"}:
    # Required for PyInstaller on Windows when using multiprocessing (NiceGUI native uses it)
    multiprocessing.freeze_support()
    try:
        run()
    except KeyboardInterrupt:
        pass
