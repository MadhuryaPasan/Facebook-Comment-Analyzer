from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.type import DBSession
from app.models.schemas.comment import CommentDetailResponseDTO, CommentListResponseDTO
from app.services.comment_service import CommentService


router = APIRouter(tags=["comments"])

@router.get('/comments', status_code=status.HTTP_200_OK)
def get_comments(
    db: DBSession,
    post_id: str | None = None,
    sentiment: str | None = None,
    intent: str | None = None,
    aspect: str | None = None,
    analyzed: bool | None = None,
    from_date: Annotated[date | None, Query(alias="from")] = None,
    to_date: Annotated[date | None, Query(alias="to")] = None,
) -> CommentListResponseDTO:
    return CommentService.get_comments(db, post_id, sentiment, intent, aspect, analyzed, from_date, to_date)

@router.get('/comments/{comment_id}', status_code=status.HTTP_200_OK)
def get_comment(comment_id: str, db: DBSession) -> CommentDetailResponseDTO:
    return CommentService.get_comment(comment_id, db)
