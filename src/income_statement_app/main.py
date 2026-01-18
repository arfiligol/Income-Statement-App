import os
import sys
from pathlib import Path

# Ensure 'app' (and root) is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import ui

from income_statement_app.ui.routers.home import register_routes


def run() -> None:
    # Handle missing streams in frozen/windowed mode to prevent Uvicorn crashes
    # Redirect to a log file for debugging
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

            # Simple file writer that satisfies isatty()
            class LogWriter:
                def __init__(self, path):
                    self.file = open(path, "a", encoding="utf-8")
                    self.file.write(f"\n--- Startup at {os.getcwd()} ---\n")

                def write(self, text):
                    self.file.write(text)
                    self.file.flush()

                def flush(self):
                    self.file.flush()

                def isatty(self):
                    return False

            writer = LogWriter(log_file)
            if sys.stdout is None:
                sys.stdout = writer
            if sys.stderr is None:
                sys.stderr = writer

        except Exception:
            # Fallback if logging fails
            class NullWriter:
                def write(self, text):
                    pass

                def flush(self):
                    pass

                def isatty(self):
                    return False

            if sys.stdout is None:
                sys.stdout = NullWriter()
            if sys.stderr is None:
                sys.stderr = NullWriter()

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
