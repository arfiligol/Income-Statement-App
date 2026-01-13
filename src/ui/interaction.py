
from typing import Optional
from nicegui import ui
import asyncio
from src.services.interfaces.user_interaction_provider import UserInteractionProvider

class NiceGUIInteractionProvider(UserInteractionProvider):
    def __init__(self):
        pass

    async def confirm(self, title: str, message: str) -> bool:
        """Shows a confirmation dialog."""
        # NiceGUI doesn't have a blocking confirm, we wrap a dialog
        result = asyncio.get_running_loop().create_future()
        
        with ui.dialog() as dialog, ui.card():
            ui.label(title).classes('text-lg font-bold')
            ui.label(message)
            with ui.row().classes('w-full justify-end'):
                ui.button('No', on_click=lambda: result.set_result(False)).props('flat color=red')
                ui.button('Yes', on_click=lambda: result.set_result(True)).props('flat color=green')
        
        dialog.open()
        return await result

    def show_message(self, title: str, message: str) -> None:
        """Shows a notification or alert."""
        ui.notify(f"{title}: {message}", type='info', close_button=True)

    async def select_lawyers(self, summary_text: str, row_number: int, available_codes: list[str]) -> tuple[list[str], str]:
        """Shows a lawyer selection dialog."""
        result = asyncio.get_running_loop().create_future()
        
        selected_values = set()

        def toggle(code, value):
            if value:
                selected_values.add(code)
            else:
                selected_values.discard(code)

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label(f"手動選擇律師 (Row {row_number})").classes('text-lg font-bold')
            ui.label(f"摘要: {summary_text}").classes('text-sm text-gray-600 mb-2')
            
            with ui.scroll_area().classes('h-48 border rounded p-2'):
                for code in available_codes:
                    ui.checkbox(code, on_change=lambda e, c=code: toggle(c, e.value))
            
            with ui.row().classes('w-full justify-between mt-4'):
                 # Actions
                def finish(action):
                    dialog.close()
                    result.set_result((list(selected_values), action))

                ui.button('Abort', on_click=lambda: finish('abort')).props('flat color=red')
                ui.button('Skip', on_click=lambda: finish('skip_single')).props('flat color=orange')
                ui.button('Skip All', on_click=lambda: finish('skip_all')).props('flat color=orange')
                ui.button('Confirm', on_click=lambda: finish('confirm')).props('flat color=green')

        dialog.open()
        return await result
