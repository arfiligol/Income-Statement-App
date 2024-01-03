import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import MainController

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
        # Packing Objects
        self.packup_tkObjects()
    
    def setup_window(self):
        self.geometry("400x200")


    def init_labels(self):
        # 創建多個 Label 並使用 Dictionary 的方式管理
        self.labels = {}
        label_texts = { # 有添加 Label 需求，請在這裡添加 Key-Value Pair
            "OpenedFilePathLabel": "尚未選擇檔案"
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
            "HandleFileButton": {
                "text": "處理檔案",
                "command": lambda: self.controller.separate_the_ledger(),
            }
        }

        for button_name, button_attribute in button_attributes.items():
            button = tk.Button(self, text = button_attribute["text"], command=button_attribute["command"])
            self.buttons[button_name] = button
    
    def packup_tkObjects(self):
        self.labels["OpenedFilePathLabel"].pack(pady=10)
        self.buttons["OpenExcelFileButton"].pack(pady=10)
        self.buttons["HandleFileButton"].pack(pady=10)