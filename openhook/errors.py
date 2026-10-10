"""Errors safe to return to an Openhook client."""


class InboxError(ValueError):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status
