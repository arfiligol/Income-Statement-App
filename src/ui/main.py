import flet as ft

from src.data.repositories.alias_repository import AliasRepository
from src.data.repositories.excel_repository import ExcelRepository
from src.data.repositories.lawyer_repository import LawyerRepository
from src.services.excel_report_service import ExcelReportService
from src.services.workflow_service import WorkflowService
from src.ui.interaction import FletInteractionProvider
from src.ui.state.database_state import DatabaseState
from src.ui.state.workflow_state import WorkflowState
from src.ui.views.database_view import DatabaseView
from src.ui.views.workflow_view import WorkflowView

def main(page: ft.Page):
    # Page basic settings
    page.title = "Income Statement App"
    # --- Dynamic Resolution Handling (Mac specific) ---
    def get_screen_resolution():
        import subprocess
        try:
            cmd = "system_profiler SPDisplaysDataType | grep Resolution"
            output = subprocess.check_output(cmd, shell=True).decode()
            # Expecting something like "Resolution: 3840 x 2160"
            parts = output.split(":")[-1].strip().split(" ")
            w = int(parts[0])
            h = int(parts[2])
            return w, h
        except:
            return 1920, 1080 # Fallback default

    screen_w, screen_h = get_screen_resolution()
    
    # Target 80% of the screen but handle Retina/Scaling factor
    # Usually UI units on Mac are 1/2 of physical pixels for 4K "Looks like 1080p"
    # But if we want 80% of physical space, and Flet uses points, we need to be careful.
    # We will aim for 80% of physical if physical looks like points, or 80% of perceived.
    # Let's assume the perceived work area is roughly half if w > 3000
    if screen_w > 3000:
        actual_w = (screen_w / 2) * 0.8
        actual_h = (screen_h / 2) * 0.8
    else:
        actual_w = screen_w * 0.8
        actual_h = screen_h * 0.8

    # Constraints for minimum usability
    page.window.width = max(1000, int(actual_w))
    page.window.height = max(700, int(actual_h))
    page.window.min_width = 1000
    page.window.min_height = 700 # Increased for 4K users
    
    page.spacing = 0
    page.padding = 0

    # Dependency Injection
    interaction = FletInteractionProvider(page)
    alias_repo = AliasRepository()
    lawyer_repo = LawyerRepository()
    excel_repo = ExcelRepository()
    report_service = ExcelReportService(interaction)
    
    workflow_service = WorkflowService(
        interaction, alias_repo, lawyer_repo, excel_repo, report_service
    )
    
    # State & ViewModels
    wf_state = WorkflowState(workflow_service)
    db_state = DatabaseState(alias_repo)
    
    # Views
    wf_view = WorkflowView(wf_state)
    db_view = DatabaseView(db_state)

    # State variables
    sidebar_visible = True

    # Theme Switching Logic
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_icon.icon = ft.Icons.LIGHT_MODE_ROUNDED
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_icon.icon = ft.Icons.DARK_MODE_ROUNDED
        page.update()

    theme_icon = ft.IconButton(
        icon=ft.Icons.DARK_MODE_ROUNDED,
        on_click=toggle_theme,
        tooltip="切換亮/暗模式"
    )

    # Sidebar Toggle Logic
    def toggle_sidebar(e):
        nonlocal sidebar_visible
        sidebar_visible = not sidebar_visible
        sidebar.width = 260 if sidebar_visible else 0
        sidebar.update()

    # Navbar (Top Bar) - Slimmed down
    navbar = ft.Container(
        content=ft.Row([
            ft.IconButton(ft.Icons.MENU_ROUNDED, on_click=toggle_sidebar, tooltip="選單"),
            ft.Text("Income Statement App", size=20, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
            ft.Row([], expand=True), # Spacer
            theme_icon,
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding(left=20, right=20, top=8, bottom=8),
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
    )

    # Sidebar Items
    def create_nav_item(text, icon, index):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(text, size=15, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
            ], spacing=12),
            padding=ft.Padding(left=20, right=20, top=12, bottom=12),
            on_click=lambda e: navigate_to(index),
            border_radius=10,
            ink=True,
        )

    sidebar_items = [
        create_nav_item("工具包", ft.Icons.WORK_OUTLINED, 0),
        create_nav_item("資料庫操作", ft.Icons.STORAGE_ROUNDED, 1),
        create_nav_item("更新測試頁面", ft.Icons.UPGRADE_ROUNDED, 2),
    ]

    sidebar = ft.Container(
        content=ft.Column([
            ft.Container(height=24), # Top spacing
            *sidebar_items,
        ], spacing=4),
        width=260,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        padding=ft.Padding(8, 0, 8, 0),
        animate=ft.Animation(400, ft.AnimationCurve.DECELERATE),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    # Content Area - Optimized Padding
    content_area = ft.Container(
        content=wf_view, 
        expand=True,
        padding=ft.Padding(20, 20, 20, 20), # Reduced from 24 to save height
    )

    def navigate_to(index):
        if index == 0:
            content_area.content = wf_view
        elif index == 1:
            content_area.content = db_view
        elif index == 2:
            content_area.content = ft.Container(
                content=ft.Column([
                    ft.Text("更新測試頁面", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("此頁面暫時計劃用於顯示版本更新與測試資訊。", size=16),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True
            )
        page.update()

    page.on_ripple_end = lambda e: None # Visual polish

    page.services.append(wf_view.file_picker)
    
    # Final assembly and proportional adjustment
    page.add(
        ft.Row(
            [
                sidebar,
                ft.Column([
                    navbar,
                    content_area,
                ], expand=True, spacing=0),
            ],
            expand=True,
            spacing=0
        )
    )

    # Attempt to resize to 80% of the sensed screen/window space
    # In Flet, page.width/height becomes available after initialization or first page.add
    if page.width and page.height:
        # If it's the first run, let's try to set it to a comfortable 80%
        # but avoid shrinking if already reasonably sized.
        pass

    page.update()
    print("Flet UI mounted", flush=True)


