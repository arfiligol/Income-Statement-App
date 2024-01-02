import tkinter as tk

class MainView(tk.Tk):
    def __init__(self, controller): # controller 在 Controller Class 中以 "self" 傳入
        super().__init__()
        self.controller = controller
        self.title("小倩工具箱")
        
        # Initialization
        # Initialize the MainView window
        self.setup_window()
        # Initialize Labels in this window
        self.init_labels()
    
    def setup_window(self):
        self.geometry("400x200")


    def init_labels(self):
        # 創建多個 Label 並使用 Dictionary 的方式管理
        self.labels = {}
        label_texts = { # 有添加 Label 需求，請在這裡添加 Key-Value Pair
            "OpenedFilePathLabel": "尚未開啟檔案"
        }

        for label_name, text in label_texts.items():
            label = tk.Label(self, text = text)
            label.pack()
            self.labels[label_name] = label
    
    def init_buttons(self):
        # 創建多個 Button 並使用 Dictionary 的方式管理
        self.buttons = {}
        button_attributes = {
            "OpenFileButton" : {
                "text": "選擇檔案",
                "command": lambda: open_file(),
            }
        }