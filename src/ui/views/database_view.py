import flet as ft
from src.ui.state.database_state import DatabaseState

class DatabaseView(ft.Column):
    def __init__(self, state: DatabaseState):
        super().__init__(expand=True, spacing=20)
        self.state = state
        self.state.bind(self.update_ui)
        
        # UI Controls
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("來源代碼 (Source)", weight=ft.FontWeight.W_700, size=15)),
                ft.DataColumn(ft.Text("目標代碼 (Targets)", weight=ft.FontWeight.W_700, size=15)),
                ft.DataColumn(ft.Text("操作", weight=ft.FontWeight.W_700, size=15)),
            ],
            column_spacing=60,
            expand=True,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=16,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )
        self.edit_dialog = None
        self.source_field = ft.TextField(
            label="來源代碼", 
            border_radius=12, 
            prefix_icon=ft.Icons.STORAGE,
            label_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
        )
        self.target_field = ft.TextField(
            label="目標代碼 (請用逗號分隔)", 
            border_radius=12, 
            prefix_icon=ft.Icons.GROUP_ADD_OUTLINED, 
            helper="例如: L001, L002",
            label_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
        )
        
        # Header Area - Compact
        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("律師代碼管理", size=22, weight=ft.FontWeight.W_700, color=ft.Colors.ON_SURFACE),
                        ft.Text("設定映射，強化自動辨識能力。", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], expand=True),
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.REFRESH_ROUNDED, tooltip="重新整理", on_click=lambda e: self.state.load_data()),
                        ft.Button(
                            "新增群組", 
                            icon=ft.Icons.ADD_ROUNDED, 
                            on_click=lambda e: self.open_edit_dialog(),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=16,
                            )
                        ),
                    ], spacing=8)
                ], alignment=ft.MainAxisAlignment.START),
                padding=ft.Padding(0, 0, 0, 20),
            ),
            
            # Data Table Area - Compact
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=self.table,
                        padding=16,
                    )
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=16,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            )
        ]
        self.padding = ft.Padding.all(0)


    def did_mount(self):
        self.state.load_data()

    def update_ui(self):
        rows = []
        for alias in self.state.aliases:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(alias.source_code, weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(alias.target_codes_str)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_ROUNDED, 
                                        icon_color=ft.Colors.BLUE_600,
                                        tooltip="編輯區塊",
                                        on_click=lambda e, s=alias.source_code, t=alias.target_codes_str: self.open_edit_dialog(s, t)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED, 
                                        icon_color=ft.Colors.RED_400,
                                        tooltip="刪除群組",
                                        on_click=lambda e, s=alias.source_code: self.state.delete_alias(s)
                                    ),
                                ],
                                spacing=0
                            )
                        ),
                    ]
                )
            )
        self.table.rows = rows
        self.update()

    def open_edit_dialog(self, source="", targets=""):
        self.source_field.value = source
        self.source_field.read_only = bool(source)
        self.source_field.border_color = ft.Colors.BLUE_GREY_100 if source else None
        self.target_field.value = targets
        
        if not self.edit_dialog:
             self.edit_dialog = ft.AlertDialog(
                title=ft.Row([ft.Icon(ft.Icons.EDIT_DOCUMENT), ft.Text("編輯代碼群組")], spacing=10),
                content=ft.Container(
                    content=ft.Column([
                        self.source_field,
                        self.target_field
                    ], spacing=15, tight=True),
                    width=400,
                    padding=ft.Padding.symmetric(vertical=15)
                ),
                actions=[
                    ft.TextButton("取消", on_click=self.close_edit_dialog),
                    ft.Button("儲存變更", color=ft.Colors.WHITE, bgcolor=ft.Colors.INDIGO, on_click=self.save_alias, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=20),
            )
        
        self.page.dialog = self.edit_dialog
        self.edit_dialog.open = True
        self.page.update()

    def close_edit_dialog(self, e=None):
        self.edit_dialog.open = False
        self.page.update()

    def save_alias(self, e):
        if not self.source_field.value or not self.target_field.value:
            return
        self.state.add_alias(self.source_field.value, self.target_field.value)
        self.close_edit_dialog()

