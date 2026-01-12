from __future__ import annotations

import argparse
import subprocess
import sys
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

if TYPE_CHECKING:
    from watchdog.events import FileSystemEvent


class RestartHandler(FileSystemEventHandler):
    def __init__(self, command: list[str]) -> None:
        super().__init__()
        self.command: list[str] = command
        self.process: subprocess.Popen[bytes] | None = None

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self.process and self.process.poll() is None:
            self.process.terminate()
            _ = self.process.wait()
        self.process = subprocess.Popen(self.command)


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-restart PySide app on changes")
    _ = parser.add_argument("path", nargs="?", default="src", help="Path to watch")
    _ = parser.add_argument("--cmd", nargs=argparse.REMAINDER, default=["uv", "run", "start"])
    args = parser.parse_args()

    handler = RestartHandler(args.cmd)
    observer = Observer()
    _ = observer.schedule(handler, args.path, recursive=True)
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
