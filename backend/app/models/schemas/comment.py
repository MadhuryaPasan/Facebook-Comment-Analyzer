from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated

from app.models.common.enum import Intent, Language, Sentiment, TaskStatus
from app.models.common.type import FBCommentId, FBPostId, Score
from app.models.schemas.post import DateRangeParams
from datetime import datetime


# ---- Query params ----

class CommentFilterParams(BaseModel):
    """Query params for GET /posts/{post_id}/comments."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    sentiment: Annotated[Sentiment | None, Field(description="Only comments with this sentiment")] = None
    intent: Annotated[Intent | None, Field(description="Only comments with this intent")] = None
    aspect: Annotated[str | None, Field(min_length=1, max_length=50, description="Only comments mentioning this aspect, e.g. delivery")] = None
    analyzed: Annotated[bool | None, Field(description="true = analyzed only, false = not analyzed yet only")] = None

class CommentSearchParams(CommentFilterParams, DateRangeParams):
    """Query params for GET /comments (all posts)."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)
    post_id: Annotated[FBPostId | None, Field(description="Only comments on this post")] = None


# ---- Analysis parts ----

class AspectSentimentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    aspect: Annotated[str, Field(description="Topic the comment talks about, e.g. delivery, price")]
    sentiment: Sentiment
    score: Score

class CommentAnalysisSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sentiment: Sentiment
    sentiment_score: Score
    intent: Intent
    aspects: list[AspectSentimentDTO] = []

class CommentAnalysisDetailDTO(CommentAnalysisSummaryDTO):
    language: Language
    keywords: list[str] = []
    is_actionable: Annotated[bool, Field(description="True if the company can act on this comment")]
    model_version: Annotated[str, Field(description="Analyzer version that produced this result")]
    analyzed_at: datetime


# ---- Responses ----

class CommentResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    comment_id: FBCommentId
    post_id: FBPostId
    parent_id: FBCommentId | None
    message: str
    created_time: datetime
    like_count: Annotated[int, Field(ge=0)]
    analysis: CommentAnalysisSummaryDTO | None = None

class CommentListResponseDTO(BaseModel):
    items: list[CommentResponseDTO]

class ReplyResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    comment_id: FBCommentId
    message: str
    created_time: datetime

class CommentDetailResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    comment_id: FBCommentId
    post_id: FBPostId
    parent_id: FBCommentId | None
    message: str
    created_time: datetime
    like_count: Annotated[int, Field(ge=0)]
    analysis: CommentAnalysisDetailDTO | None = None
    replies: list[ReplyResponseDTO] = []


# ---- POST /comments/analyze ----

class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    post_id: FBPostId

class AnalyzeTaskResponseDTO(BaseModel):
    task_id: Annotated[str, Field(description="Id of the queued analysis task")]
    post_id: FBPostId
    status: TaskStatus
    queued_at: datetime


# ---- Contracts between FacebookCommentFetcher and CommentAnalyzer ----

class RawComment(BaseModel):
    """Returned by FacebookCommentFetcher, taken by CommentAnalyzer."""
    model_config = ConfigDict(from_attributes=True)
    comment_id: FBCommentId
    post_id: FBPostId
    parent_id: FBCommentId | None = None
    message: str
    created_time: datetime
    like_count: Annotated[int, Field(ge=0)] = 0
    author_hash: Annotated[str | None, Field(description="Hashed commenter id, never the raw FB id")] = None

class AnalysisResult(BaseModel):
    """Returned by CommentAnalyzer, saved to comment_analyses."""
    comment_id: FBCommentId
    language: Language
    sentiment: Sentiment
    sentiment_score: Score
    intent: Intent
    aspects: list[AspectSentimentDTO] = []
    keywords: list[str] = []
    is_actionable: bool = False
    model_version: str
