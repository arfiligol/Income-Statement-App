from __future__ import annotations

from typing import Any, Optional

import tkinter as tk


class PlaceholderEntry(tk.Entry):
    def __init__(self, master: Optional[tk.Misc] = None, placeholder: str = "Enter text here", color: str = "grey"):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color: str = self["fg"]

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self) -> None:
        self.insert(0, self.placeholder)
        self["fg"] = self.placeholder_color

    def foc_in(self, _event: tk.Event[Any]) -> None:
        if self["fg"] == self.placeholder_color:
            self.delete("0", "end")
            self["fg"] = self.default_fg_color

    def foc_out(self, _event: tk.Event[Any]) -> None:
        if not self.get():
            self.put_placeholder()
