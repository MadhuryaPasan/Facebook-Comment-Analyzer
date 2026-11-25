from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas import DateRangeParams
from app.shared.types import FBPostId


class PostFilterParams(DateRangeParams):
    """Query parameters for filtering the posts list (`GET /posts`)."""


class SentimentSummaryDTO(BaseModel):
    """Aggregated sentiment counts for analyzed comments on a post."""

    positive: Annotated[int, Field(ge=0, description="Number of positive comments")] = 0
    neutral: Annotated[int, Field(ge=0, description="Number of neutral comments")] = 0
    negative: Annotated[int, Field(ge=0, description="Number of negative comments")] = 0


class PostResponseDTO(BaseModel):
    """Serialized Facebook post with comment and sentiment counts."""

    model_config = ConfigDict(from_attributes=True)

    post_id: FBPostId
    message: Annotated[str | None, Field(description="Post caption/body text, if any")] = None
    created_time: Annotated[datetime, Field(description="UTC timestamp when the post was published")]
    comment_count: Annotated[int, Field(ge=0, description="Total comments on the post")]
    analyzed_count: Annotated[int, Field(ge=0, description="Comments that already have an analysis")]
    sentiment_summary: SentimentSummaryDTO


class PostListResponseDTO(BaseModel):
    """Response envelope containing a list of Facebook posts."""

    items: Annotated[list[PostResponseDTO], Field(description="Matching Facebook posts")]
