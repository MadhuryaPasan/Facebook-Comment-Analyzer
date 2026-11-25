from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import Intent, Language, Sentiment
from app.shared.dtos import AspectSentimentDTO, DateRangeParams
from app.shared.types import FBCommentId, FBPostId, Score

# ---- Query params ----

class CommentFilterParams(BaseModel):
    """Query parameters for filtering comments on a post (`GET /posts/{post_id}/comments`)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    sentiment: Annotated[Sentiment | None, Field(description="Only comments with this sentiment")] = None
    intent: Annotated[Intent | None, Field(description="Only comments with this intent")] = None
    aspect: Annotated[
        str | None,
        Field(min_length=1, max_length=50, description="Only comments mentioning this aspect, e.g. delivery"),
    ] = None
    analyzed: Annotated[
        bool | None,
        Field(description="true = analyzed only, false = not analyzed yet only"),
    ] = None


class CommentSearchParams(CommentFilterParams, DateRangeParams):
    """Query parameters for searching comments across all posts (`GET /comments`)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)
    post_id: Annotated[FBPostId | None, Field(description="Only comments on this post")] = None


# ---- Analysis parts ----


class CommentAnalysisSummaryDTO(BaseModel):
    """Compact NLP analysis summary included in comment list responses."""

    model_config = ConfigDict(from_attributes=True)
    sentiment: Sentiment
    sentiment_score: Score
    intent: Intent
    aspects: list[AspectSentimentDTO] = []


class CommentAnalysisDetailDTO(CommentAnalysisSummaryDTO):
    """Full NLP analysis details included in single-comment responses."""

    language: Language
    keywords: list[str] = []
    is_actionable: Annotated[bool, Field(description="True if the company can act on this comment")]
    model_version: Annotated[str, Field(description="Analyzer version that produced this result")]
    analyzed_at: datetime


# ---- Responses ----

class CommentResponseDTO(BaseModel):
    """Serialized Facebook comment with optional summary analysis."""

    model_config = ConfigDict(from_attributes=True)

    comment_id: FBCommentId
    post_id: FBPostId
    parent_id: FBCommentId | None
    message: str
    created_time: datetime
    like_count: Annotated[int, Field(ge=0)]
    analysis: CommentAnalysisSummaryDTO | None = None


class CommentListResponseDTO(BaseModel):
    """Response envelope containing a list of Facebook comments."""

    items: Annotated[list[CommentResponseDTO], Field(description="Matching Facebook comments")]


class ReplyResponseDTO(BaseModel):
    """Lightweight representation of a reply nested under a parent comment."""

    model_config = ConfigDict(from_attributes=True)

    comment_id: FBCommentId
    message: str
    created_time: datetime


class CommentDetailResponseDTO(BaseModel):
    """Detailed single-comment response including full analysis and replies."""

    model_config = ConfigDict(from_attributes=True)

    comment_id: FBCommentId
    post_id: FBPostId
    parent_id: FBCommentId | None
    message: str
    created_time: datetime
    like_count: Annotated[int, Field(ge=0)]
    analysis: CommentAnalysisDetailDTO | None = None
    replies: list[ReplyResponseDTO] = []
