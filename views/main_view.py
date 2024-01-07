import logging
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import MainController

class MainView(ttk.Window):
    def __init__(self, controller: "MainController"):
        super().__init__(
            themename="superhero",
        )

        # Attributes
        self.selected_action_var = ttk.StringVar(value = "")
        self.output_filename = ttk.StringVar(value="")
        self.proccess_hint_text = ttk.StringVar(value="")
        
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





    def create_navigation_bar(self):
        navigation_bar = ttk.Frame(self, height = 60, width = 800, bootstyle = "info")
        navigation_bar.pack(side=TOP, fill=X, pady=0) # expand = NO, make sure it won't expand on the vertical axis

        welcome_label = ttk.Label(navigation_bar, text = "歡迎使用工具包", font = ("Microsoft Yahei", 14), anchor=CENTER, bootstyle="white", background=self.style.colors.info)
        welcome_label.pack(pady=10)
    
    def create_body_frame(self):
        self.body_frame = ttk.Frame(self)
        self.body_frame.pack(fill=BOTH, expand=YES)
    
    def create_target_file_frame(self):
        target_file_container = ttk.Frame(self.body_frame)
        target_file_container.pack(fill=X, expand=YES, pady=(10, 10))

        hint_label = ttk.Label(target_file_container, text = "請選擇來源檔案", font = ("Microsoft Yahei", 14), width = 15, anchor = CENTER, bootstyle = "white")
        hint_label.pack(side=LEFT, padx=(10, 5))

        select_file_text = ttk.StringVar(value="")
        select_file_label = ttk.Label(target_file_container, textvariable=select_file_text, font = ("Microsoft Yahei", 14), anchor=CENTER, bootstyle= "white")
        select_file_label.pack(side=LEFT, padx=(10, 5))

        select_file_btn = ttk.Button(target_file_container, text = "選擇檔案", command=lambda: self.select_source_file(select_file_text), bootstyle = "primary")
        select_file_btn.pack(side=LEFT)
        return
    
    def create_functionality_buttons(self):
        functionality_buttons_container = ttk.Frame(self.body_frame)
        functionality_buttons_container.pack(fill=X, expand=YES, pady=(10, 10), padx=(10, 10))

        hint_label = ttk.Label(functionality_buttons_container, text = "請選擇要執行的功能", font = ("Microsoft Yahei", 14), width = 20, anchor = CENTER, bootstyle = "white")
        hint_label.pack(side = TOP, expand = NO)

        ttk.Style().configure("info.TButton", font = ("Microsoft Yahei", 12))

        separate_the_ledger_btn = ttk.Button(functionality_buttons_container, text = "律師收入明細", command=lambda: self.process_selected_action("separate_the_ledger"), style = "info.TButton")
        separate_the_ledger_btn.pack(side=LEFT, padx=(10, 10))
        return
    
    def create_output_config_frame(self):
        output_config_frame = ttk.Frame(self.body_frame)
        output_config_frame.pack(fill=X, expand=YES, pady=(10, 10), padx=(10, 10))

        ttk.Label(output_config_frame, text = "輸出設定", font = ("Microsoft Yahei", 14), width = 15, anchor = CENTER, bootstyle = "white").pack(side=TOP, pady=(5, 5))

        dir_frame = ttk.Frame(output_config_frame)
        dir_frame.pack(side=TOP, fill=X, expand=YES, pady=(10, 10), padx=(10, 5))
        dir_hint_text = ttk.Label(dir_frame, text = "輸出資料夾", font = ("Microsoft Yahei", 14), width = 15, anchor = CENTER, bootstyle = "white")
        dir_hint_text.pack(side=LEFT)
        selected_dir_text = ttk.StringVar(value = "")
        selected_dir_label = ttk.Label(dir_frame, textvariable=selected_dir_text, font = ("Microsoft Yahei", 14), anchor=W, bootstyle="white")
        selected_dir_label.pack(side=LEFT, padx=(10, 10))
        dir_button = ttk.Button(dir_frame, text = "選擇資料夾", command=lambda: self.select_output_dir(selected_dir_text), bootstyle = "primary")
        dir_button.pack(side=LEFT)

        filename_frame = ttk.Frame(output_config_frame)
        filename_frame.pack(fill=X, expand=YES, pady=(10, 10), padx=(5, 5))
        filename_hint_text = ttk.Label(filename_frame, text = "輸出檔案名稱: ", font = ("Microsoft Yahei", 14), width = 15, anchor = CENTER, bootstyle = "white")
        filename_hint_text.pack(side=LEFT, padx=(10, 10))
        filename_input = ttk.Entry(master = filename_frame, textvariable=self.output_filename)
        filename_input.pack(side=LEFT, fill=X, expand=YES)

        proccess_button_frame = ttk.Frame(output_config_frame)
        proccess_button_frame.pack(side=BOTTOM, fill=X, expand=YES, pady=(10, 10), padx=(10, 5))
        proccess_label = ttk.Label(proccess_button_frame, textvariable=self.proccess_hint_text, font = ("Microsoft Yahei", 14), anchor = CENTER, bootstyle = "white")
        proccess_label.pack(padx=(10, 10))
        proccess_button = ttk.Button(proccess_button_frame, text="執行功能 (Submit)", command=lambda: self.on_process(), bootstyle="success")
        proccess_button.pack(side=RIGHT, padx=(10, 10))
        return
    
    # When user select a source file
    def select_source_file(self, hint_text: "ttk.StringVar"):
        selected_filename = self.controller.open_excel_file()
        hint_text.set(selected_filename)

    # When user select a output folder
    def select_output_dir(self, hint_text: "ttk.StringVar"):
        output_dir = self.controller.choose_output_dir()
        hint_text.set(output_dir)
    
    # When user click functionality buttons
    def process_selected_action(self, action):
        self.selected_action_var.set(action)
        logging.debug(f"用戶選擇進行的操作: {self.selected_action_var.get()}")

    # When user click 'process' or 'submit' button
    def on_process(self):
        if (self.selected_action_var.get() == "separate_the_ledger"):
            self.controller.separate_the_ledger()
        else:
            messagebox.showinfo("說明", "請先選擇要執行的功能！")
    