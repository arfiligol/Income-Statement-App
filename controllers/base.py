from typing import Union # 用於【類型提示】
import tkinter as tk

class BaseController:
    def __init__(self):
                self.window: Union[tk.Tk, tk.Toplevel, None] = None # Window 在子類 Controller 中創建

    def show_window(self):
        if self.window is not None:
            self.window.deiconify() # Shows the window if it is hidden

    def hide_window(self):
        if self.window is not None:
            self.window.withdraw()

    def close_window(self):
        if self.window is not None:
            self.window.destroy()
            self.window = None