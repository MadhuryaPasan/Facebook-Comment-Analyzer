from app.core.exceptions import NotFoundException


class CommentNotFoundException(NotFoundException):
    """Raised when a requested Facebook comment does not exist in storage."""

    def __init__(self, comment_id: str) -> None:
        super().__init__(detail=f"Comment {comment_id} does not exist", code="COMMENT_NOT_FOUND")
