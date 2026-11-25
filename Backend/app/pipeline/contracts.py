from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import Intent, Language, Sentiment
from app.shared.schemas import AspectSentimentDTO
from app.shared.types import FBCommentId, FBPostId, Score


class RawComment(BaseModel):
    """Contract produced by `FacebookCommentFetcher` and consumed by `CommentAnalyzer`."""

    model_config = ConfigDict(from_attributes=True)

    comment_id: FBCommentId
    post_id: FBPostId
    parent_id: FBCommentId | None = None
    message: str
    created_time: datetime
    like_count: Annotated[int, Field(ge=0)] = 0
    author_hash: Annotated[
        str | None,
        Field(description="Hashed commenter id, never the raw Facebook user id"),
    ] = None


class AnalysisResult(BaseModel):
    """Contract produced by `CommentAnalyzer` and persisted to comment analyses."""

    comment_id: FBCommentId
    language: Language
    sentiment: Sentiment
    sentiment_score: Score
    intent: Intent
    aspects: list[AspectSentimentDTO] = []
    keywords: list[str] = []
    is_actionable: bool = False
    model_version: str
