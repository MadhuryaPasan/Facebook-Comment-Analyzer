from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Annotated

from app.models.common.type import FBPostId
from datetime import date, datetime


# ---- Query params ----

class DateRangeParams(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    from_date: Annotated[date | None, Field(alias="from", description="On or after this date (YYYY-MM-DD)")] = None
    to_date: Annotated[date | None, Field(alias="to", description="On or before this date (YYYY-MM-DD)")] = None

    @model_validator(mode="after")
    def _check_range(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("'from' must be on or before 'to'")
        return self

class PostFilterParams(DateRangeParams):
    """Query params for GET /posts."""


# ---- Responses ----

class SentimentSummaryDTO(BaseModel):
    positive: Annotated[int, Field(ge=0, description="Number of positive comments")] = 0
    neutral: Annotated[int, Field(ge=0, description="Number of neutral comments")] = 0
    negative: Annotated[int, Field(ge=0, description="Number of negative comments")] = 0

class PostResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    post_id: FBPostId
    message: str | None
    created_time: datetime
    comment_count: Annotated[int, Field(ge=0, description="Total comments on the post")]
    analyzed_count: Annotated[int, Field(ge=0, description="Comments that already have an analysis")]
    sentiment_summary: SentimentSummaryDTO

class PostListResponseDTO(BaseModel):
    items: list[PostResponseDTO]
