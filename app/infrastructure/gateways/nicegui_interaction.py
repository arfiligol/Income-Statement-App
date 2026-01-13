import asyncio

from nicegui import ui

from app.application.ports.gateways import UserInteractionGateway
from app.domain.dto.auto_fill import AutoFillPrompt, AutoFillResponse


class NiceGUIInteractionGateway(UserInteractionGateway):
    """
    Implementation of UserInteractionGateway using NiceGUI Dialogs.
    """

    async def select_lawyers(self, prompt: AutoFillPrompt) -> AutoFillResponse:
        # Create a Future to await user input
        future = asyncio.get_event_loop().create_future()

        with ui.dialog() as dialog, ui.card():
            ui.label(f"Row {prompt.row_number}: Lawyer Selection").classes(
                "text-lg font-bold"
            )
            ui.label(f"Summary: {prompt.summary}").classes("text-slate-600 mb-2")

            # Selection Interface
            selected = []

            def update_selection():
                # This is a bit tricky with dynamic UI generation in a dialog
                # Simplified: Using a multi-select
                pass

            # NiceGUI Select (or Toggle)
            select = ui.select(
                options=prompt.available_codes,
                multiple=True,
                label="Select Lawyers",
                with_input=True,
            ).classes("w-64")

            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("Skip", on_click=lambda: dialog.submit("skip")).props(
                    "flat color=grey"
                )
                ui.button("Submit", on_click=lambda: dialog.submit("submit"))

        dialog.open()
        result_action = await dialog

        # Parse result
        if result_action == "submit":
            return AutoFillResponse(selected_codes=select.value or [], action="submit")
        else:
            return AutoFillResponse(selected_codes=[], action="skip")
