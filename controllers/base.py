from __future__ import annotations

from typing import Optional

import tkinter as tk

class BaseController:
    def __init__(self) -> None:
        self.window: Optional[tk.Misc] = None  # 子類會建立實際視窗

    def show_window(self) -> None:
        if self.window is not None:
            self.window.deiconify() # Shows the window if it is hidden

    def hide_window(self) -> None:
        if self.window is not None:
            self.window.withdraw()

    def close_window(self) -> None:
        if self.window is not None:
            self.window.destroy()
            self.window = None
