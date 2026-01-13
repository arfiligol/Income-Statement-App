from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")

# Type alias for paths
PathLike = str | Path


@dataclass
class Result(Generic[T, E]):
    """
    A generic Result type to handle Success/Failure without raising exceptions immediately.
    This encourages explicit error handling in the application layer.
    """

    value: T | None = None
    error: E | None = None
    is_success: bool = True

    @classmethod
    def success(cls, value: T) -> "Result[T, E]":
        return cls(value=value, is_success=True)

    @classmethod
    def failure(cls, error: E) -> "Result[T, E]":
        return cls(error=error, is_success=False)

    def unwrap(self) -> T:
        if not self.is_success:
            raise ValueError(f"Called unwrap on a failure Result: {self.error}")
        # We know value is not None if success, but type checker might not.
        # Strict typing: T | None.
        return self.value  # type: ignore
