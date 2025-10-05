from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING, Dict

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, BOTTOM, CENTER, LEFT, PRIMARY, RIGHT, TOP, W, X

if TYPE_CHECKING:
    from ttk_app.controllers import MainController

class MainView(ttk.Window):
    def __init__(self, controller: "MainController"):
        super().__init__(
            themename="superhero",
        )

        # Attributes
        self.selected_action_var = ttk.StringVar(value="")
        self.output_filename = ttk.StringVar(value="")
        self.proccess_hint_text = ttk.StringVar(value="")
        self.source_file_text = ttk.StringVar(value="")
        self.selected_dir_text = ttk.StringVar(value="")
        self.action_buttons: Dict[str, ttk.Button] = {}
        self._default_action_bootstyle = "info"
        self._selected_action_bootstyle = "success"
        self.current_view = "workflow"
        
        # Controller
        self.controller = controller
        self.title("小倩工具箱")

        # Create Navigation Bar
        self.create_navigation_bar()
        
        # Create Body Frame
        self.create_body_frame()

        # Create Target File Frame
        self.create_target_file_frame()

        # Create Functionality Buttons
        self.create_functionality_buttons()

        # Create Output Config Frame
        self.create_output_config_frame()





    def create_navigation_bar(self) -> None:
        navigation_bar = ttk.Frame(self, height=60, width=800, bootstyle="info")
        navigation_bar.pack(side=TOP, fill=X, pady=0, expand=False)

        welcome_label = ttk.Label(
            navigation_bar,
            text="歡迎使用工具包",
            font=("Microsoft Yahei", 14),
            anchor=CENTER,
            bootstyle="white",
            background=self.style.colors.info,
        )
        welcome_label.pack(side=LEFT, padx=10, pady=10)

        tabs_container = ttk.Frame(navigation_bar, bootstyle="info")
        tabs_container.pack(side=RIGHT, padx=10, pady=10)

        self.workflow_tab_btn = ttk.Button(
            tabs_container,
            text="工作包",
            command=lambda: self.switch_view("workflow"),
        )
        self.workflow_tab_btn.pack(side=LEFT, padx=(0, 5))

        self.database_tab_btn = ttk.Button(
            tabs_container,
            text="資料庫操作",
            command=lambda: self.switch_view("database"),
        )
        self.database_tab_btn.pack(side=LEFT)

        self._update_tab_styles()
    
    def create_body_frame(self) -> None:
        self.body_frame = ttk.Frame(self)
        self.body_frame.pack(fill=BOTH, expand=True)
        self.workflow_frame = ttk.Frame(self.body_frame)
        self.workflow_frame.pack(fill=BOTH, expand=True)
        self.database_frame = ttk.Frame(self.body_frame)
        placeholder_label = ttk.Label(
            self.database_frame,
            text="資料庫操作頁面開發中...",
            font=("Microsoft Yahei", 14),
            bootstyle="white",
        )
        placeholder_label.pack(pady=20)
    
    def create_target_file_frame(self) -> None:
        target_file_container = ttk.Frame(self.workflow_frame)
        target_file_container.pack(fill=X, expand=True, pady=(10, 10))

        hint_label = ttk.Label(
            target_file_container,
            text="請選擇來源檔案",
            font=("Microsoft Yahei", 14),
            width=15,
            anchor=CENTER,
            bootstyle="white",
        )
        hint_label.pack(side=LEFT, padx=(10, 5))

        select_file_label = ttk.Label(
            target_file_container,
            textvariable=self.source_file_text,
            font=("Microsoft Yahei", 14),
            anchor=CENTER,
            bootstyle="white",
        )
        select_file_label.pack(side=LEFT, padx=(10, 5))

        select_file_btn = ttk.Button(
            target_file_container,
            text="選擇檔案",
            command=self.select_source_file,
            bootstyle="primary",
        )
        select_file_btn.pack(side=LEFT)
        return
    
    def create_functionality_buttons(self) -> None:
        functionality_buttons_container = ttk.Frame(self.workflow_frame)
        functionality_buttons_container.pack(fill=X, expand=True, pady=(10, 10), padx=(10, 10))

        hint_label = ttk.Label(
            functionality_buttons_container,
            text="請選擇要執行的功能",
            font=("Microsoft Yahei", 14),
            width=20,
            anchor=CENTER,
            bootstyle="white",
        )
        hint_label.pack(side=TOP, expand=False)

        self.style.configure("info.TButton", font=("Microsoft Yahei", 12))

        auto_fill_btn = ttk.Button(
            functionality_buttons_container,
            text="摘要填入律師代碼",
            command=lambda: self.process_selected_action("auto_fill_remark"),
            bootstyle=self._default_action_bootstyle,
        )
        auto_fill_btn.pack(side=LEFT, padx=(10, 10))
        self.action_buttons["auto_fill_remark"] = auto_fill_btn

        separate_the_ledger_btn = ttk.Button(
            functionality_buttons_container,
            text="律師收入明細",
            command=lambda: self.process_selected_action("separate_the_ledger"),
            bootstyle=self._default_action_bootstyle,
        )
        separate_the_ledger_btn.pack(side=LEFT, padx=(10, 10))
        self.action_buttons["separate_the_ledger"] = separate_the_ledger_btn
        self._update_action_button_styles()

    def create_output_config_frame(self) -> None:
        output_config_frame = ttk.Frame(self.workflow_frame)
        output_config_frame.pack(fill=X, expand=True, pady=(10, 10), padx=(10, 10))

        ttk.Label(
            output_config_frame,
            text="輸出設定",
            font=("Microsoft Yahei", 14),
            width=15,
            anchor=CENTER,
            bootstyle="white",
        ).pack(side=TOP, pady=(5, 5))

        dir_frame = ttk.Frame(output_config_frame)
        dir_frame.pack(side=TOP, fill=X, expand=True, pady=(10, 10), padx=(10, 5))
        dir_hint_text = ttk.Label(
            dir_frame,
            text="輸出資料夾",
            font=("Microsoft Yahei", 14),
            width=15,
            anchor=CENTER,
            bootstyle="white",
        )
        dir_hint_text.pack(side=LEFT)
        selected_dir_label = ttk.Label(
            dir_frame,
            textvariable=self.selected_dir_text,
            font=("Microsoft Yahei", 14),
            anchor=W,
            bootstyle="white",
        )
        selected_dir_label.pack(side=LEFT, padx=(10, 10))
        dir_button = ttk.Button(
            dir_frame,
            text="選擇資料夾",
            command=self.select_output_dir,
            bootstyle="primary",
        )
        dir_button.pack(side=LEFT)

        filename_frame = ttk.Frame(output_config_frame)
        filename_frame.pack(fill=X, expand=True, pady=(10, 10), padx=(5, 5))
        filename_hint_text = ttk.Label(
            filename_frame,
            text="輸出檔案名稱: ",
            font=("Microsoft Yahei", 14),
            width=15,
            anchor=CENTER,
            bootstyle="white",
        )
        filename_hint_text.pack(side=LEFT, padx=(10, 10))
        filename_input = ttk.Entry(master = filename_frame, textvariable=self.output_filename)
        filename_input.pack(side=LEFT, fill=X, expand=True)

        proccess_button_frame = ttk.Frame(output_config_frame)
        proccess_button_frame.pack(side=BOTTOM, fill=X, expand=True, pady=(10, 10), padx=(10, 5))
        proccess_label = ttk.Label(proccess_button_frame, textvariable=self.proccess_hint_text, font = ("Microsoft Yahei", 14), anchor = CENTER, bootstyle = "white")
        proccess_label.pack(padx=(10, 10))
        proccess_button = ttk.Button(proccess_button_frame, text="執行功能 (Submit)", command=lambda: self.on_process(), bootstyle="success")
        proccess_button.pack(side=RIGHT, padx=(10, 10))
        return
    
    # When user select a source file
    def select_source_file(self) -> None:
        selected_filename = self.controller.open_excel_file()
        if selected_filename:
            self.set_source_file_path(selected_filename)

    # When user select a output folder
    def select_output_dir(self) -> None:
        output_dir = self.controller.choose_output_dir()
        if output_dir:
            self.set_output_dir_path(output_dir)
    
    # When user click functionality buttons
    def process_selected_action(self, action: str) -> None:
        current_action = self.selected_action_var.get()
        if current_action == action:
            self.selected_action_var.set("")
            logging.debug("用戶取消選擇的操作: %s", action)
        else:
            self.selected_action_var.set(action)
            logging.debug("用戶選擇進行的操作: %s", action)

        self._update_action_button_styles()

    # When user click 'process' or 'submit' button
    def on_process(self) -> None:
        selected_action = self.selected_action_var.get()
        if selected_action == "auto_fill_remark":
            self.controller.auto_fill_lawyer_codes()
        elif selected_action == "separate_the_ledger":
            self.controller.separate_the_ledger()
        else:
            messagebox.showinfo("說明", "請先選擇要執行的功能！")

    def _update_action_button_styles(self) -> None:
        selected_action = self.selected_action_var.get()
        for action_name, button in self.action_buttons.items():
            if action_name == selected_action:
                button.configure(bootstyle=self._selected_action_bootstyle)
            else:
                button.configure(bootstyle=self._default_action_bootstyle)

    def switch_view(self, target_view: str) -> None:
        if target_view == self.current_view:
            return

        if target_view == "workflow":
            self.database_frame.pack_forget()
            self.workflow_frame.pack(fill=BOTH, expand=True)
        else:
            self.workflow_frame.pack_forget()
            self.database_frame.pack(fill=BOTH, expand=True)

        self.current_view = target_view
        self._update_tab_styles()

    def set_source_file_path(self, path: str) -> None:
        self.source_file_text.set(path)

    def set_output_dir_path(self, path: str) -> None:
        self.selected_dir_text.set(path)

    def _update_tab_styles(self) -> None:
        active_style = "primary"
        inactive_style = "secondary"

        if self.current_view == "workflow":
            self.workflow_tab_btn.configure(bootstyle=active_style)
            self.database_tab_btn.configure(bootstyle=inactive_style)
        else:
            self.workflow_tab_btn.configure(bootstyle=inactive_style)
            self.database_tab_btn.configure(bootstyle=active_style)
