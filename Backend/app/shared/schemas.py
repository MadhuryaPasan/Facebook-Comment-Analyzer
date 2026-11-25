from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.shared.enums import Sentiment
from app.shared.types import Score


class DateRangeParams(BaseModel):
    """Reusable inclusive date-range query parameters."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_date: Annotated[
        date | None,
        Field(alias="from", description="On or after this date (YYYY-MM-DD)"),
    ] = None
    to_date: Annotated[
        date | None,
        Field(alias="to", description="On or before this date (YYYY-MM-DD)"),
    ] = None

    @model_validator(mode="after")
    def _check_range(self) -> "DateRangeParams":
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("'from' must be on or before 'to'")
        return self


class AspectSentimentDTO(BaseModel):
    """Sentiment detected for a specific topic or aspect inside a comment."""

    model_config = ConfigDict(from_attributes=True)

    aspect: Annotated[str, Field(description="Topic the comment talks about, e.g. delivery, price")]
    sentiment: Sentiment
    score: Score


class ErrorDetailDTO(BaseModel):
    """Machine-readable error code and human-readable message."""

    code: Annotated[str, Field(description="Stable application error code, e.g. POST_NOT_FOUND")]
    message: Annotated[str, Field(description="Human-readable explanation of the error")]


class ErrorResponseDTO(BaseModel):
    """Standard API error envelope returned for AppException responses."""

    error: ErrorDetailDTO
