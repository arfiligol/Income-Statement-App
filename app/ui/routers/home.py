from nicegui import ui

from app.application.use_cases.import_excel import ImportExcelUseCase
from app.infrastructure.repositories.excel_pandas_repo import ExcelPandasRepository
from app.ui.pages.statement_editor_page import StatementEditorPage
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

        # 2. Application
        import_use_case = ImportExcelUseCase(excel_repo)

        # 3. UI (ViewModel + Page)
        vm = StatementViewModel(import_use_case)
        page = StatementEditorPage(vm)

        # 4. Render
        page.render()
