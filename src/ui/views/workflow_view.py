import flet as ft
from src.ui.state.workflow_state import WorkflowState

class WorkflowView(ft.Column):
    def __init__(self, state: WorkflowState):
        super().__init__(expand=True, spacing=0) # Main padding handled by Container in main.py
        self.state = state
        self.state.bind(self.update_ui)
        
        self.file_picker = ft.FilePicker()
        
        # UI Elements
        self.file_path_text = ft.Text("尚未選擇來源檔案", italic=True, size=13, color=ft.Colors.ON_SURFACE_VARIANT)
        self.log_view = ft.ListView(expand=True, spacing=4, auto_scroll=True)
        
        # Submit Button
        self.submit_btn = ft.Button(
            "執行功能 (Submit)", 
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor={ft.ControlState.HOVERED: ft.Colors.INDIGO_700, "": ft.Colors.INDIGO_600},
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=16,
            ),
            on_click=self.handle_submit,
            disabled=True
        )

        # Custom Tab System Setup
        self.selected_tab_index = 0
        self.tab_contents = [
            self._build_auto_fill_tab(),
            self._build_separate_ledger_tab()
        ]
        self.content_switcher = ft.AnimatedSwitcher(
            self.tab_contents[0],
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=200,
            switch_in_curve=ft.AnimationCurve.EASE_OUT_QUART,
        )

        def on_tab_click(index):
            if self.selected_tab_index == index:
                return
            self.selected_tab_index = index
            self.content_switcher.content = self.tab_contents[index]
            self._refresh_tab_headers(on_tab_click)
            self.update()

        self.tab_headers_row = ft.Row(spacing=24)
        self._refresh_tab_headers(on_tab_click)

        self.controls = [
            # Header Area - Compact
            ft.Container(
                content=ft.Column([
                    ft.Text("工具包 (Toolbox)", size=22, weight=ft.FontWeight.W_700, color=ft.Colors.ON_SURFACE),
                    ft.Text("管理資料處理工作流。請選取來源檔案。", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                ], spacing=4),
                padding=ft.Padding(0, 0, 0, 16),
            ),
            
            # Step 1: File Picker Surface - Compact
            ft.Container(
                content=ft.Row([
                    ft.Button(
                        "選擇檔案", 
                        icon=ft.Icons.UPLOAD_FILE_ROUNDED,
                        on_click=self.pick_file,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=16,
                        )
                    ),
                    ft.Column([
                        ft.Text("檔案路徑", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY),
                        self.file_path_text,
                    ], spacing=2, expand=True)
                ], alignment=ft.MainAxisAlignment.START, spacing=20),
                padding=20,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=16,
                bgcolor=ft.Colors.SURFACE_CONTAINER,
            ),
            
            ft.Container(height=16), 

            # Step 2: Custom Tab headers
            self.tab_headers_row,
            ft.Divider(height=1, thickness=1, color=ft.Colors.OUTLINE_VARIANT),
            
            # Step 3: Tab Content with animation
            ft.Container(content=self.content_switcher, expand=True, width=1000),
            
            # Step 4: Global Footer Actions - Compact
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("執行日誌", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
                        ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        content=self.log_view,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        border_radius=12,
                        padding=12,
                        height=100,
                    ),
                    ft.Row([
                        ft.Text("準備就緒", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        self.submit_btn
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=10),
                padding=ft.Padding(0, 16, 0, 0),
            )
        ]
    def _refresh_tab_headers(self, on_click):
        labels = ["摘要抓律師代碼", "律師收入明細"]
        headers = []
        for i, label in enumerate(labels):
            is_selected = self.selected_tab_index == i
            headers.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            label, 
                            size=15, 
                            weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_400,
                            color=ft.Colors.PRIMARY if is_selected else ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Container(
                            height=3,
                            width=30,
                            bgcolor=ft.Colors.PRIMARY if is_selected else ft.Colors.TRANSPARENT,
                            border_radius=1.5,
                        )
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(0, 8, 0, 0),
                    on_click=lambda e, idx=i: on_click(idx),
                )
            )
        self.tab_headers_row.controls = headers

    def _build_auto_fill_tab(self):
        return ft.Container(
            padding=ft.Padding(0, 16, 0, 0),
            expand=True,
            width=1000, # Force width to prevent shrinking during animation
            content=ft.Column([
                ft.Text("摘要抓律師代碼說明", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
                ft.Text(
                    "自動掃描 Excel 「摘要」欄位並填入「備註」。",
                    size=14, color=ft.Colors.ON_SURFACE_VARIANT
                ),
                ft.Container(
                    padding=16,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                    border_radius=16,
                    width=950, # Sub-container also forced
                    content=ft.Column([
                        ft.Text("操作步驟：", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("1. 選擇來源 Excel\n2. 點擊「執行功能」\n3. 若有不確定項目將提示手動選擇", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.START)
                )
            ], spacing=16, expand=True, horizontal_alignment=ft.CrossAxisAlignment.START)
        )

    def _build_separate_ledger_tab(self):
        return ft.Container(
            padding=ft.Padding(0, 16, 0, 0),
            expand=True,
            width=1000, # Match exactly with auto_fill_tab
            content=ft.Column([
                ft.Text("律師收入明細說明", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
                ft.Text(
                    "根據備註欄位的律師代碼拆分帳務。",
                    size=14, color=ft.Colors.ON_SURFACE_VARIANT
                ),
                ft.Container(
                    padding=16,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    border_radius=16,
                    width=950, # Match exactly
                    content=ft.Column([
                        ft.Text("注意事項：", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.ON_PRIMARY_CONTAINER),
                        ft.Text("• 會在原檔新增工作表\n• 請確保檔案未被開啟", size=13, color=ft.Colors.ON_PRIMARY_CONTAINER),
                    ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.START)
                )
            ], spacing=16, expand=True, horizontal_alignment=ft.CrossAxisAlignment.START)
        )



    async def pick_file(self, e):
        files = await self.file_picker.pick_files(allowed_extensions=["xlsx", "xls"])
        if files:
            self.state.set_file(files[0].path)

    def handle_submit(self, e):
        if self.selected_tab_index == 0:
            self.state.run_auto_fill()
        else:
            self.state.run_separate_ledger()

    def update_ui(self):
        self.file_path_text.value = self.state.selected_file if self.state.selected_file else "尚未選擇來源檔案"
        self.file_path_text.color = ft.Colors.BLUE_700 if self.state.selected_file else ft.Colors.GREY_600
        self.file_path_text.weight = ft.FontWeight.BOLD if self.state.selected_file else None
        
        is_ready = bool(self.state.selected_file) and not self.state.is_processing
        self.submit_btn.disabled = not is_ready
        
        # Update progress ring if needed
        footer_column = self.controls[-1].content
        progress_ring = footer_column.controls[0].controls[1]
        progress_ring.visible = self.state.is_processing
        
        status_text = footer_column.controls[2].controls[0]
        if self.state.is_processing:
            status_text.value = "處理中..."
            status_text.color = ft.Colors.ORANGE_700
        else:
            status_text.value = "準備就緒" if self.state.selected_file else "請選擇檔案"
            status_text.color = ft.Colors.GREEN_700 if self.state.selected_file else ft.Colors.GREY_500
        
        self.log_view.controls = [
            ft.Text(
                f"[{i:02d}] {log}", 
                font_family="Consolas", 
                color=ft.Colors.GREEN_ACCENT_400 if "完成" in log else (ft.Colors.RED_ACCENT_200 if "錯誤" in log else ft.Colors.BLUE_GREY_100),
                size=12
            ) for i, log in enumerate(self.state.logs)
        ]
        
        self.update()


