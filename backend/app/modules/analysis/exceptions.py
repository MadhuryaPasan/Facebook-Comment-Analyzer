from app.core.exceptions import ServiceUnavailableException


class TaskQueueUnavailableException(ServiceUnavailableException):
    """Raised when an analysis job cannot be enqueued (e.g., Redis broker is down)."""

    def __init__(
        self,
        detail: str = "Analysis queue is unavailable, try again later",
    ) -> None:
        super().__init__(detail=detail, code="TASK_QUEUE_UNAVAILABLE")
