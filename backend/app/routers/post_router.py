from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.type import DBSession
from app.models.schemas.comment import CommentListResponseDTO
from app.models.schemas.post import PostListResponseDTO, PostResponseDTO
from app.services.comment_service import CommentService
from app.services.post_service import PostService


router = APIRouter(tags=["posts"])

@router.get('/posts', status_code=status.HTTP_200_OK)
def get_posts(
    db: DBSession,
    from_date: Annotated[date | None, Query(alias="from")] = None,
    to_date: Annotated[date | None, Query(alias="to")] = None,
) -> PostListResponseDTO:
    return PostService.get_posts(db, from_date, to_date)

@router.get('/posts/{post_id}', status_code=status.HTTP_200_OK)
def get_post(post_id: str, db: DBSession) -> PostResponseDTO:
    return PostService.get_post(post_id, db)

@router.get('/posts/{post_id}/comments', status_code=status.HTTP_200_OK)
def get_post_comments(
    post_id: str,
    db: DBSession,
    sentiment: str | None = None,
    intent: str | None = None,
    aspect: str | None = None,
    analyzed: bool | None = None,
) -> CommentListResponseDTO:
    return CommentService.get_post_comments(post_id, db, sentiment, intent, aspect, analyzed)
