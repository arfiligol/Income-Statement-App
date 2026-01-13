import os
import shutil

from nicegui import events, ui

from src.services.workflow_service import WorkflowService


class WorkflowPage:
    def __init__(self, service: WorkflowService):
        self.service = service
        self.selected_file = None
        self.log_container = None

    # Removed render() that wraps main_layout

    def render_content(self):  # Renamed to facilitate SPA injection
        self._content()

    def _content(self):
        # Header Section
        with ui.row().classes("w-full items-end justify-between mb-2"):
            with ui.column().classes("gap-1"):
                ui.label("工具包 (Toolbox)").classes(
                    "text-2xl font-bold text-slate-800 tracking-tight dark:text-white"
                )
                ui.label("管理資料處理工作流").classes(
                    "text-sm text-slate-500 font-medium dark:text-slate-400"
                )

        # Step 1: File Selection - Compact Design
        with ui.card().classes(
            "w-full p-4 shadow-sm border border-slate-200 rounded-xl bg-white dark:!bg-slate-800 dark:border-slate-700"
        ):
            with ui.row().classes("items-center justify-between w-full gap-4"):
                # Left: Label
                with ui.row().classes("items-center gap-3"):
                    ui.icon("upload_file", size="24px").classes(
                        "text-indigo-500 dark:text-indigo-400"
                    )
                    with ui.column().classes("gap-0"):
                        ui.label("Step 1: 選擇來源檔案").classes(
                            "text-sm font-bold text-slate-700 dark:text-slate-200"
                        )
                        self.file_label = ui.label("尚未選擇").classes(
                            "text-xs text-slate-400 dark:text-slate-500"
                        )

                # Right: Custom Upload Button & Hidden Input
                with ui.row().classes("items-center gap-4 relative"):
                    # File Status Area (Hidden initially or showing placeholder)
                    self.upload_progress = (
                        ui.linear_progress()
                        .classes("w-32 hidden")
                        .props("color=indigo track-color=indigo-1")
                    )

                    # Note: We use opacity-0 instead of hidden to ensure it's clickable via JS
                    self.upload = (
                        ui.upload(
                            auto_upload=True,
                            on_upload=self.handle_upload,
                            max_files=1,
                        )
                        .props('accept=".xlsx,.xls" flat')
                        .classes(
                            "absolute top-0 left-0 w-0 h-0 opacity-0 overflow-hidden"
                        )
                        .on(
                            "uploading",
                            lambda e: self.update_progress(e.args["percent"]),
                        )
                        .on("start", lambda: self.on_upload_start())
                        .on("finish", lambda: self.on_upload_finish())
                    )

                    # Trigger Button using Client-Side JS execution
                    ui.button(
                        "選擇 Excel 檔案",
                        icon="upload_file",
                    ).classes(
                        "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm rounded-lg text-sm px-4 py-2"
                    ).props("unelevated no-caps").on(
                        "click",
                        js_handler=f"getElement({self.upload.id}).pickFiles()",
                    )

        # Step 2: Tabbed Actions
        with ui.card().classes(
            "w-full p-0 shadow-sm border border-slate-200 rounded-xl bg-white mt-6 overflow-hidden dark:!bg-slate-800 dark:border-slate-700"
        ):
            with ui.tabs().classes(
                "w-full text-slate-500 bg-slate-50 border-b border-slate-200 active-text-indigo-600 indicator-color-indigo dark:!bg-slate-800 dark:border-slate-700 dark:text-slate-400 dark:active-text-indigo-400"
            ) as tabs:
                auto_fill_tab = ui.tab("摘要抓律師代碼", icon="manage_search").classes(
                    "h-14 font-medium"
                )
                separate_tab = ui.tab("律師收入明細", icon="pie_chart").classes(
                    "h-14 font-medium"
                )

            with ui.tab_panels(tabs, value=auto_fill_tab).classes("w-full p-8"):
                # Tab 1: Auto Fill
                with ui.tab_panel(auto_fill_tab):
                    with ui.row().classes("items-start gap-6"):
                        with ui.column().classes("flex-grow max-w-2xl"):
                            ui.label("功能說明").classes(
                                "text-lg font-bold text-slate-800 mb-2 dark:text-white"
                            )
                            ui.markdown(
                                "自動掃描 Excel `摘要` 欄位並填入 `備註`。"
                            ).classes(
                                "text-slate-600 leading-relaxed dark:text-slate-300"
                            )

                            with ui.element("div").classes(
                                "bg-indigo-50 p-4 rounded-lg mt-4 border border-indigo-100/50 flex gap-3 dark:bg-indigo-900/20 dark:border-indigo-800"
                            ):
                                ui.icon("info", size="20px").classes(
                                    "text-indigo-500 mt-0.5 dark:text-indigo-400"
                                )
                                with ui.column().classes("gap-1"):
                                    ui.label("智慧匹配").classes(
                                        "text-xs font-bold text-indigo-800 dark:text-indigo-300"
                                    )
                                    ui.label(
                                        "程式會根據摘要關鍵字自動匹配律師代碼。如果不確定，會跳出對話框詢問您。"
                                    ).classes(
                                        "text-sm text-indigo-700/80 dark:text-indigo-300/80"
                                    )

                        with ui.column().classes(
                            "items-end justify-center min-w-[200px]"
                        ):
                            self.btn_auto_fill = (
                                ui.button("執行：自動填入", on_click=self.run_auto_fill)
                                .props("icon=play_arrow unelevated")
                                .classes(
                                    "w-full h-12 text-sm font-bold rounded-lg shadow-sm bg-indigo-600 hover:bg-indigo-700 text-white transition-colors"
                                )
                            )
                            self.btn_auto_fill.disable()

                # Tab 2: Separate Ledger
                with ui.tab_panel(separate_tab):
                    with ui.row().classes("items-start gap-6"):
                        with ui.column().classes("flex-grow max-w-2xl"):
                            ui.label("功能說明").classes(
                                "text-lg font-bold text-slate-800 mb-2 dark:text-white"
                            )
                            ui.markdown(
                                "根據備註欄位的律師代碼拆分帳務，產生新的工作表。"
                            ).classes(
                                "text-slate-600 leading-relaxed dark:text-slate-300"
                            )

                            with ui.element("div").classes(
                                "bg-emerald-50 p-4 rounded-lg mt-4 border border-emerald-100/50 flex gap-3 dark:bg-emerald-900/20 dark:border-emerald-800"
                            ):
                                ui.icon("warning", size="20px").classes(
                                    "text-emerald-600 mt-0.5 dark:text-emerald-400"
                                )
                                with ui.column().classes("gap-1"):
                                    ui.label("寫入注意").classes(
                                        "text-xs font-bold text-emerald-800 dark:text-emerald-300"
                                    )
                                    ui.label(
                                        "請確保檔案未被其他程式開啟。結果將直接寫入原檔的新工作表。"
                                    ).classes(
                                        "text-sm text-emerald-700/80 dark:text-emerald-300/80"
                                    )

                        with ui.column().classes(
                            "items-end justify-center min-w-[200px]"
                        ):
                            self.btn_separate = (
                                ui.button("執行：拆分明細", on_click=self.run_separate)
                                .props("icon=play_arrow unelevated")
                                .classes(
                                    "w-full h-12 text-sm font-bold rounded-lg shadow-sm bg-emerald-600 hover:bg-emerald-700 text-white transition-colors"
                                )
                            )
                            self.btn_separate.disable()

        # Logs
        with (
            ui.expansion("執行日誌 (System Logs)", icon="terminal")
            .classes(
                "w-full mt-6 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm dark:!bg-slate-800 dark:border-slate-700"
            )
            .props(
                'header-class="bg-slate-50 text-slate-700 font-semibold dark:!bg-slate-800 dark:text-slate-200"'
            )
        ):
            self.log_container = ui.log().classes(
                "w-full h-48 font-mono text-xs bg-slate-900 text-emerald-400 p-4"
            )

    def on_upload_start(self):
        self.upload_progress.classes(remove="hidden")
        self.file_label.text = "正在上傳..."
        self.file_label.classes(
            remove="text-slate-400 italic", add="text-indigo-600 font-bold"
        )

    def on_upload_finish(self):
        self.upload_progress.classes(add="hidden")

    def update_progress(self, percent):
        self.upload_progress.value = percent

    async def handle_upload(self, e):
        # Save to temp file
        try:
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            # NiceGUI uses e.file.name and e.file.read() for uploaded file access
            file_name = e.file.name
            file_path = os.path.join(temp_dir, file_name)

            with open(file_path, "wb") as f:
                # e.file.read() is async in NiceGUI - need to await
                content = await e.file.read()
                f.write(content)

            self.selected_file = file_path
            self.file_label.text = f"{file_name}"
            self.file_label.classes(
                remove="text-slate-400 italic dark:text-slate-500",
                add="text-indigo-600 font-bold dark:text-indigo-400",
            )

            # Enable buttons
            self.btn_auto_fill.enable()
            self.btn_separate.enable()

            self.log_container.push(f"[INFO] 檔案已載入: {file_path}")
            ui.notify(
                f"檔案上傳成功: {file_name}",
                type="positive",
                icon="check_circle",
                color="emerald",
            )

        except Exception as ex:
            ui.notify(f"上傳失敗: {ex}", type="negative")
            self.log_container.push(f"[ERROR] 上傳錯誤: {ex}")

    async def run_auto_fill(self):
        if not self.selected_file:
            return
        try:
            self.log_container.push("[INFO] 開始執行：摘要抓律師代碼...")
            result = await self.service.run_auto_fill(self.selected_file)

            self.log_container.push(
                f"[SUCCESS] 執行完成。更新筆數: {result.updated_count}"
            )
            ui.notify(
                f"完成! 更新 {result.updated_count} 筆",
                type="positive",
                icon="check_circle",
            )
            ui.download(
                self.selected_file,
                filename=f"processed_{os.path.basename(self.selected_file)}",
            )

        except Exception as e:
            self.log_container.push(f"[ERROR] 錯誤: {e}")
            ui.notify(f"執行失敗: {e}", type="negative")

    async def run_separate(self):
        if not self.selected_file:
            return
        try:
            self.log_container.push("[INFO] 開始執行：律師收入明細...")
            await self.service.run_separate_ledger(
                self.selected_file, self.selected_file
            )

            self.log_container.push("[SUCCESS] 執行完成。已新增工作表。")
            ui.notify("執行完成", type="positive", icon="check_circle")
            ui.download(
                self.selected_file,
                filename=f"report_{os.path.basename(self.selected_file)}",
            )

        except Exception as e:
            self.log_container.push(f"[ERROR] 錯誤: {e}")
            ui.notify(f"執行失敗: {e}", type="negative")
