from __future__ import annotations

import threading
from typing import Optional

import flet as ft

from src.services.interfaces.user_interaction_provider import UserInteractionProvider

class FletInteractionProvider(UserInteractionProvider):
    """
    Implementation of UserInteractionProvider for Flet.
    Handles communication between background service threads and the main UI thread.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self._event = threading.Event()
        self._confirm_result: bool = False
        self._select_result: tuple[list[str], str] = ([], "abort")

    def confirm(self, title: str, message: str) -> bool:
        """Shows a confirmation dialog and waits for user input."""
        if threading.current_thread() is threading.main_thread():
             raise RuntimeError("Cannot call synchronous confirm() from the main thread (Deadlock risk).")
        
        self._event.clear()

        def close_dlg(e):
            self.page.dialog.open = False
            self.page.update()

        def on_yes(e):
            self._confirm_result = True
            close_dlg(e)
            self._event.set()

        def on_no(e):
            self._confirm_result = False
            close_dlg(e)
            self._event.set()

        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("是 (Yes)", on_click=on_yes),
                ft.TextButton("否 (No)", on_click=on_no),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
        
        # Block thread until user responds
        self._event.wait()
        return self._confirm_result

    def show_message(self, title: str, message: str) -> None:
        """Shows a message dialog asynchronously (does not block service)."""
        def close_dlg(e):
            self.page.dialog.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dlg)],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def select_lawyers(self, summary_text: str, row_number: int, available_codes: list[str]) -> tuple[list[str], str]:
        """Shows a lawyer selection dialog."""
        if threading.current_thread() is threading.main_thread():
             raise RuntimeError("Cannot call select_lawyers from main thread.")

        self._event.clear()
        
        # UI Components for Dialog
        selected_values = set()
        
        def on_change(e):
            if e.control.value:
                selected_values.add(e.control.data)
            else:
                selected_values.discard(e.control.data)

        checkboxes = ft.Column(
            controls=[
                ft.Checkbox(label=code, data=code, on_change=on_change)
                for code in available_codes
            ],
            height=200,
            scroll=ft.ScrollMode.AUTO,
        )
        
        def finish(action: str):
            self._select_result = (list(selected_values), action)
            self.page.dialog.open = False
            self.page.update()
            self._event.set()

        dlg = ft.AlertDialog(
            title=ft.Text(f"手動選擇律師 (Col {row_number})"),
            content=ft.Column(
                width=400,
                tight=True,
                controls=[
                    ft.Text(f"摘要內容：\n{summary_text}", weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("請勾選包含的律師代碼："),
                    checkboxes,
                ]
            ),
            actions=[
                ft.TextButton("中止 (Abort)", on_click=lambda e: finish("abort"), style=ft.ButtonStyle(color=ft.Colors.ERROR)),
                ft.TextButton("跳過單筆", on_click=lambda e: finish("skip_single")),
                ft.TextButton("跳過全部手動", on_click=lambda e: finish("skip_all")),
                ft.TextButton("確認 (Confirm)", on_click=lambda e: finish("confirm")),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            modal=True,
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
        
        self._event.wait()
        return self._select_result
