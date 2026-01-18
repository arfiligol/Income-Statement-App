import asyncio

from nicegui import ui

from income_statement_app.application.ports.gateways import UserInteractionGateway
from income_statement_app.domain.dto.auto_fill import AutoFillPrompt, AutoFillResponse


class NiceGUIInteractionGateway(UserInteractionGateway):
    """
    Implementation of UserInteractionGateway using NiceGUI Dialogs.
    """


from income_statement_app.ui.components.dialogs.lawyer_selection_dialog import LawyerSelectionDialog


class NiceGUIInteractionGateway(UserInteractionGateway):
    """
    Implementation of UserInteractionGateway using NiceGUI Dialogs.
    """

    async def select_lawyers(self, prompt: AutoFillPrompt) -> AutoFillResponse:
        dialog = LawyerSelectionDialog(
            row_number=prompt.row_number,
            summary=prompt.summary,
            available_codes=prompt.available_codes,
        )
        return await dialog.await_result()
