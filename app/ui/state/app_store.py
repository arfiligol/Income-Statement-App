from dataclasses import dataclass


@dataclass
class AppState:
    """Global application state (User preferences, Dark mode, etc.)"""

    is_dark_mode: bool = True
    active_page: str = "home"


class AppStore:
    """
    Simple singleton-like store for cross-page state.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppStore, cls).__new__(cls)
            cls._instance.state = AppState()
        return cls._instance

    def toggle_dark_mode(self):
        self.state.is_dark_mode = not self.state.is_dark_mode
        # In a real app, you might emit an event here or bind to ui.dark_mode()
