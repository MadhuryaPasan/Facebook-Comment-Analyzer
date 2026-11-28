from datetime import UTC, datetime

from sqlmodel import Session

from app.modules.posts.models.schemas import (
    PostFilterParams,
    PostListResponseDTO,
    PostResponseDTO,
    SentimentSummaryDTO,
)

# Sample data used until the database is connected.
SAMPLE_POSTS = [
    PostResponseDTO(
        post_id="1029384756_5566778899",
        message="Our new rice & curry menu is live! Order now.",
        created_time=datetime(2026, 11, 20, 10, 15, tzinfo=UTC),
        comment_count=84,
        analyzed_count=80,
        sentiment_summary=SentimentSummaryDTO(positive=52, neutral=18, negative=10),
    ),
    PostResponseDTO(
        post_id="1029384756_6677889900",
        message="Delivery update: we now deliver until 10 pm.",
        created_time=datetime(2026, 11, 10, 9, 0, tzinfo=UTC),
        comment_count=30,
        analyzed_count=30,
        sentiment_summary=SentimentSummaryDTO(positive=10, neutral=8, negative=12),
    ),
]


class PostService:
    """Business logic for retrieving Facebook page posts and sentiment overviews."""

    @staticmethod
    def get_posts(filters: PostFilterParams, db: Session) -> PostListResponseDTO:
        """Return posts matching the requested date-range filters."""
        items = SAMPLE_POSTS
        if filters.from_date is not None:
            items = [p for p in items if p.created_time.date() >= filters.from_date]
        if filters.to_date is not None:
            items = [p for p in items if p.created_time.date() <= filters.to_date]
        items = sorted(items, key=lambda p: p.created_time, reverse=True)
        return PostListResponseDTO(items=items)

    @staticmethod
    def get_post(post_id: str, db: Session) -> PostResponseDTO:
        """Return a single post and its sentiment breakdown."""
        raise NotImplementedError("PostService.get_post is not implemented yet")