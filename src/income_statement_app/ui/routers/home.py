from nicegui import ui

from income_statement_app.application.use_cases.auto_fill import AutoFillUseCase
from income_statement_app.application.use_cases.import_excel import ImportExcelUseCase
from income_statement_app.application.use_cases.separate_ledger import SeparateLedgerUseCase
from income_statement_app.infrastructure.gateways.excel_report_gateway import ExcelReportGateway
from income_statement_app.infrastructure.gateways.nicegui_interaction import NiceGUIInteractionGateway
from income_statement_app.infrastructure.repositories.excel_pandas_repo import ExcelPandasRepository
from income_statement_app.infrastructure.repositories.sqla_code_replacement_repo import (
    SQLACodeReplacementRepository,
)
from income_statement_app.infrastructure.repositories.sqla_lawyer_repo import SQLALawyerRepository
from income_statement_app.ui.components.layout.shell import app_shell
from income_statement_app.ui.pages.database_page import DatabasePage
from income_statement_app.ui.pages.statement_editor_page import StatementEditorPage
from income_statement_app.ui.viewmodels.database_vm import DatabaseViewModel
from income_statement_app.ui.viewmodels.statement_vm import StatementViewModel


def register_routes():
    """
    Registers the routes for the application.
    Acts as the Composition Root for the Page Graph.
    """

    @ui.page("/")
    def home_page():
        def render_toolbox():
            # 1. Infrastructure
            excel_repo = ExcelPandasRepository()
            lawyer_repo = SQLALawyerRepository()
            replacement_repo = SQLACodeReplacementRepository()
            interaction_gw = NiceGUIInteractionGateway()
            report_gw = ExcelReportGateway()

            # 2. Application
            import_use_case = ImportExcelUseCase(excel_repo)
            auto_fill_use_case = AutoFillUseCase(
                excel_repo, lawyer_repo, replacement_repo, interaction_gw
            )
            sep_ledger_use_case = SeparateLedgerUseCase(
                excel_repo, lawyer_repo, report_gw
            )

            # 3. UI (ViewModel + Page)
            vm = StatementViewModel(
                import_use_case, auto_fill_use_case, sep_ledger_use_case
            )
            page = StatementEditorPage(vm)

            # 4. Render content only (shell handled by root)
            page.render_content()

        def render_database():
            # 1. Infrastructure
            lawyer_repo = SQLALawyerRepository()
            replacement_repo = SQLACodeReplacementRepository()

            # 2. UI
            vm = DatabaseViewModel(lawyer_repo, replacement_repo)
            page = DatabasePage(vm)

            page.render_content()

        def render_content():
            subpages = ui.sub_pages({"/": render_toolbox, "/database": render_database})

        app_shell(render_content)
