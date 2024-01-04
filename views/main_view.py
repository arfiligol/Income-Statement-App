import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import MainController

from .custom_widgets import PlaceholderEntry

class MainView(tk.Tk):
    def __init__(self, controller: "MainController"): # controller 在 Controller Class 中以 "self" 傳入
        super().__init__()
        self.controller = controller
        self.title("小倩工具箱")
        
        # Initialization
        # Initialize the MainView window
        self.setup_window()
        # Initialize Labels in this window
        self.init_labels()
        # Initialize Buttons in this window
        self.init_buttons()
        # Initialize Entries in this window
        self.init_entries()
        # Packing Objects
        self.packup_tkObjects()
    
    def setup_window(self):
        self.geometry("800x400")


    def init_labels(self):
        # 創建多個 Label 並使用 Dictionary 的方式管理
        self.labels = {}
        label_texts = { # 有添加 Label 需求，請在這裡添加 Key-Value Pair
            "OpenedFilePathLabel": "尚未選擇檔案",
            "OutputDirPathLabel": "尚未選擇輸出資料夾",
            "DealingWorkIsDoneLabel": "",
        }

        for label_name, text in label_texts.items():
            label = tk.Label(self, text = text)
            self.labels[label_name] = label
    
    def init_buttons(self):
        # 創建多個 Button 並使用 Dictionary 的方式管理
        self.buttons = {}
        button_attributes = {
            "OpenExcelFileButton": {
                "text": "選擇檔案",
                "command": lambda: self.controller.open_excel_file(),
            },
            "ChooseOutputDirButton": {
                "text": "選擇輸出資料夾",
                "command": lambda: self.controller.choose_output_dir(),
            },
            "HandleFileButton": {
                "text": "處理檔案",
                "command": lambda: self.controller.separate_the_ledger(),
            }
        }

        for button_name, button_attribute in button_attributes.items():
            button = tk.Button(self, text = button_attribute["text"], command=button_attribute["command"])
            self.buttons[button_name] = button
    
    def init_entries(self):
        # 創建多個 Entry 並使用 Dictionary 的方式管理
        self.entries = {}
        entry_attributes = {
            "OutputFileNameEntry": {
                "HintText": "輸入輸出檔名"
            }
        }

        for entry_name, entry_attribute in entry_attributes.items():
            entry = PlaceholderEntry(self, entry_attribute["HintText"])
            self.entries[entry_name] = entry

    def packup_tkObjects(self):
        self.labels["OpenedFilePathLabel"].grid(row = 0, column = 1, pady=10)
        self.buttons["OpenExcelFileButton"].grid(row = 1, column = 1, pady=10)
        self.labels["OutputDirPathLabel"].grid(row = 2, column = 0, pady = 10, padx = 5)
        self.entries["OutputFileNameEntry"].grid(row = 2, column = 1, pady=10, padx = 5)
        self.buttons["ChooseOutputDirButton"].grid(row = 2, column = 3, pady = 10, padx = 5)
        self.buttons["HandleFileButton"].grid(row = 3, column = 1, pady=10)