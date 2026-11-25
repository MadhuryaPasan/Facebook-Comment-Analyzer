class AppException(Exception):
    """Base exception for all HTTP-mapped domain errors.

    Every AppException is serialized as:
    `{"error": {"code": "<code>", "message": "<detail>"}}`
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.detail = detail
        self.headers = headers
        super().__init__(detail)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist (HTTP 404)."""

    def __init__(self, detail: str = "Resource not found", code: str = "NOT_FOUND") -> None:
        super().__init__(status_code=404, code=code, detail=detail)


class BadRequestException(AppException):
    """Raised when the client supplies an invalid request (HTTP 400)."""

    def __init__(self, detail: str = "Bad request", code: str = "BAD_REQUEST") -> None:
        super().__init__(status_code=400, code=code, detail=detail)


class ServiceUnavailableException(AppException):
    """Raised when an external dependency or queue is unavailable (HTTP 503)."""

    def __init__(
        self,
        detail: str = "Service temporarily unavailable",
        code: str = "SERVICE_UNAVAILABLE",
    ) -> None:
        super().__init__(status_code=503, code=code, detail=detail)
