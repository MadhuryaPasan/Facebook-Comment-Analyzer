class AppException(Exception):
    """Base exception for the app.

    Every AppException is returned as:
    {"error": {"code": "<code>", "message": "<detail>"}}
    """
    def __init__(self, status_code: int, code: str, detail: str, headers: dict[str, str] | None = None):
        self.status_code = status_code
        self.code = code
        self.detail = detail
        self.headers = headers
        super().__init__(detail)


# ---- Generic ----

class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(status_code=404, code=code, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request", code: str = "BAD_REQUEST"):
        super().__init__(status_code=400, code=code, detail=detail)


class ServiceUnavailableException(AppException):
    def __init__(self, detail: str = "Service temporarily unavailable", code: str = "SERVICE_UNAVAILABLE"):
        super().__init__(status_code=503, code=code, detail=detail)


# ---- Posts ----

class PostNotFoundException(NotFoundException):
    def __init__(self, post_id: str):
        super().__init__(detail=f"Post {post_id} does not exist", code="POST_NOT_FOUND")


# ---- Comments ----

class CommentNotFoundException(NotFoundException):
    def __init__(self, comment_id: str):
        super().__init__(detail=f"Comment {comment_id} does not exist", code="COMMENT_NOT_FOUND")


# ---- Analysis ----

class TaskQueueUnavailableException(ServiceUnavailableException):
    """Raised when the post can't be added to the task queue (e.g. Redis is down)."""
    def __init__(self, detail: str = "Analysis queue is unavailable, try again later"):
        super().__init__(detail=detail, code="TASK_QUEUE_UNAVAILABLE")
