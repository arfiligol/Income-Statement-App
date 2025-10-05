from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class RestartHandler(FileSystemEventHandler):
    def __init__(self, command: list[str]) -> None:
        super().__init__()
        self.command = command
        self.process: subprocess.Popen | None = None

    def on_any_event(self, event):
        if event.is_directory:
            return
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen(self.command)


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-restart PySide app on changes")
    parser.add_argument("path", nargs="?", default=".", help="Path to watch")
    parser.add_argument("--cmd", nargs=argparse.REMAINDER, default=[sys.executable, "pyside_main.py"])
    args = parser.parse_args()

    handler = RestartHandler(args.cmd)
    observer = Observer()
    observer.schedule(handler, args.path, recursive=True)
    observer.start()

    try:
        handler.process = subprocess.Popen(args.cmd)
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.stop()
        observer.join()
        if handler.process and handler.process.poll() is None:
            handler.process.terminate()


if __name__ == "__main__":
    main()
