from __future__ import annotations

from typing import List, Optional

import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, LEFT, RIGHT, TOP


class LawyerSelectionDialog(ttk.Toplevel):
    def __init__(self, master: tk.Misc, summary: str, row_number: int, available_codes: List[str]) -> None:
        super().__init__(master)
        self.title("選擇律師代碼")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._available_codes = sorted(available_codes)
        self._selected_codes: Optional[List[str]] = None
        self.skip_remaining = False

        container = ttk.Frame(self, padding=15)
        container.pack(fill=BOTH, expand=True)

        ttk.Label(
            container,
            text=f"列號：{row_number}",
            bootstyle="warning",
        ).pack(side=TOP, anchor="w")

        ttk.Label(
            container,
            text="摘要內容：",
            bootstyle="secondary",
        ).pack(side=TOP, anchor="w")

        summary_box = ttk.Text(container, height=4, width=60, wrap="word")
        summary_box.insert("1.0", summary)
        summary_box.configure(state="disabled")
        summary_box.pack(fill=BOTH, expand=True, pady=(0, 10))

        ttk.Label(container, text="既有律師代碼：", bootstyle="secondary").pack(side=TOP, anchor="w")

        listbox_frame = ttk.Frame(container)
        listbox_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        self.listbox = tk.Listbox(
            listbox_frame,
            selectmode=tk.MULTIPLE,
            height=10,
            exportselection=False,
        )
        for code in self._available_codes:
            self.listbox.insert(tk.END, code)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame, command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        ttk.Label(container, text="新增律師代碼（以空白分隔）：", bootstyle="secondary").pack(side=TOP, anchor="w")
        self.new_code_entry = ttk.Entry(container)
        self.new_code_entry.pack(fill=BOTH, pady=(0, 10))

        button_frame = ttk.Frame(container)
        button_frame.pack(fill=BOTH, expand=True)

        confirm_btn = ttk.Button(button_frame, text="確認", bootstyle="success", command=self._on_confirm)
        confirm_btn.pack(side=RIGHT, padx=5)

        cancel_btn = ttk.Button(button_frame, text="取消", bootstyle="secondary", command=self._on_cancel)
        cancel_btn.pack(side=RIGHT, padx=5)

        skip_btn = ttk.Button(button_frame, text="跳過後續列", bootstyle="warning", command=self._on_skip_remaining)
        skip_btn.pack(side=LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def show(self) -> Optional[List[str]]:
        self.wait_window()
        return self._selected_codes

    def _on_confirm(self) -> None:
        selected_indices = self.listbox.curselection()
        selected_codes = [self._available_codes[index] for index in selected_indices]

        new_code_text = self.new_code_entry.get().strip()
        if new_code_text:
            new_codes = [code for code in new_code_text.split(" ") if code]
            selected_codes.extend(new_codes)

        # Remove duplicates while preserving order
        seen = set()
        ordered_codes: List[str] = []
        for code in selected_codes:
            normalized = code.strip()
            if not normalized:
                continue
            if normalized not in seen:
                seen.add(normalized)
                ordered_codes.append(normalized)

        if not ordered_codes:
            messagebox.showinfo("提醒", "請選擇或輸入至少一個律師代碼。", parent=self)
            return

        self._selected_codes = ordered_codes
        self.destroy()

    def _on_cancel(self) -> None:
        self._selected_codes = None
        self.destroy()

    def _on_skip_remaining(self) -> None:
        self.skip_remaining = True
        self._selected_codes = []
        self.destroy()
