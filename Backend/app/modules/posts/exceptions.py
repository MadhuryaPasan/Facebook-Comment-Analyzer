from app.core.exceptions import NotFoundException


class PostNotFoundException(NotFoundException):
    """Raised when a requested Facebook post does not exist in storage."""

    def __init__(self, post_id: str) -> None:
        super().__init__(detail=f"Post {post_id} does not exist", code="POST_NOT_FOUND")
