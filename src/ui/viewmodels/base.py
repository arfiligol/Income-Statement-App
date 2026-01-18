from typing import Any, Callable, Generic, TypeVar

from nicegui import ui

TState = TypeVar("TState")


class BaseViewModel(Generic[TState]):
    """
    Base class for ViewModels.
    Manages State, Intents, and Effects.
    """

    def __init__(self, initial_state: TState):
        self._state = initial_state
        self._listeners: list[Callable[[TState], None]] = []
        self._effect_handlers: list[Callable[[Any], None]] = []

    @property
    def state(self) -> TState:
        return self._state

    def update_state(self, **kwargs):
        """
        Partially updates state and notifies listeners.
        Note: TState should ideally be a dataclass.
        """
        for key, value in kwargs.items():
            if hasattr(self._state, key):
                setattr(self._state, key, value)

        self.notify_listeners()

    def add_listener(self, callback: Callable[[TState], None]):
        self._listeners.append(callback)

    def notify_listeners(self):
        for callback in self._listeners:
            callback(self._state)

    def emit_effect(self, effect: Any):
        """Emits a side effect (toast, dialog, navigation)."""
        for handler in self._effect_handlers:
            handler(effect)

    def on_effect(self, handler: Callable[[Any], None]):
        self._effect_handlers.append(handler)
