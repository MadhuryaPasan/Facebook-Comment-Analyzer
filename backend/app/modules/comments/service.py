from sqlmodel import Session

from app.modules.comments.models.schemas import (
    CommentDetailResponseDTO,
    CommentFilterParams,
    CommentListResponseDTO,
    CommentSearchParams,
)


class CommentService:
    """Business logic for querying Facebook comments, replies, and analysis views."""

    @staticmethod
    def get_post_comments(
        post_id: str,
        filters: CommentFilterParams,
        db: Session,
    ) -> CommentListResponseDTO:
        """Return comments belonging to a specific Facebook post."""
        raise NotImplementedError("CommentService.get_post_comments is not implemented yet")

    @staticmethod
    def get_comments(
        filters: CommentSearchParams,
        db: Session,
    ) -> CommentListResponseDTO:
        """Search comments across all posts using filter criteria."""
        raise NotImplementedError("CommentService.get_comments is not implemented yet")

    @staticmethod
    def get_comment(comment_id: str, db: Session) -> CommentDetailResponseDTO:
        """Return a single comment with full analysis metadata and nested replies."""
        raise NotImplementedError("CommentService.get_comment is not implemented yet")
