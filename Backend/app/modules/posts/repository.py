from sqlmodel import Session


class PostRepository:
    """Data-access layer for reading and persisting Facebook posts."""

    @staticmethod
    def list_posts(db: Session, from_date=None, to_date=None):
        """Query posts filtered by optional creation date range."""
        raise NotImplementedError("PostRepository.list_posts is not implemented yet")

    @staticmethod
    def get_by_id(db: Session, post_id: str):
        """Fetch a single post by its Facebook post ID."""
        raise NotImplementedError("PostRepository.get_by_id is not implemented yet")
