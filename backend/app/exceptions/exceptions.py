class AppError(Exception):
    """Base error. Every error returns {"error": {"code", "message"}}."""

    status_code: int = 400
    code: str = "APP_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PostNotFoundError(AppError):
    status_code = 404
    code = "POST_NOT_FOUND"


class CommentNotFoundError(AppError):
    status_code = 404
    code = "COMMENT_NOT_FOUND"
