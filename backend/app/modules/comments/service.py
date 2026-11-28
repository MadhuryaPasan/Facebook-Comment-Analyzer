from sqlmodel import Session

from app.modules.comments.exceptions import CommentNotFoundException
from app.modules.comments.models.schemas import (
    CommentDetailResponseDTO,
    CommentFilterParams,
    CommentListResponseDTO,
    CommentResponseDTO,
    CommentSearchParams,
)

_MOCK_COMMENTS = [
    CommentDetailResponseDTO(
        comment_id="5566778899_1122334455",
        post_id="1029384756_5566778899",
        parent_id=None,
        message="Delivery took 2 hours and the food was cold",
        created_time="2026-11-20T12:03:00Z",
        like_count=5,
        analysis={
            "language": "en",
            "sentiment": "negative",
            "sentiment_score": 0.94,
            "intent": "complaint",
            "aspects": [
                {
                    "aspect": "delivery",
                    "sentiment": "negative",
                    "score": 0.96,
                },
                {
                    "aspect": "food_quality",
                    "sentiment": "negative",
                    "score": 0.81,
                },
            ],
            "keywords": ["delivery", "2 hours", "cold"],
            "is_actionable": True,
            "model_version": "analyzer-0.1.0",
            "analyzed_at": "2026-11-20T12:05:10Z",
        },
        replies=[
            {
                "comment_id": "5566778899_1122334499",
                "message": "Sorry about this! Please DM us your order number.",
                "created_time": "2026-11-20T12:30:00Z",
            }
        ],
    ),
    CommentDetailResponseDTO(
        comment_id="5566778899_1122334466",
        post_id="1029384756_5566778899",
        parent_id=None,
        message="Amazing food and excellent service!",
        created_time="2026-11-20T13:00:00Z",
        like_count=12,
        analysis={
            "language": "en",
            "sentiment": "positive",
            "sentiment_score": 0.98,
            "intent": "praise",
            "aspects": [
                {
                    "aspect": "food_quality",
                    "sentiment": "positive",
                    "score": 0.97,
                }
            ],
            "keywords": ["food", "service"],
            "is_actionable": False,
            "model_version": "analyzer-0.1.0",
            "analyzed_at": "2026-11-20T13:05:00Z",
        },
        replies=[],
    ),
    CommentDetailResponseDTO(
        comment_id="6677889900_2233445577",
        post_id="1029384756_6677889900",
        parent_id=None,
        message="What time do you open tomorrow?",
        created_time="2026-11-21T09:00:00Z",
        like_count=1,
        analysis={
            "language": "en",
            "sentiment": "neutral",
            "sentiment_score": 0.85,
            "intent": "question",
            "aspects": [
                {
                    "aspect": "opening_hours",
                    "sentiment": "neutral",
                    "score": 0.85,
                }
            ],
            "keywords": ["opening", "time"],
            "is_actionable": True,
            "model_version": "analyzer-0.1.0",
            "analyzed_at": "2026-11-21T09:05:00Z",
        },
        replies=[],
    ),
    CommentDetailResponseDTO(
        comment_id="6677889900_2233445588",
        post_id="1029384756_6677889900",
        parent_id=None,
        message="Can you add more vegetarian meals?",
        created_time="2026-11-22T10:00:00Z",
        like_count=3,
        analysis=None,
        replies=[],
    ),
    CommentDetailResponseDTO(
        comment_id="6677889900_2233445566",
        post_id="1029384756_6677889900",
        parent_id=None,
        message="Ordered at 7, still waiting at 8:30",
        created_time="2026-11-22T15:10:00Z",
        like_count=2,
        analysis={
            "language": "en",
            "sentiment": "negative",
            "sentiment_score": 0.89,
            "intent": "complaint",
            "aspects": [
                {
                    "aspect": "delivery",
                    "sentiment": "negative",
                    "score": 0.92,
                }
            ],
            "keywords": ["ordered", "waiting"],
            "is_actionable": True,
            "model_version": "analyzer-0.1.0",
            "analyzed_at": "2026-11-22T15:15:00Z",
        },
        replies=[],
    ),
]


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

        results: list[CommentResponseDTO] = []

        for comment in _MOCK_COMMENTS:
            analysis = comment.analysis

            if filters.post_id is not None and comment.post_id != filters.post_id:
                continue

            if filters.from_date is not None and comment.created_time.date() < filters.from_date:
                continue

            if filters.to_date is not None and comment.created_time.date() > filters.to_date:
                continue

            if filters.analyzed is not None:
                is_analyzed = analysis is not None
                if is_analyzed != filters.analyzed:
                    continue

            if filters.sentiment is not None and (
                analysis is None or analysis.sentiment != filters.sentiment
            ):
                continue

            if filters.intent is not None and (
                analysis is None or analysis.intent != filters.intent
            ):
                continue

            if filters.aspect is not None and (
                analysis is None
                or not any(aspect.aspect == filters.aspect for aspect in analysis.aspects)
            ):
                continue

            results.append(
                CommentResponseDTO.model_validate(comment.model_dump(exclude={"replies"}))
            )

        return CommentListResponseDTO(items=results)

    @staticmethod
    def get_comment(
        comment_id: str,
        db: Session,
    ) -> CommentDetailResponseDTO:
        """Return a single comment with full analysis metadata and nested replies."""

        for comment in _MOCK_COMMENTS:
            if comment.comment_id == comment_id:
                return comment

        raise CommentNotFoundException(comment_id)
