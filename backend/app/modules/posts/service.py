from sqlmodel import Session

from app.modules.posts.models.schemas import PostFilterParams, PostListResponseDTO, PostResponseDTO


class PostService:
    """Business logic for retrieving Facebook page posts and sentiment overviews."""

    @staticmethod
    def get_posts(filters: PostFilterParams, db: Session) -> PostListResponseDTO:
        """Return posts matching the requested date-range filters."""
        raise NotImplementedError("PostService.get_posts is not implemented yet")

    @staticmethod
    def get_post(post_id: str, db: Session) -> PostResponseDTO:
        """Return a single post and its sentiment breakdown."""
        raise NotImplementedError("PostService.get_post is not implemented yet")
