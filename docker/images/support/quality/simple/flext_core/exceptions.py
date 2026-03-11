class Error(Exception):
    def __init__(self, message: str, context: dict[str, object] = None):
        super().__init__(message)
        self.context = context or {}


class ValidationError(Error):
    pass


class ConfigurationError(Error):
    pass


class ConnectionError(Error):
    pass


class ProcessingError(Error):
    pass


class AuthenticationError(Error):
    pass


class TimeoutError(Error):
    pass
