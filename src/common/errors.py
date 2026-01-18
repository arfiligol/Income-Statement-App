class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        super().__init__(message)
        self.code = code


class DomainError(AppError):
    """Errors related to domain rules and validation."""

    pass


class ValidationError(AppError):
    """Errors related to input validation (e.g. invalid file format)."""

    pass


class InfrastructureError(AppError):
    """Errors related to external systems (I/O, Database, Network)."""

    pass
