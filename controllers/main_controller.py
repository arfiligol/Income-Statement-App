from .base import BaseController
from views import MainView

class MainController(BaseController):
    def __init__(self):
        super().__init__()
        self.window = MainView(self)
        self.window.mainloop()