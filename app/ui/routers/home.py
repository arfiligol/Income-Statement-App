from nicegui import ui

from app.application.use_cases.auto_fill import AutoFillUseCase
from app.application.use_cases.import_excel import ImportExcelUseCase
from app.application.use_cases.separate_ledger import SeparateLedgerUseCase
from app.infrastructure.gateways.excel_report_gateway import ExcelReportGateway
from app.infrastructure.gateways.nicegui_interaction import NiceGUIInteractionGateway
from app.infrastructure.repositories.excel_pandas_repo import ExcelPandasRepository
from app.infrastructure.repositories.sqla_alias_repo import SQLAAliasRepository
from app.infrastructure.repositories.sqla_lawyer_repo import SQLALawyerRepository
from app.ui.pages.database_page import DatabasePage
from app.ui.pages.statement_editor_page import StatementEditorPage
from app.ui.viewmodels.database_vm import DatabaseViewModel
from app.ui.viewmodels.statement_vm import StatementViewModel


def register_routes():
    """
    Registers the routes for the application.
    Acts as the Composition Root for the Page Graph.
    """

    @ui.page("/")
    def home_page():
        # 1. Infrastructure
        excel_repo = ExcelPandasRepository()
        lawyer_repo = SQLALawyerRepository()
        alias_repo = SQLAAliasRepository()
        interaction_gw = NiceGUIInteractionGateway()
        report_gw = ExcelReportGateway()

        # 2. Application
        import_use_case = ImportExcelUseCase(excel_repo)
        auto_fill_use_case = AutoFillUseCase(
            excel_repo, lawyer_repo, alias_repo, interaction_gw
        )
        sep_ledger_use_case = SeparateLedgerUseCase(excel_repo, lawyer_repo, report_gw)

        # 3. UI (ViewModel + Page)
        vm = StatementViewModel(
            import_use_case, auto_fill_use_case, sep_ledger_use_case
        )
        page = StatementEditorPage(vm)

        # 4. Render
        page.render()

    @ui.page("/database")
    def database_page():
        # 1. Infrastructure
        lawyer_repo = SQLALawyerRepository()
        alias_repo = SQLAAliasRepository()

        # 2. UI
        vm = DatabaseViewModel(lawyer_repo, alias_repo)
        page = DatabasePage(vm)

        page.render()
