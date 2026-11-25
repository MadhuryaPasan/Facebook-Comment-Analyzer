from sqlmodel import Session


class CommentRepository:
    """Data-access layer for querying Facebook comments and analysis records."""

    @staticmethod
    def list_by_post(db: Session, post_id: str, filters=None):
        """Query comments belonging to a specific post."""
        raise NotImplementedError("CommentRepository.list_by_post is not implemented yet")

    @staticmethod
    def search_comments(db: Session, filters=None):
        """Search comments across all posts using sentiment, intent, aspect, and date filters."""
        raise NotImplementedError("CommentRepository.search_comments is not implemented yet")

    @staticmethod
    def get_by_id(db: Session, comment_id: str):
        """Fetch a single comment along with its full analysis and replies."""
        raise NotImplementedError("CommentRepository.get_by_id is not implemented yet")
