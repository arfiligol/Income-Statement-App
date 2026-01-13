from nicegui import ui

from src.data.repositories.alias_repository import AliasRepository
from src.data.repositories.excel_repository import ExcelRepository
from src.data.repositories.lawyer_repository import LawyerRepository
from src.services.excel_report_service import ExcelReportService
from src.services.workflow_service import WorkflowService
from src.ui.interaction import NiceGUIInteractionProvider
from src.ui.layout import create_layout
from src.ui.views.database_view import DatabasePage
from src.ui.views.workflow_view import WorkflowPage

# Dependency Injection Setup
interaction = NiceGUIInteractionProvider()
alias_repo = AliasRepository()
lawyer_repo = LawyerRepository()
excel_repo = ExcelRepository()
report_service = ExcelReportService(interaction)
workflow_service = WorkflowService(
    interaction, alias_repo, lawyer_repo, excel_repo, report_service
)


# SPA Router
@ui.page("/")
def index():
    # Helper to calculate resolution
    def get_screen_resolution():
        # ... existing logic or skip ...
        pass

    # Layout Setup
    content_container = None

    def navigate(page_key):
        nonlocal content_container
        content_container.clear()

        with content_container:
            if page_key == "workflow":
                page = WorkflowPage(workflow_service)
                page.render_content()  # Render directly into container
            elif page_key == "database":
                page = DatabasePage(lawyer_repo, alias_repo)
                page.render_content()

    # Create Layout once
    content_container = create_layout(on_nav=navigate)

    # Initial Page
    navigate("workflow")


def get_screen_resolution():
    import subprocess

    try:
        cmd = "system_profiler SPDisplaysDataType | grep Resolution"
        output = subprocess.check_output(cmd, shell=True).decode()
        line = output.strip().split("\n")[0]
        parts = line.split(":")[-1].strip().split(" ")
        w = int(parts[0])
        h = int(parts[2])
        return w, h
    except Exception:
        return 1920, 1080


def run():
    screen_w, screen_h = get_screen_resolution()
    target_w = 1280
    target_h = 720
    if screen_w > 1920:
        target_w = 1600
        target_h = 900
    elif screen_w < 1280:
        target_w = 1000
        target_h = 600

    ui.run(
        title="Income Statement App",
        native=True,
        reload=True,
    )


if __name__ in {"__main__", "__mp_main__"}:
    run()
