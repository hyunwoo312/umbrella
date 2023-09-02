class ValidationError(Exception):
    """A custom exception thrown when there is any failure in validating some value(s)."""

    def __init__(self, message: str = "Validation failed."):
        super().__init__(message)
