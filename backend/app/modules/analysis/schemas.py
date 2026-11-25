from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import TaskStatus
from app.shared.types import FBPostId


class AnalyzeRequest(BaseModel):
    """Request payload to fetch and analyze comments for a Facebook post."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    post_id: FBPostId


class AnalyzeTaskResponseDTO(BaseModel):
    """Response payload returned when a post comment analysis task is queued."""

    task_id: Annotated[str, Field(description="ID of the queued analysis task")]
    post_id: FBPostId
    status: TaskStatus
    queued_at: Annotated[datetime, Field(description="UTC timestamp when the task was queued")]
